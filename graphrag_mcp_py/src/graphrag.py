"""
GraphRAG service implementation.
"""

import re
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from .config import config
from .utils import logger, timed_execution
from .vector_db import VectorDocument, get_vector_db


class EntityType(str, Enum):
    """Entity types for GraphRAG."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    CONCEPT = "concept"
    PRODUCT = "product"
    EVENT = "event"
    DATE = "date"
    FACT = "fact"
    CLAIM = "claim"
    OTHER = "other"


class RelationType(str, Enum):
    """Relationship types for GraphRAG."""
    IS_A = "is_a"
    PART_OF = "part_of"
    LOCATED_IN = "located_in"
    CREATED_BY = "created_by"
    WORKS_FOR = "works_for"
    HAS_PROPERTY = "has_property"
    RELATED_TO = "related_to"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    OTHER = "other"


class SourceType(str, Enum):
    """Source types for GraphRAG."""
    WEB = "web"
    DOCUMENT = "document"
    DATABASE = "database"
    API = "api"
    KNOWLEDGE_BASE = "knowledge_base"
    CALCULATION = "calculation"
    USER_PROVIDED = "user_provided"
    OTHER = "other"


class Entity:
    """Entity representation in GraphRAG."""
    
    def __init__(
        self,
        name: str,
        entity_type: Union[EntityType, str],
        entity_id: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.entity_id = entity_id or f"ent_{uuid.uuid4().hex[:8]}"
        self.name = name
        
        # Convert string to EntityType enum if needed
        if isinstance(entity_type, str):
            try:
                self.entity_type = EntityType(entity_type)
            except ValueError:
                self.entity_type = EntityType.OTHER
        else:
            self.entity_type = entity_type
            
        self.aliases = aliases or []
        self.description = description
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "name": self.name,
            "aliases": self.aliases,
            "description": self.description,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create from dictionary."""
        return cls(
            entity_id=data["entity_id"],
            name=data["name"],
            entity_type=data["entity_type"],
            aliases=data.get("aliases", []),
            description=data.get("description"),
            metadata=data.get("metadata", {})
        )


