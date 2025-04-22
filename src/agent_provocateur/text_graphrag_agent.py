"""
Enhanced Text Document Agent with GraphRAG integration.

This agent provides GraphRAG capabilities for text and markdown documents including
source attribution, entity extraction, and relationship detection using the
GraphRAG MCP server and enhanced entity linking.
"""

import logging
import asyncio
import os
import re
from typing import Dict, List, Any, Optional, Tuple, Set
import uuid
import datetime

from agent_provocateur.agent_base import BaseAgent
from agent_provocateur.a2a_models import TaskRequest, TaskResult
from agent_provocateur.models import Document, DocumentContent, Source, SourceType
from agent_provocateur.graphrag_client import GraphRAGClient
from agent_provocateur.entity_linking import get_entity_linker, Entity, EntityType, RelationType

logger = logging.getLogger(__name__)

class TextGraphRAGAgent(BaseAgent):
    """Enhanced Text Document Agent with GraphRAG integration and advanced entity linking."""
    
    async def on_startup(self) -> None:
        """Initialize the Text GraphRAG agent with enhanced entity linking."""
        self.logger.info("Starting Text GraphRAG agent...")
        
        # Initialize GraphRAG client
        graphrag_url = os.environ.get("GRAPHRAG_MCP_URL", "http://localhost:8083")
        self.graphrag_client = GraphRAGClient(base_url=graphrag_url)
        
        # Initialize enhanced entity linker
        self.entity_linker = get_entity_linker(self.graphrag_client)
        
        # Track extracted entities and relationships
        self.extracted_entities: Dict[str, Entity] = {}
        self.entity_clusters: List[Dict[str, Any]] = []
        
        # Document processing configuration
        self.chunk_size = 1000
        self.chunk_overlap = 200
        
        self.logger.info(f"Initialized Text GraphRAG agent with server: {graphrag_url}")
    
    async def handle_index_text_document(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Index a text or markdown document in GraphRAG.
        
        Args:
            task_request: Task request with document content
            
        Returns:
            Dict with indexing results
        """
        content = task_request.payload.get("content")
        title = task_request.payload.get("title")
        doc_type = task_request.payload.get("doc_type", "markdown")
        metadata = task_request.payload.get("metadata", {})
        
        if not content:
            raise ValueError("Missing required parameter: content")
        
        if not title:
            title = f"Document {uuid.uuid4().hex[:8]}"
        
        # Validate document type
        if doc_type not in ["markdown", "text"]:
            raise ValueError(f"Unsupported document type: {doc_type}. Must be 'markdown' or 'text'")
        
        try:
            # Index the document using GraphRAG
            doc_id = await self.graphrag_client.index_text_document(
                content=content,
                title=title,
                doc_type=doc_type,
                metadata=metadata
            )
            
            return {
                "success": True,
                "doc_id": doc_id,
                "message": f"Successfully indexed {doc_type} document: {title}"
            }
        except Exception as e:
            self.logger.error(f"Error indexing {doc_type} document: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to index document: {str(e)}"
            }
    
    async def handle_extract_entities(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Extract entities from text document.
        
        Args:
            task_request: Task request with document ID or content
            
        Returns:
            Dict with extracted entities
        """
        doc_id = task_request.payload.get("doc_id")
        content = task_request.payload.get("content")
        use_graphrag = task_request.payload.get("use_graphrag", True)
        
        if not doc_id and not content:
            raise ValueError("Missing required parameter: either doc_id or content must be provided")
        
        # Get document content if doc_id is provided
        if doc_id and not content:
            # In a real implementation, you would retrieve the document content from storage
            # For now, we'll just return an error
            return {
                "doc_id": doc_id,
                "entities": [],
                "entity_count": 0,
                "extraction_method": "local",
                "error": "Document retrieval not implemented yet"
            }
        
        # Skip if no content
        if not content:
            return {
                "doc_id": doc_id,
                "entities": [],
                "entity_count": 0,
                "extraction_method": "local",
                "error": "No content to extract entities from"
            }
        
        try:
            if use_graphrag:
                self.logger.info("Using GraphRAG for entity extraction")
                
                # Extract entities using GraphRAG
                graphrag_entities = await self.graphrag_client.extract_entities(content)
                
                # Format entity results
                entity_results = []
                for entity in graphrag_entities:
                    entity_results.append({
                        "entity_id": entity["entity_id"],
                        "entity_type": entity["entity_type"],
                        "name": entity["name"],
                        "aliases": entity.get("aliases", []),
                        "description": entity.get("description", ""),
                        "confidence": entity.get("confidence", 0.9),
                        "context": entity.get("text", "Context from document")
                    })
                
                return {
                    "doc_id": doc_id,
                    "entities": entity_results,
                    "entity_count": len(entity_results),
                    "extraction_method": "graphrag_mcp"
                }
            
        except Exception as e:
            self.logger.error(f"Error using GraphRAG for entity extraction: {str(e)}")
            # Fall back to local implementation
        
        # Local entity extraction using entity_linker
        self.logger.info("Using local entity extraction")
        
        try:
            # Extract entities using our entity linker
            entities = await self.entity_linker.extract_entities_from_text(content)
            
            # Format entity results
            entity_results = []
            for entity in entities:
                entity_results.append({
                    "entity_id": entity.entity_id,
                    "entity_type": entity.entity_type,
                    "name": entity.name,
                    "aliases": entity.aliases,
                    "description": entity.description or "",
                    "confidence": entity.confidence,
                    "context": entity.mentions[0]["text"] if entity.mentions else "Context from document"
                })
            
            return {
                "doc_id": doc_id,
                "entities": entity_results,
                "entity_count": len(entity_results),
                "extraction_method": "local"
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting entities: {str(e)}")
            return {
                "doc_id": doc_id,
                "entities": [],
                "entity_count": 0,
                "extraction_method": "error",
                "error": f"Entity extraction failed: {str(e)}"
            }
    
    async def handle_extract_enhanced_entities(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Extract entities with enhanced techniques including relationship detection.
        
        Args:
            task_request: Task request with document ID or content
            
        Returns:
            Dictionary with extracted entities and relationships
        """
        doc_id = task_request.payload.get("doc_id")
        content = task_request.payload.get("content")
        min_confidence = task_request.payload.get("min_confidence", 0.6)
        
        if not doc_id and not content:
            return {
                "error": "No document ID or content provided",
                "status": "failed"
            }
        
        if not content:
            return {
                "error": "No content to process",
                "status": "failed"
            }
        
        # Extract entities using enhanced entity linker
        entities = await self.entity_linker.extract_entities_from_text(
            content,
            options={"min_confidence": min_confidence}
        )
        
        # Store extracted entities
        self.extracted_entities = {entity.entity_id: entity for entity in entities}
        
        # Disambiguate entities for better accuracy
        disambiguated_entities = []
        for entity in entities:
            # Get local context for this entity
            context = self._get_entity_context(content, entity)
            
            # Disambiguate entity
            disambiguated = await self.entity_linker.disambiguate_entity(entity, context)
            disambiguated_entities.append(disambiguated)
        
        # Get relationships between entities
        relationship_count = sum(len(entity.relationships) for entity in disambiguated_entities)
        
        # Organize entities by type
        entities_by_type = {}
        for entity in disambiguated_entities:
            entity_type = entity.entity_type
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity.to_dict())
        
        # Identify clusters of related entities
        self.entity_clusters = self._identify_entity_clusters(disambiguated_entities)
        
        # Format response
        response = {
            "doc_id": doc_id,
            "entity_count": len(disambiguated_entities),
            "relationship_count": relationship_count,
            "entities": [entity.to_dict() for entity in disambiguated_entities],
            "entities_by_type": entities_by_type,
            "clusters": self.entity_clusters,
            "status": "success"
        }
        
        return response
    
    def _get_entity_context(self, text: str, entity: Entity) -> str:
        """
        Get contextual text around an entity's mentions.
        
        Args:
            text: Full text
            entity: Entity to get context for
            
        Returns:
            Context text
        """
        if not entity.mentions:
            return entity.name
        
        # Use the first mention
        mention = entity.mentions[0]
        start = mention["start"]
        end = mention["end"]
        
        # Get context around mention (up to 200 chars)
        context_start = max(0, start - 100)
        context_end = min(len(text), end + 100)
        context = text[context_start:context_end]
        
        return context
    
    def _identify_entity_clusters(self, entities: List[Entity]) -> List[Dict[str, Any]]:
        """
        Identify clusters of connected entities.
        
        Args:
            entities: List of entities
            
        Returns:
            List of cluster information
        """
        # Build adjacency graph
        graph = {}
        for entity in entities:
            entity_id = entity.entity_id
            if entity_id not in graph:
                graph[entity_id] = []
            
            for rel in entity.relationships:
                target_id = rel["target_entity_id"]
                graph[entity_id].append(target_id)
                
                # Ensure target is in graph
                if target_id not in graph:
                    graph[target_id] = []
        
        # Find connected components (clusters)
        visited = set()
        clusters = []
        
        for node in graph:
            if node in visited:
                continue
            
            # BFS to find connected component
            cluster = []
            queue = [node]
            visited.add(node)
            
            while queue:
                current = queue.pop(0)
                cluster.append(current)
                
                for neighbor in graph.get(current, []):
                    if neighbor not in visited and neighbor in graph:
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            # Add cluster if it has at least 2 entities
            if len(cluster) >= 2:
                # Get primary entity type for cluster
                cluster_entities = [
                    self.extracted_entities[eid] 
                    for eid in cluster 
                    if eid in self.extracted_entities
                ]
                
                type_counts = {}
                for entity in cluster_entities:
                    entity_type = entity.entity_type
                    if entity_type not in type_counts:
                        type_counts[entity_type] = 0
                    type_counts[entity_type] += 1
                
                primary_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else "unknown"
                
                clusters.append({
                    "entity_ids": cluster,
                    "size": len(cluster),
                    "primary_type": primary_type
                })
        
        # Sort clusters by size
        clusters.sort(key=lambda x: x["size"], reverse=True)
        
        return clusters
    
    async def handle_analyze_entity_relationships(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Analyze relationships between entities.
        
        Args:
            task_request: Task request with entity IDs
            
        Returns:
            Dictionary with relationship analysis
        """
        entity_ids = task_request.payload.get("entity_ids", [])
        
        if not entity_ids:
            # Use all extracted entities if none specified
            entities = list(self.extracted_entities.values())
        else:
            # Get specified entities
            entities = [
                self.extracted_entities[entity_id] 
                for entity_id in entity_ids 
                if entity_id in self.extracted_entities
            ]
        
        if not entities:
            return {
                "error": "No entities found",
                "status": "failed"
            }
        
        # Analyze relationships
        relationship_types = {}
        entity_connections = {}
        
        for entity in entities:
            for rel in entity.relationships:
                # Count relationship types
                rel_type = rel["relation_type"]
                if rel_type not in relationship_types:
                    relationship_types[rel_type] = 0
                relationship_types[rel_type] += 1
                
                # Track connections
                source_id = rel["source_entity_id"]
                target_id = rel["target_entity_id"]
                
                if source_id not in entity_connections:
                    entity_connections[source_id] = set()
                entity_connections[source_id].add(target_id)
        
        # Create relationship map for visualization
        relationship_map = await self.entity_linker.create_entity_map(entities)
        
        # Format response
        response = {
            "entity_count": len(entities),
            "relationship_count": sum(len(entity.relationships) for entity in entities),
            "relationship_types": relationship_types,
            "entity_connectivity": {
                eid: len(connections) for eid, connections in entity_connections.items()
            },
            "clusters": self.entity_clusters if self.entity_clusters else self._identify_entity_clusters(entities),
            "relationship_map": relationship_map,
            "status": "success"
        }
        
        return response
    
    async def handle_generate_entity_map(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Generate an entity map for visualization.
        
        Args:
            task_request: Task request with entity IDs or parameters
            
        Returns:
            Dictionary with entity map data
        """
        entity_ids = task_request.payload.get("entity_ids", [])
        include_all = task_request.payload.get("include_all", False)
        min_confidence = task_request.payload.get("min_confidence", 0.6)
        
        if not entity_ids and not include_all:
            return {
                "error": "No entity IDs provided and include_all not set",
                "status": "failed"
            }
        
        if include_all:
            # Use all extracted entities
            entities = [
                entity for entity in self.extracted_entities.values()
                if entity.confidence >= min_confidence
            ]
        else:
            # Use specified entities
            entities = [
                self.extracted_entities[entity_id] 
                for entity_id in entity_ids 
                if entity_id in self.extracted_entities
            ]
        
        if not entities:
            return {
                "error": "No entities found",
                "status": "failed"
            }
        
        # Generate entity map
        entity_map = await self.entity_linker.create_entity_map(entities)
        
        # Add metadata about the map
        response = {
            "entity_map": entity_map,
            "node_count": len(entity_map["nodes"]),
            "edge_count": len(entity_map["edges"]),
            "entity_types": self._count_entity_types(entities),
            "relation_types": self._count_relation_types(entities),
            "status": "success"
        }
        
        return response
    
    def _count_entity_types(self, entities: List[Entity]) -> Dict[str, int]:
        """
        Count entity types.
        
        Args:
            entities: List of entities
            
        Returns:
            Dictionary with entity type counts
        """
        type_counts = {}
        for entity in entities:
            entity_type = entity.entity_type
            if entity_type not in type_counts:
                type_counts[entity_type] = 0
            type_counts[entity_type] += 1
        
        return type_counts
    
    def _count_relation_types(self, entities: List[Entity]) -> Dict[str, int]:
        """
        Count relationship types.
        
        Args:
            entities: List of entities
            
        Returns:
            Dictionary with relationship type counts
        """
        type_counts = {}
        for entity in entities:
            for rel in entity.relationships:
                rel_type = rel["relation_type"]
                if rel_type not in type_counts:
                    type_counts[rel_type] = 0
                type_counts[rel_type] += 1
        
        return type_counts