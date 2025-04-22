"""
FastAPI server for GraphRAG MCP.
"""

from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from .config import config
from .graphrag import GraphRAGService
from .utils import cache, logger, rate_limiter, timed_execution


# Initialize FastAPI app
app = FastAPI(
    title="GraphRAG MCP Server",
    description="Graph-based Retrieval Augmented Generation Microservice",
    version="1.0.0"
)

# Initialize GraphRAG service
graphrag_service = GraphRAGService()


# ----- API Models -----

class ServerInfo(BaseModel):
    """Server information."""
    name: str = "GraphRAG MCP Server"
    version: str = "1.0.0"
    status: str = "running"
    graphrag_version: str = "1.0.0"
    tools: List[str] = [
        "graphrag_index_source",
        "graphrag_extract_entities",
        "graphrag_query",
        "graphrag_relationship_query",
        "graphrag_entity_lookup",
        "graphrag_semantic_search",
        "graphrag_concept_map",
        "graphrag_schema"
    ]


class ApiResponse(BaseModel):
    """Base API response."""
    success: bool
    error: Optional[str] = None


class EntityModel(BaseModel):
    """Entity model."""
    entity_id: str
    entity_type: str
    name: str
    aliases: Optional[List[str]] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EntityMentionModel(BaseModel):
    """Entity mention model."""
    start: int
    end: int
    text: str


class RelationshipModel(BaseModel):
    """Relationship model."""
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


class SourceIndexRequest(BaseModel):
    """Source indexing request."""
    source: Dict[str, Any]


class SourceIndexResponse(ApiResponse):
    """Source indexing response."""
    doc_id: Optional[str] = None
    entities_extracted: Optional[int] = None
    relationships_extracted: Optional[int] = None


class EntityExtractionRequest(BaseModel):
    """Entity extraction request."""
    text: str
    options: Optional[Dict[str, Any]] = None
    use_enhanced_linking: Optional[bool] = None
    use_contextual_disambiguation: Optional[bool] = None
    use_external_kb: Optional[bool] = None


class EntityExtractionResponse(ApiResponse):
    """Entity extraction response."""
    entities: List[EntityModel] = []
    relationships: List[RelationshipModel] = []
    sources: List[str] = []  # Sources used for entity linking
    disambiguation_applied: bool = False


class QueryRequest(BaseModel):
    """Query request."""
    query: str
    focus_entities: Optional[List[str]] = None
    options: Optional[Dict[str, Any]] = None


class QueryResponse(ApiResponse):
    """Query response."""
    sources: List[Dict[str, Any]] = []
    attributed_prompt: Optional[str] = None


class EntityLookupRequest(BaseModel):
    """Entity lookup request."""
    entity_id: str


class EntityLookupResponse(ApiResponse):
    """Entity lookup response."""
    entity: Optional[EntityModel] = None


class ConceptMapRequest(BaseModel):
    """Concept map request."""
    focus_entities: List[str]
    traversal_depth: Optional[int] = 2
    include_relationships: Optional[bool] = True


class ConceptMapResponse(ApiResponse):
    """Concept map response."""
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []


# ----- API Routes -----

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "GraphRAG MCP Server is running. See /api/info for more details."}


