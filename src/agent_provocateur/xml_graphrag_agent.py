"""
XML Agent with GraphRAG integration.

This agent extends the XmlAgent with GraphRAG capabilities for enhanced
source attribution and entity extraction using the GraphRAG MCP server.
"""

import logging
import asyncio
import os
from typing import Dict, List, Any, Optional

from agent_provocateur.xml_agent import XmlAgent
from agent_provocateur.a2a_models import TaskRequest
from agent_provocateur.models import XmlDocument, XmlNode, Source, SourceType
from agent_provocateur.graphrag_client import GraphRAGClient

logger = logging.getLogger(__name__)

class XmlGraphRAGAgent(XmlAgent):
    """XML Agent with GraphRAG integration."""
    
    async def on_startup(self) -> None:
        """Initialize the XML GraphRAG agent."""
        await super().on_startup()
        
        # Initialize GraphRAG client
        graphrag_url = os.environ.get("GRAPHRAG_MCP_URL", "http://localhost:8083")
        self.graphrag_client = GraphRAGClient(base_url=graphrag_url)
        self.logger.info(f"Initialized XML GraphRAG agent with server: {graphrag_url}")
    
    async def handle_extract_entities(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Extract research entities from XML content with GraphRAG integration.
        
        Args:
            task_request: Task request with document ID
            
        Returns:
            Dict with extracted entities and confidence
        """
        doc_id = task_request.payload.get("doc_id")
        if not doc_id:
            raise ValueError("Missing required parameter: doc_id")
        
        use_graphrag = task_request.payload.get("use_graphrag", True)
        
        # Get XML document
        xml_doc = await self.async_mcp_client.get_xml_document(doc_id)
        
        # Use GraphRAG for entity extraction
        if use_graphrag:
            try:
                self.logger.info(f"Using GraphRAG MCP for entity extraction")
                
                # Extract text from all researchable nodes
                all_text = ""
                for node in xml_doc.researchable_nodes:
                    if node.content:
                        all_text += f"{node.content}\n\n"
                
                # Skip if no content
                if not all_text:
                    return {
                        "doc_id": doc_id,
                        "entities": [],
                        "entity_count": 0,
                        "extraction_method": "graphrag_mcp",
                        "error": "No content to extract entities from"
                    }
                
                # Extract entities using GraphRAG MCP
                entities = await self.graphrag_client.extract_entities(all_text)
                
                # Format entity results
                entity_results = []
                for entity in entities:
                    # Find the node containing this entity
                    containing_node = None
                    for node in xml_doc.researchable_nodes:
                        if node.content and entity["name"].lower() in node.content.lower():
                            containing_node = node
                            break
                    
                    # Default XPath if no containing node found
                    xpath = "//content" if not containing_node else containing_node.xpath
                    
                    entity_results.append({
                        "entity_id": entity["entity_id"],
                        "entity_type": entity["entity_type"],
                        "name": entity["name"],
                        "aliases": entity.get("aliases", []),
                        "description": entity.get("description", ""),
                        "xpath": xpath,
                        "confidence": entity.get("confidence", 0.9),
                        "context": entity.get("text", "Context from XML document")
                    })
                
                # Return results
                return {
                    "doc_id": doc_id,
                    "entities": entity_results,
                    "entity_count": len(entity_results),
                    "extraction_method": "graphrag_mcp"
                }
                
            except Exception as e:
                self.logger.error(f"Error using GraphRAG MCP for entity extraction: {str(e)}")
                # Fall back to super implementation
        
        # Fall back to super implementation
        return await super().handle_extract_entities(task_request)
    
    async def handle_batch_verify_nodes(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Verify multiple nodes using GraphRAG attribution.
        
        Args:
            task_request: Task request with document ID and nodes
            
        Returns:
            Dict with verification results
        """
        doc_id = task_request.payload.get("doc_id")
        nodes = task_request.payload.get("nodes", [])
        options = task_request.payload.get("options", {})
        use_graphrag = options.get("use_graphrag", True)
        
        if not doc_id:
            raise ValueError("Missing required parameter: doc_id")
        
        # Get document
        xml_doc = await self.async_mcp_client.get_xml_document(doc_id)
        
        if not nodes:
            # If no specific nodes provided, get all pending nodes
            nodes = [
                node.dict() for node in xml_doc.researchable_nodes 
                if node.verification_status == "pending"
            ]
        
        # Use GraphRAG for attribution if enabled
        if use_graphrag:
            try:
                self.logger.info(f"Using GraphRAG MCP for batch verification of {len(nodes)} nodes")
                
                # Process each node
                verification_results = []
                completed = 0
                
                for node_dict in nodes:
                    xpath = node_dict.get("xpath")
                    element_name = node_dict.get("element_name", "unknown")
                    content = node_dict.get("content", "")
                    
                    # Skip empty content
                    if not content or content.strip() == "":
                        continue
                    
                    # Get sources for node content
                    try:
                        sources, _ = await self.graphrag_client.get_sources_for_query(content)
                        
                        # Create Source objects
                        processed_sources = []
                        for source in sources:
                            metadata = source["metadata"]
                            source_obj = Source(
                                source_id=metadata.get("source_id", f"src_{element_name}"),
                                source_type=getattr(SourceType, metadata.get("source_type", "OTHER").upper(), SourceType.OTHER),
                                title=metadata.get("title", f"Source for {element_name}"),
                                url=metadata.get("url"),
                                confidence=metadata.get("confidence_score", 0.8),
                                metadata={
                                    "relevance_score": source.get("relevance_score", 0.8),
                                    "explanation": source.get("explanation", ""),
                                    "content_preview": source["content"][:200] + "..." if len(source["content"]) > 200 else source["content"]
                                }
                            )
                            processed_sources.append(source_obj)
                        
                        # Determine verification status
                        if len(processed_sources) > 1 and processed_sources[0].confidence > 0.8:
                            status = "verified"
                            confidence = processed_sources[0].confidence
                        elif len(processed_sources) > 0:
                            status = "partially_verified"
                            confidence = processed_sources[0].confidence * 0.8
                        else:
                            status = "unverified"
                            confidence = 0.5
                        
                        # Add verification result
                        verification_results.append({
                            "xpath": xpath,
                            "element_name": element_name,
                            "content": content,
                            "status": status,
                            "confidence": confidence,
                            "sources": processed_sources,
                            "notes": f"Verified using GraphRAG MCP with {len(processed_sources)} sources"
                        })
                        
                        completed += 1
                        
                    except Exception as e:
                        self.logger.error(f"Error verifying node {xpath}: {str(e)}")
                        verification_results.append({
                            "xpath": xpath,
                            "element_name": element_name,
                            "content": content,
                            "status": "error",
                            "confidence": 0.3,
                            "sources": [],
                            "notes": f"Error during verification: {str(e)}"
                        })
                
                return {
                    "doc_id": doc_id,
                    "total_nodes": len(nodes),
                    "completed_nodes": completed,
                    "verification_results": verification_results,
                    "verification_method": "graphrag_mcp",
                    "options": options
                }
                
            except Exception as e:
                self.logger.error(f"Error using GraphRAG MCP for batch verification: {str(e)}")
                self.logger.info("Falling back to traditional verification method")
        
        # Fall back to super implementation
        return await super().handle_batch_verify_nodes(task_request)
    
    async def process_attributed_response(self, 
                                        response: str, 
                                        sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a response with attribution markers.
        
        Args:
            response: Response text with attribution markers
            sources: Sources used for the response
            
        Returns:
            AttributionResult with processed attribution data
        """
        try:
            # Process using GraphRAG client
            return await self.graphrag_client.process_attributed_response(response, sources)
        except Exception as e:
            self.logger.error(f"Error processing attributed response: {str(e)}")
            
            # Basic fallback processing
            return {
                "text": response,
                "sources": sources,
                "confidence": 0.75,
                "explanation": "Basic attribution fallback due to error"
            }