"""
XML source attribution service using GraphRAG.

This module enhances XML documents with source attribution
using Microsoft's GraphRAG library.
"""

import logging
import asyncio
import uuid
import datetime
from typing import Any, Dict, List, Optional, Union

from agent_provocateur.models import Source, SourceType, XmlDocument, XmlNode
from agent_provocateur.source_model import EnhancedSource, Entity, EntityType
from agent_provocateur.graphrag_service import GraphRAGService

logger = logging.getLogger(__name__)

class XmlAttributionService:
    """Service for enhancing XML documents with source attribution."""
    
    def __init__(self):
        """Initialize the XML attribution service."""
        self.graphrag = GraphRAGService()
        logger.info("Initialized XML Attribution Service with GraphRAG integration")
    
    async def process_xml_document(self, doc: XmlDocument) -> XmlDocument:
        """
        Process an XML document to enhance it with source attribution.
        
        Args:
            doc: XML document to process
            
        Returns:
            Enhanced document with source attribution
        """
        logger.info(f"Processing XML document {doc.doc_id} for source attribution")
        
        # Skip if no researchable nodes
        if not doc.researchable_nodes:
            logger.info(f"No researchable nodes in document {doc.doc_id}, skipping attribution")
            return doc
        
        # Process each node asynchronously
        tasks = []
        for node in doc.researchable_nodes:
            if node.content:  # Only process nodes with content
                tasks.append(self.attribute_node(node, doc.doc_id))
        
        # Wait for all attribution tasks to complete
        processed_nodes = await asyncio.gather(*tasks)
        
        # Update the document with processed nodes
        for processed_node in processed_nodes:
            # Find and replace the corresponding node in the document
            for i, node in enumerate(doc.researchable_nodes):
                if node.xpath == processed_node.xpath:
                    doc.researchable_nodes[i] = processed_node
                    break
        
        logger.info(f"Completed source attribution for document {doc.doc_id}")
        return doc
    
    async def attribute_node(self, node: XmlNode, doc_id: str) -> XmlNode:
        """
        Attribute a single XML node using GraphRAG.
        
        Args:
            node: XML node to attribute
            doc_id: Document ID for context
            
        Returns:
            Node with enhanced source attribution
        """
        if not node.content:
            logger.info(f"Node {node.xpath} has no content, skipping attribution")
            return node
        
        try:
            logger.info(f"Attributing node: {node.element_name} at {node.xpath}")
            
            # Check if node already has sources
            if node.sources:
                logger.info(f"Node {node.xpath} already has {len(node.sources)} sources")
                
                # Index existing sources in GraphRAG
                for source in node.sources:
                    # Skip if source doesn't have content
                    if not source.metadata.get("content"):
                        continue
                        
                    # Create enhanced source
                    enhanced = EnhancedSource.from_source(
                        source, 
                        source.metadata.get("content", "No content available")
                    )
                    
                    # Index in GraphRAG
                    self.graphrag.index_source(enhanced)
            
            # Get sources for node content
            query = node.content
            sources = self.graphrag.get_sources_for_query(query)
            
            # If no sources found, extract entities and try entity-focused search
            if not sources:
                logger.info(f"No sources found for direct query, trying entity-focused search")
                
                # Extract entities
                entities = self.graphrag.extract_entities_from_text(query)
                if entities:
                    entity_ids = [entity.entity_id for entity in entities]
                    logger.info(f"Found entities: {', '.join(e.name for e in entities)}")
                    
                    # Try entity-focused search
                    sources = self.graphrag.get_sources_for_query(query, focus_entities=entity_ids)
            
            # Process sources into the format needed for XML node
            processed_sources = []
            for i, src in enumerate(sources):
                metadata = src["metadata"]
                source_id = metadata.get("source_id", f"src_{uuid.uuid4().hex[:8]}")
                
                # Determine source type
                try:
                    source_type = SourceType(metadata.get("source_type", "other"))
                except ValueError:
                    source_type = SourceType.OTHER
                
                # Create Source object
                source = Source(
                    source_id=source_id,
                    source_type=source_type,
                    title=metadata.get("title", f"Source {i+1}"),
                    url=metadata.get("url"),
                    confidence=float(metadata.get("confidence_score", 0.5)),
                    retrieved_at=datetime.datetime.now(),
                    metadata={
                        "relevance_score": src.get("relevance_score", 0.5),
                        "explanation": src.get("explanation", ""),
                        "content_preview": src["content"][:200] + "..." if len(src["content"]) > 200 else src["content"]
                    }
                )
                
                processed_sources.append(source)
            
            # Update the node
            if processed_sources:
                # Determine verification status based on sources
                if len(processed_sources) > 1 and processed_sources[0].confidence > 0.8:
                    status = "verified"
                elif len(processed_sources) > 0:
                    status = "partially_verified"
                else:
                    status = "unverified"
                
                # Calculate confidence score based on source relevance and confidence
                if processed_sources:
                    avg_confidence = sum(s.confidence for s in processed_sources) / len(processed_sources)
                    avg_relevance = sum(float(s.metadata.get("relevance_score", 0.5)) 
                                      for s in processed_sources) / len(processed_sources)
                    confidence = (avg_confidence + avg_relevance) / 2
                else:
                    confidence = 0.5
                
                # Update node with attribution data
                node.sources = processed_sources
                node.verification_status = status
                node.verification_data = {
                    "confidence": confidence,
                    "source_count": len(processed_sources),
                    "verification_method": "graphrag",
                    "verification_timestamp": datetime.datetime.now().isoformat(),
                    "verification_notes": f"Verified using GraphRAG with {len(processed_sources)} sources"
                }
                
                logger.info(f"Added {len(processed_sources)} sources to node {node.xpath}")
            else:
                logger.warning(f"No sources found for node {node.xpath}")
                
                # Fallback to basic source
                fallback_source = Source(
                    source_id=f"fallback_{uuid.uuid4().hex[:8]}",
                    source_type=SourceType.OTHER,
                    title="No external sources found",
                    confidence=0.3,
                    retrieved_at=datetime.datetime.now(),
                    metadata={
                        "fallback": True,
                        "notes": "No external sources could be found to verify this content"
                    }
                )
                
                # Update node with fallback
                node.sources = [fallback_source]
                node.verification_status = "unverified"
                node.verification_data = {
                    "confidence": 0.3,
                    "source_count": 1,
                    "verification_method": "fallback",
                    "verification_timestamp": datetime.datetime.now().isoformat(),
                    "verification_notes": "No attribution sources found"
                }
            
            return node
            
        except Exception as e:
            logger.error(f"Error attributing node {node.xpath}: {str(e)}")
            
            # Return original node on error
            return node
    
    async def attribute_document_from_web_search(self, 
                                              doc: XmlDocument, 
                                              search_results: List[Dict[str, Any]]) -> XmlDocument:
        """
        Enhance XML document attribution using web search results.
        
        Args:
            doc: XML document to enhance
            search_results: List of web search results
            
        Returns:
            Enhanced document with attribution from web search
        """
        logger.info(f"Enhancing document {doc.doc_id} with {len(search_results)} web search results")
        
        # Process search results into enhanced sources
        for result in search_results:
            try:
                # Create source from search result
                source = Source(
                    source_id=f"web_{uuid.uuid4().hex[:8]}",
                    source_type=SourceType.WEB,
                    title=result.get("title", "Web Search Result"),
                    url=result.get("url"),
                    confidence=0.7,  # Default confidence for web search
                    retrieved_at=datetime.datetime.now(),
                    metadata={
                        "snippet": result.get("snippet", ""),
                        "search_rank": result.get("rank", 0)
                    }
                )
                
                # Create enhanced source
                content = result.get("snippet", "") 
                if "content" in result and result["content"]:
                    content = result["content"]
                    
                enhanced = self.graphrag.create_enhanced_source(source, content)
                
                # Index in GraphRAG
                self.graphrag.index_source(enhanced)
                
            except Exception as e:
                logger.error(f"Error processing search result: {str(e)}")
        
        # Now process the document for attribution
        return await self.process_xml_document(doc)
    
    def extract_entities_from_document(self, doc: XmlDocument) -> List[Entity]:
        """
        Extract entities from an XML document.
        
        Args:
            doc: XML document to process
            
        Returns:
            List of extracted entities
        """
        entities = []
        
        # Extract from researchable nodes
        for node in doc.researchable_nodes:
            if node.content:
                node_entities = self.graphrag.extract_entities_from_text(node.content)
                entities.extend(node_entities)
        
        # Deduplicate entities
        unique_entities = {}
        for entity in entities:
            if entity.name.lower() not in unique_entities:
                unique_entities[entity.name.lower()] = entity
        
        return list(unique_entities.values())