@app.get("/api/info", response_model=ServerInfo)
async def get_info():
    """Get server information."""
    return ServerInfo()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Only rate limit the API routes
    if request.url.path.startswith("/api/tools/"):
        if not rate_limiter.allow_request():
            logger.warning(f"Rate limit exceeded for {request.client.host}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return response


@app.post("/api/tools/graphrag_index_source", response_model=SourceIndexResponse)
@timed_execution
async def index_source(request: SourceIndexRequest):
    """
    Index a source in GraphRAG.
    
    This endpoint adds a source document to the GraphRAG knowledge graph
    and extracts entities and relationships.
    """
    try:
        doc_id = graphrag_service.index_source(request.source)
        doc = graphrag_service.vector_db.get_document(doc_id)
        
        return SourceIndexResponse(
            success=True,
            doc_id=doc_id,
            entities_extracted=len(doc.entities) if doc else 0,
            relationships_extracted=len(doc.relationships) if doc else 0
        )
    except Exception as e:
        logger.error(f"Error indexing source: {e}")
        return SourceIndexResponse(success=False, error=str(e))


@app.post("/api/tools/graphrag_extract_entities", response_model=EntityExtractionResponse)
@timed_execution
async def extract_entities(request: EntityExtractionRequest):
    """
    Extract entities from text.
    
    This endpoint extracts named entities from text using named entity recognition
    and returns them with confidence scores.
    
    Options:
    - use_enhanced_linking: Use the enhanced entity linking (defaults to config setting)
    - use_contextual_disambiguation: Apply contextual disambiguation (defaults to config setting) 
    - use_external_kb: Use external knowledge bases like Wikidata (defaults to config setting)
    """
    try:
        # Set temporary config overrides if provided in the request
        original_enhanced_linking = config.ENABLE_ENHANCED_ENTITY_LINKING
        original_contextual_disambiguation = config.CONTEXTUAL_DISAMBIGUATION
        original_use_wikidata = config.USE_WIKIDATA_KB
        
        if request.use_enhanced_linking is not None:
            config.ENABLE_ENHANCED_ENTITY_LINKING = request.use_enhanced_linking
        
        if request.use_contextual_disambiguation is not None:
            config.CONTEXTUAL_DISAMBIGUATION = request.use_contextual_disambiguation
        
        if request.use_external_kb is not None:
            config.USE_WIKIDATA_KB = request.use_external_kb
        
        try:
            # Generate cache key based on text and current settings
            settings_hash = hash((
                config.ENABLE_ENHANCED_ENTITY_LINKING,
                config.CONTEXTUAL_DISAMBIGUATION,
                config.USE_WIKIDATA_KB
            ))
            cache_key = f"extract_entities:{hash(request.text)}:{settings_hash}"
            
            # Check cache first
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Extract entities
            entities = graphrag_service.extract_entities_from_text(request.text)
            
            # Extract relationships if using enhanced linking
            relationships = []
            if config.ENABLE_ENHANCED_ENTITY_LINKING and len(entities) >= 2:
                from .entity_linking import get_entity_linker
                entity_linker = get_entity_linker()
                relationship_objects = entity_linker._create_relationships(entities, request.text)
                
                # Convert to relationship models
                relationships = [RelationshipModel(
                    relationship_id=rel.relationship_id,
                    source_entity_id=rel.source_entity_id,
                    target_entity_id=rel.target_entity_id,
                    relation_type=rel.relation_type.value,
                    confidence=rel.confidence,
                    metadata=rel.metadata
                ) for rel in relationship_objects]
            
            # Format response
            entity_models = [EntityModel(
                entity_id=entity.entity_id,
                entity_type=entity.entity_type.value,
                name=entity.name,
                aliases=entity.aliases,
                description=entity.description,
                metadata=entity.metadata
            ) for entity in entities]
            
            # Determine sources used
            sources = []
            if config.ENABLE_ENHANCED_ENTITY_LINKING:
                sources.append("enhanced_entity_linking")
                
                if config.CONTEXTUAL_DISAMBIGUATION:
                    sources.append("contextual_disambiguation")
                    
                if config.USE_WIKIDATA_KB:
                    sources.append("wikidata_kb")
                
                sources.append("local_kb")
            
            # Cache and return result
            result = EntityExtractionResponse(
                success=True,
                entities=entity_models,
                relationships=relationships,
                sources=sources,
                disambiguation_applied=config.CONTEXTUAL_DISAMBIGUATION
            )
            cache.set(cache_key, result)
            return result
            
        finally:
            # Restore original config settings
            config.ENABLE_ENHANCED_ENTITY_LINKING = original_enhanced_linking
            config.CONTEXTUAL_DISAMBIGUATION = original_contextual_disambiguation
            config.USE_WIKIDATA_KB = original_use_wikidata
            
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        return EntityExtractionResponse(success=False, error=str(e))


@app.post("/api/tools/graphrag_query", response_model=QueryResponse)
@timed_execution
async def query(request: QueryRequest):
    """
    Retrieve relevant sources for a natural language query.
    
    This endpoint searches the knowledge graph for sources relevant to the
    query and returns them with relevance scores.
    """
    try:
        # Check cache first
        cache_key = f"query:{request.query}:{','.join(request.focus_entities or [])}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Get sources
        sources, attributed_prompt = graphrag_service.get_sources_for_query(
            request.query,
            request.focus_entities,
            request.options
        )
        
        # Cache and return result
        result = QueryResponse(
            success=True,
            sources=sources,
            attributed_prompt=attributed_prompt
        )
        cache.set(cache_key, result)
        return result
    except Exception as e:
        logger.error(f"Error querying: {e}")
        return QueryResponse(success=False, error=str(e))


@app.post("/api/tools/graphrag_entity_lookup", response_model=EntityLookupResponse)
async def entity_lookup(request: EntityLookupRequest):
    """
    Look up entity information by ID.
    
    This endpoint retrieves detailed information about an entity in the
    knowledge graph.
    """
    try:
        entity_data = graphrag_service.get_entity(request.entity_id)
        if not entity_data:
            return EntityLookupResponse(
                success=False,
                error=f"Entity with ID {request.entity_id} not found"
            )
        
        return EntityLookupResponse(
            success=True,
            entity=EntityModel(**entity_data)
        )
    except Exception as e:
        logger.error(f"Error looking up entity: {e}")
        return EntityLookupResponse(success=False, error=str(e))


@app.post("/api/tools/graphrag_concept_map", response_model=ConceptMapResponse)
@timed_execution
async def concept_map(request: ConceptMapRequest):
    """
    Generate a concept map for visualization.
    
    This endpoint creates a graph visualization of entities and their relationships
    in the knowledge graph, centered around specified focus entities.
    """
    try:
        if not request.focus_entities:
            return ConceptMapResponse(
                success=False,
                error="At least one focus entity is required"
            )
        
        # Generate concept map
        result = graphrag_service.generate_concept_map(
            request.focus_entities,
            request.traversal_depth or 2
        )
        
        return ConceptMapResponse(
            success=True,
            nodes=result["nodes"],
            edges=result["edges"] if request.include_relationships else []
        )
    except Exception as e:
        logger.error(f"Error generating concept map: {e}")
        return ConceptMapResponse(success=False, error=str(e))


@app.post("/api/process_attributed_response")
@timed_execution
async def process_attributed_response(request: Dict[str, Any]):
    """
    Process a response with attribution markers.
    
    This endpoint takes a response with attribution markers and the sources used,
    and returns attribution information with confidence scores.
    """
    try:
        if "response" not in request or "sources" not in request:
            raise ValueError("Both 'response' and 'sources' are required")
        
        # Process response
        result = graphrag_service.process_attributed_response(
            request["response"],
            request["sources"]
        )
        
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"Error processing attributed response: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/tools/graphrag_schema")
async def schema(request: Dict[str, Any]):
    """
    Get or update the GraphRAG knowledge graph schema.
    
    This endpoint retrieves or modifies the schema for the knowledge graph,
    including entity types, relationship types, and property definitions.
    """
    # This is a placeholder for future implementation
    schema_data = {
        "entity_types": [
            {"id": "person", "name": "Person", "description": "Human individual"},
            {"id": "organization", "name": "Organization", "description": "Group of people"},
            {"id": "location", "name": "Location", "description": "Physical place"},
            {"id": "concept", "name": "Concept", "description": "Abstract idea or notion"},
            {"id": "product", "name": "Product", "description": "Good or service"},
            {"id": "event", "name": "Event", "description": "Something that happens"},
            {"id": "date", "name": "Date", "description": "Point in time"},
            {"id": "fact", "name": "Fact", "description": "Verified information"},
            {"id": "claim", "name": "Claim", "description": "Assertion or statement"},
        ],
        "relationship_types": [
            {"id": "is_a", "name": "Is A", "description": "Type relationship"},
            {"id": "part_of", "name": "Part Of", "description": "Composition relationship"},
            {"id": "located_in", "name": "Located In", "description": "Spatial relationship"},
            {"id": "created_by", "name": "Created By", "description": "Creation relationship"},
            {"id": "works_for", "name": "Works For", "description": "Employment relationship"},
            {"id": "has_property", "name": "Has Property", "description": "Attribute relationship"},
            {"id": "related_to", "name": "Related To", "description": "General relationship"},
            {"id": "contradicts", "name": "Contradicts", "description": "Contradiction relationship"},
            {"id": "supports", "name": "Supports", "description": "Supporting relationship"},
        ]
    }
    
    return {"success": True, "schema": schema_data}