class Relationship:
    """Relationship between entities in GraphRAG."""
    
    def __init__(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relation_type: Union[RelationType, str],
        relationship_id: Optional[str] = None,
        confidence: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.relationship_id = relationship_id or f"rel_{uuid.uuid4().hex[:8]}"
        self.source_entity_id = source_entity_id
        self.target_entity_id = target_entity_id
        
        # Convert string to RelationType enum if needed
        if isinstance(relation_type, str):
            try:
                self.relation_type = RelationType(relation_type)
            except ValueError:
                self.relation_type = RelationType.OTHER
        else:
            self.relation_type = relation_type
            
        self.confidence = confidence
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "relationship_id": self.relationship_id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "relation_type": self.relation_type.value,
            "confidence": self.confidence,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create from dictionary."""
        return cls(
            relationship_id=data["relationship_id"],
            source_entity_id=data["source_entity_id"],
            target_entity_id=data["target_entity_id"],
            relation_type=data["relation_type"],
            confidence=data.get("confidence", 0.7),
            metadata=data.get("metadata", {})
        )


class Source:
    """Source representation in GraphRAG."""
    
    def __init__(
        self,
        title: str,
        content: str,
        source_type: Union[SourceType, str],
        source_id: Optional[str] = None,
        url: Optional[str] = None,
        authors: Optional[List[str]] = None,
        publication_date: Optional[str] = None,
        retrieval_date: Optional[str] = None,
        confidence_score: float = 0.8,
        reliability_score: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None
    ):
        from datetime import datetime
        
        self.source_id = source_id or f"src_{uuid.uuid4().hex[:8]}"
        self.title = title
        self.content = content
        
        # Convert string to SourceType enum if needed
        if isinstance(source_type, str):
            try:
                self.source_type = SourceType(source_type)
            except ValueError:
                self.source_type = SourceType.OTHER
        else:
            self.source_type = source_type
            
        self.url = url
        self.authors = authors or []
        self.publication_date = publication_date
        self.retrieval_date = retrieval_date or datetime.now().isoformat()
        self.confidence_score = confidence_score
        self.reliability_score = reliability_score
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_id": self.source_id,
            "title": self.title,
            "content": self.content,
            "source_type": self.source_type.value,
            "url": self.url,
            "authors": self.authors,
            "publication_date": self.publication_date,
            "retrieval_date": self.retrieval_date,
            "confidence_score": self.confidence_score,
            "reliability_score": self.reliability_score,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Source':
        """Create from dictionary."""
        return cls(
            source_id=data["source_id"],
            title=data["title"],
            content=data["content"],
            source_type=data["source_type"],
            url=data.get("url"),
            authors=data.get("authors", []),
            publication_date=data.get("publication_date"),
            retrieval_date=data.get("retrieval_date"),
            confidence_score=data.get("confidence_score", 0.8),
            reliability_score=data.get("reliability_score", 0.7),
            metadata=data.get("metadata", {})
        )


class GraphRAGService:
    """
    GraphRAG service implementation using FAISS vector database.
    
    This service provides graph-based retrieval augmented generation capabilities,
    including entity extraction, source indexing, and knowledge graph operations.
    """
    
    def __init__(self):
        """Initialize the GraphRAG service."""
        # Initialize vector database
        self.vector_db = get_vector_db()
        
        # Entity and relationship stores
        self.entity_store: Dict[str, Entity] = {}
        self.relationship_store: Dict[str, Relationship] = {}
        
        logger.info("Initialized GraphRAG service")
    
    @timed_execution
    def index_source(self, source: Union[Source, Dict[str, Any]]) -> str:
        """
        Index a source in GraphRAG.
        
        Args:
            source: Source to index
            
        Returns:
            Document ID in the index
        """
        # Convert dict to Source if needed
        if isinstance(source, dict):
            source = Source.from_dict(source)
        
        logger.info(f"Indexing source: {source.source_id} - {source.title}")
        
        # Create vector document
        doc = VectorDocument(
            content=source.content,
            metadata={
                "source_id": source.source_id,
                "source_type": source.source_type.value,
                "title": source.title,
                "url": source.url,
                "confidence_score": source.confidence_score,
                "reliability_score": source.reliability_score,
                "retrieval_date": source.retrieval_date,
            }
        )
        
        # Extract and store entities
        entities = self.extract_entities_from_text(source.content)
        
        # Add entities to document
        for entity in entities:
            # Store entity
            self.entity_store[entity.entity_id] = entity
            
            # Find mentions in text
            entity_name = entity.name.lower()
            content = source.content.lower()
            positions = []
            
            # Find all occurrences
            start = 0
            while True:
                pos = content.find(entity_name, start)
                if pos == -1:
                    break
                
                positions.append((pos, pos + len(entity_name)))
                start = pos + 1
            
            if positions:
                doc.add_entity(entity.entity_id, entity.entity_type.value, positions)
        
        # Create relationships between entities
        self._create_entity_relationships(entities, doc)
        
        # Index the document
        doc_id = self.vector_db.add_document(doc)
        logger.info(f"Indexed source {source.source_id} as document {doc_id}")
        
        return doc_id
    
    def _create_entity_relationships(self, entities: List[Entity], doc: VectorDocument) -> None:
        """Create relationships between entities."""
        if len(entities) <= 1:
            return
            
        # Use enhanced entity linking for relationship creation if enabled
        if config.ENABLE_ENHANCED_ENTITY_LINKING:
            from .entity_linking import get_entity_linker
            entity_linker = get_entity_linker()
            content = doc.content
            
            # Create relationships using the entity linker
            relationships = entity_linker._create_relationships(entities, content)
            
            # Limit the number of relationships to avoid overwhelming the graph
            max_relationships = min(config.MAX_ENTITY_RELATIONSHIPS, len(relationships))
            selected_relationships = relationships[:max_relationships]
            
            # Add relationships to the document and store
            for relationship in selected_relationships:
                # Store the relationship
                self.relationship_store[relationship.relationship_id] = relationship
                
                # Add to document
                doc.add_relationship(
                    relationship.source_entity_id,
                    relationship.target_entity_id,
                    relationship.relation_type.value
                )
                
            logger.info(f"Created {len(selected_relationships)} entity relationships using enhanced entity linking")
        else:
            # Fall back to basic sequential relationship creation
            for i in range(len(entities) - 1):
                relationship = Relationship(
                    source_entity_id=entities[i].entity_id,
                    target_entity_id=entities[i + 1].entity_id,
                    relation_type=RelationType.RELATED_TO,
                    confidence=0.7
                )
                
                self.relationship_store[relationship.relationship_id] = relationship
                
                doc.add_relationship(
                    relationship.source_entity_id,
                    relationship.target_entity_id,
                    relationship.relation_type.value
                )
    
    @timed_execution
    def get_sources_for_query(
        self, 
        query: str, 
        focus_entities: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Dict[str, Any]], str]:
        """
        Get sources for a query.
        
        Args:
            query: Query text
            focus_entities: Optional list of entity IDs to focus on
            options: Optional query options
            
        Returns:
            Tuple of (sources, attributed_prompt)
        """
        options = options or {}
        logger.info(f"Retrieving sources for query: {query}")
        
        # Configure retrieval options
        max_results = options.get("max_results", config.MAX_RESULTS)
        min_confidence = options.get("min_confidence", config.MIN_CONFIDENCE)
        
        # Search results
        results: List[Tuple[str, float]] = []
        
        # Use different search strategies based on context
        if focus_entities and focus_entities:
            logger.info(f"Using entity-centric retrieval with entities: {focus_entities}")
            results = self.vector_db.search_by_entity(focus_entities, limit=max_results)
        else:
            logger.info("Using query-based retrieval")
            results = self.vector_db.search(query, limit=max_results, min_score=min_confidence)
        
        # Process search results
        sources = []
        for doc_id, score in results:
            doc = self.vector_db.get_document(doc_id)
            if not doc:
                continue
                
            # Get entity information
            doc_entities = []
            for entity_data in doc.entities:
                entity_id = entity_data["entity_id"]
                entity = self.entity_store.get(entity_id)
                if entity:
                    doc_entities.append(entity_id)
            
            sources.append({
                "content": doc.content,
                "metadata": doc.metadata,
                "relevance_score": score,
                "explanation": self._generate_explanation(query, doc, score),
                "entities": doc_entities
            })
        
        # Generate attributed prompt
        attributed_prompt = self.build_attributed_prompt(query, sources)
        
        logger.info(f"Retrieved {len(sources)} sources for query")
        return sources, attributed_prompt
    
    def _generate_explanation(self, query: str, doc: VectorDocument, score: float) -> str:
        """Generate an explanation for why this document was retrieved."""
        # Simple explanation based on relevance score
        if score > 0.9:
            return "Very high relevance to query"
        elif score > 0.8:
            return "High relevance to query"
        elif score > 0.7:
            # Try to extract query terms that match
            query_terms = set(query.lower().split())
            doc_terms = set(doc.content.lower().split())
            matching_terms = query_terms.intersection(doc_terms)
            
            if matching_terms:
                return f"Document contains query terms: {', '.join(matching_terms)}"
            return "Good relevance to query"
        elif score > 0.6:
            return "Moderate relevance to query"
        else:
            return "Some relevance to query"
    
    @timed_execution
    def extract_entities_from_text(self, text: str) -> List[Entity]:
        """
        Extract entities from text.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            List of extracted entities
        """
        try:
            # Use enhanced entity linking if enabled, otherwise fall back to basic approach
            if config.ENABLE_ENHANCED_ENTITY_LINKING:
                from .entity_linking import get_entity_linker
                entity_linker = get_entity_linker()
                entities = entity_linker.extract_entities(text)
                
                # Perform contextual disambiguation if enabled
                if config.CONTEXTUAL_DISAMBIGUATION and entities:
                    entities = entity_linker.disambiguate_entities(entities, text)
                
                logger.info(f"Extracted {len(entities)} entities from text using enhanced entity linking")
                return entities
            
            # Fall back to basic entity extraction if enhanced linking is disabled
            entities: List[Entity] = []
            
            # Simple keyword-based entity extraction
            keyword_map: Dict[str, EntityType] = {
                'climate change': EntityType.CONCEPT,
                'global warming': EntityType.CONCEPT,
                'artificial intelligence': EntityType.CONCEPT,
                'united states': EntityType.LOCATION,
                'european union': EntityType.ORGANIZATION,
                'covid-19': EntityType.CONCEPT,
                'paris agreement': EntityType.CONCEPT,
            }
            
            # Check for known entities
            text_lower = text.lower()
            for keyword, entity_type in keyword_map.items():
                if keyword in text_lower:
                    entity_name = ' '.join(word.capitalize() for word in keyword.split())
                    entities.append(Entity(
                        name=entity_name,
                        entity_type=entity_type,
                        description="Entity extracted from text based on keyword match"
                    ))
            
            # Extract potential entities based on capitalization patterns
            capitals_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
            capitalized_phrases = re.findall(capitals_pattern, text)
            
            for phrase in capitalized_phrases:
                # Skip if already added as a known entity
                if any(e.name.lower() == phrase.lower() for e in entities):
                    continue
                
                # Determine entity type based on content
                entity_type = EntityType.OTHER
                if re.match(r'^\d{1,2}/\d{1,2}/\d{2,4}$', phrase):
                    entity_type = EntityType.DATE
                elif 2 < len(phrase) < 15:
                    entity_type = EntityType.CONCEPT
                
                entities.append(Entity(
                    name=phrase,
                    entity_type=entity_type,
                    description="Entity extracted from text based on capitalization pattern"
                ))
            
            # If no entities found, add at least one general concept
            if not entities:
                # Extract most frequent non-stop word as a concept
                words = text.lower().split()
                word_freq: Dict[str, int] = {}
                
                for word in words:
                    if len(word) > 4:  # Skip short words
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                if word_freq:
                    top_word = max(word_freq.items(), key=lambda x: x[1])[0]
                    entities.append(Entity(
                        name=top_word.capitalize(),
                        entity_type=EntityType.CONCEPT,
                        description="Main concept extracted from text"
                    ))
            
            logger.info(f"Extracted {len(entities)} entities from text")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    def build_attributed_prompt(self, query: str, sources: List[Dict[str, Any]]) -> str:
        """
        Build a prompt with attribution markers.
        
        Args:
            query: Query text
            sources: Sources to include in the prompt
            
        Returns:
            Prompt with attribution markers
        """
        prompt_parts = [
            'Answer the question based on these sources:\n\n'
        ]
        
        # Add each source with clear attribution markers
        for i, source in enumerate(sources):
            source_id = f"SOURCE_{i + 1}"
            metadata = source["metadata"]
            
            prompt_parts.append(
                f"[{source_id}: {metadata.get('title', 'Unknown')} " +
                f"({metadata.get('source_type', 'unknown')}, " +
                f"confidence: {metadata.get('confidence_score', 0.7):.2f})]\n"
            )
            prompt_parts.append(source["content"] + '\n')
            prompt_parts.append(f"[END {source_id}]\n\n")
        
        # Add instructions for attribution in the response
        prompt_parts.append(
            '\nQuestion: ' + query + '\n\n' +
            'Answer the question based on the sources provided. ' +
            'For each piece of information in your answer, indicate which ' +
            'source(s) it came from using source numbers [SOURCE_X].'
        )
        
        return ''.join(prompt_parts)
    
    @timed_execution
    def process_attributed_response(
        self,
        response: str,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a response with attribution markers.
        
        Args:
            response: Response text with attribution markers
            sources: Sources used in the response
            
        Returns:
            Attribution result
        """
        # Extract attribution counts
        source_refs = re.findall(r'\[SOURCE_(\d+)\]', response) or []
        attribution_counts: Dict[int, int] = {}
        
        for ref in source_refs:
            source_num = int(ref)
            attribution_counts[source_num] = attribution_counts.get(source_num, 0) + 1
        
        # Map sources
        attributed_sources = []
        for source_num, count in attribution_counts.items():
            if 1 <= source_num <= len(sources):
                source_idx = source_num - 1  # Convert from 1-indexed to 0-indexed
                source = sources[source_idx]
                attributed_sources.append({
                    "source_id": source["metadata"].get("source_id", f"unknown_{source_idx}"),
                    "title": source["metadata"].get("title", "Unknown Source"),
                    "reference_count": count,
                    "relevance_score": source.get("relevance_score", 0.0),
                    "metadata": source["metadata"]
                })
        
        # Calculate overall confidence based on source confidence and relevance
        confidence = 0.75  # Reasonable default
        if attributed_sources:
            total_weight = 0
            weighted_sum = 0
            
            for source in attributed_sources:
                ref_count = source["reference_count"]
                relevance = source.get("relevance_score", 0.8)
                conf = source["metadata"].get("confidence_score", 0.75)
                
                # Weight = reference count * relevance
                weight = ref_count * relevance
                weighted_sum += weight * conf
                total_weight += weight
            
            if total_weight > 0:
                confidence = weighted_sum / total_weight
            
            # Ensure minimum confidence
            confidence = max(confidence, 0.75)
        
        return {
            "text": response,
            "sources": attributed_sources,
            "confidence": confidence,
            "explanation": "Attribution based on source references in the response"
        }
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity data or None if not found
        """
        entity = self.entity_store.get(entity_id)
        return entity.to_dict() if entity else None
    
    def get_relationship(self, relationship_id: str) -> Optional[Dict[str, Any]]:
        """
        Get relationship by ID.
        
        Args:
            relationship_id: Relationship ID
            
        Returns:
            Relationship data or None if not found
        """
        relationship = self.relationship_store.get(relationship_id)
        return relationship.to_dict() if relationship else None
    
    @timed_execution
    def generate_concept_map(
        self, 
        focus_entities: List[str], 
        traversal_depth: int = 2
    ) -> Dict[str, Any]:
        """
        Generate a concept map for visualization.
        
        Args:
            focus_entities: Entity IDs to focus on
            traversal_depth: Maximum traversal depth
            
        Returns:
            Concept map with nodes and edges
        """
        nodes = []
        edges = []
        
        # Process each focus entity
        processed_entities = set()
        entities_to_process = list(focus_entities)
        
        # Process entities up to the specified traversal depth
        for depth in range(traversal_depth + 1):
            if not entities_to_process:
                break
            
            current_batch = entities_to_process.copy()
            entities_to_process = []
            
            for entity_id in current_batch:
                if entity_id in processed_entities:
                    continue
                processed_entities.add(entity_id)
                
                # Add entity to nodes
                entity = self.entity_store.get(entity_id)
                if entity:
                    nodes.append({
                        "id": entity.entity_id,
                        "label": entity.name,
                        "type": entity.entity_type.value,
                        "properties": {
                            "description": entity.description or "",
                            "aliases": entity.aliases,
                            **entity.metadata
                        }
                    })
                    
                    # Find relationships where this entity is source or target
                    for rel in self.relationship_store.values():
                        if rel.source_entity_id == entity_id or rel.target_entity_id == entity_id:
                            # Add the relationship
                            edges.append({
                                "id": rel.relationship_id,
                                "source": rel.source_entity_id,
                                "target": rel.target_entity_id,
                                "label": rel.relation_type.value,
                                "properties": {
                                    "confidence": rel.confidence,
                                    **rel.metadata
                                }
                            })
                            
                            # Add the other entity to be processed in the next depth
                            other_entity_id = rel.target_entity_id if rel.source_entity_id == entity_id else rel.source_entity_id
                            if other_entity_id not in processed_entities and depth < traversal_depth:
                                entities_to_process.append(other_entity_id)
        
        return {"nodes": nodes, "edges": edges}