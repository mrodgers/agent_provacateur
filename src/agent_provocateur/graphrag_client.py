"""
GraphRAG MCP client for agent integration.

This module provides a client for interacting with the GraphRAG MCP server,
allowing agents to use graph-based retrieval-augmented generation capabilities.
"""

import aiohttp
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
import datetime
import os

logger = logging.getLogger(__name__)

class GraphRAGClient:
    """Client for the GraphRAG MCP server."""
    
    def __init__(self, base_url: str = None):
        """
        Initialize the GraphRAG client.
        
        Args:
            base_url: Base URL of the GraphRAG MCP server.
                     If not provided, uses GRAPHRAG_MCP_URL environment variable
                     or defaults to http://localhost:8083
        """
        self.base_url = base_url or os.environ.get("GRAPHRAG_MCP_URL", "http://localhost:8083")
        logger.info(f"Initialized GraphRAG client with server: {self.base_url}")
        
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the GraphRAG MCP server.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
            
        Returns:
            Tool response
            
        Raises:
            Exception: If the call fails
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/tools/{tool_name}"
            logger.debug(f"Calling GraphRAG tool: {tool_name} at {url}")
            
            try:
                async with session.post(url, json=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Error calling {tool_name}: {error_text}")
                        raise Exception(f"GraphRAG MCP error: {error_text}")
                    
                    return await response.json()
            except aiohttp.ClientConnectorError as e:
                logger.error(f"Connection error to GraphRAG MCP server: {e}")
                raise Exception(f"Could not connect to GraphRAG MCP server at {self.base_url}")
            except Exception as e:
                logger.error(f"Error calling {tool_name}: {e}")
                raise
    
    async def get_server_info(self) -> Dict[str, Any]:
        """
        Get information about the GraphRAG MCP server.
        
        Returns:
            Server information
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/info"
            logger.debug(f"Getting GraphRAG server info from {url}")
            
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Error getting server info: {error_text}")
                        raise Exception(f"GraphRAG MCP error: {error_text}")
                    
                    return await response.json()
            except Exception as e:
                logger.error(f"Error getting server info: {e}")
                raise
    
    async def index_source(self, source: Dict[str, Any]) -> str:
        """
        Index a source in GraphRAG.
        
        Args:
            source: Source to index with required fields:
                   source_id, source_type, title, content
            
        Returns:
            Document ID in the index
        """
        result = await self.call_tool("graphrag_index_source", {
            "source": source
        })
        
        if not result.get("success"):
            raise Exception(f"Failed to index source: {result.get('error')}")
        
        return result.get("doc_id")
    
    async def extract_entities(self, text: str, options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Extract entities from text.
        
        Args:
            text: Text to extract entities from
            options: Optional extraction options
            
        Returns:
            List of extracted entities
        """
        result = await self.call_tool("graphrag_extract_entities", {
            "text": text,
            "options": options or {}
        })
        
        if not result.get("success"):
            raise Exception(f"Failed to extract entities: {result.get('error')}")
        
        return result.get("entities", [])
    
    async def get_sources_for_query(
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
        result = await self.call_tool("graphrag_query", {
            "query": query,
            "focus_entities": focus_entities,
            "options": options or {}
        })
        
        if not result.get("success"):
            raise Exception(f"Failed to get sources: {result.get('error')}")
        
        return result.get("sources", []), result.get("attributed_prompt", "")
    
    async def get_entity(self, entity_id: str) -> Dict[str, Any]:
        """
        Get entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity data
        """
        result = await self.call_tool("graphrag_entity_lookup", {
            "entity_id": entity_id
        })
        
        if not result.get("success"):
            raise Exception(f"Failed to get entity: {result.get('error')}")
        
        return result.get("entity", {})
    
    async def generate_concept_map(
        self, 
        focus_entities: List[str], 
        traversal_depth: int = 2
    ) -> Dict[str, Any]:
        """
        Generate a concept map.
        
        Args:
            focus_entities: Entity IDs to focus on
            traversal_depth: Maximum traversal depth
            
        Returns:
            Concept map with nodes and edges
        """
        result = await self.call_tool("graphrag_concept_map", {
            "focus_entities": focus_entities,
            "traversal_depth": traversal_depth
        })
        
        if not result.get("success"):
            raise Exception(f"Failed to generate concept map: {result.get('error')}")
        
        return {
            "nodes": result.get("nodes", []),
            "edges": result.get("edges", [])
        }
    
    async def process_attributed_response(
        self, 
        response: str, 
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a response with attribution markers.
        
        Args:
            response: Response text with attribution markers
            sources: Sources used for the response
            
        Returns:
            Attribution result
        """
        # This functionality is handled on the server side in the GraphRAG service
        # For now, we'll implement a simple version client-side
        # Extract source references like [SOURCE_1]
        import re
        
        source_pattern = r'\[SOURCE_(\d+)\]'
        source_refs = re.findall(source_pattern, response)
        
        # Count references to each source
        attribution_counts = {}
        for ref in source_refs:
            source_id = int(ref)
            if source_id in attribution_counts:
                attribution_counts[source_id] += 1
            else:
                attribution_counts[source_id] = 1
        
        # Map sources
        attributed_sources = []
        for source_num, count in attribution_counts.items():
            if source_num <= len(sources):
                source_idx = source_num - 1  # Convert from 1-indexed to 0-indexed
                source = sources[source_idx]
                attributed_sources.append({
                    "source_id": source["metadata"].get("source_id", f"unknown_{source_idx}"),
                    "title": source["metadata"].get("title", "Unknown Source"),
                    "reference_count": count,
                    "relevance_score": source.get("relevance_score", 0.0),
                    "metadata": source["metadata"]
                })
        
        # Calculate overall confidence
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
            if confidence < 0.75:
                confidence = 0.75
        
        return {
            "text": response,
            "sources": attributed_sources,
            "confidence": confidence,
            "explanation": "Attribution based on source references in the response"
        }