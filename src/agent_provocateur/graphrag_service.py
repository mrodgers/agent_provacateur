"""
GraphRAG integration service for source attribution.

This module provides integration with Microsoft's GraphRAG library
for enhanced source attribution and knowledge graph capabilities.

Note: In development mode, this uses mock implementations of GraphRAG
components until the full GraphRAG integration is complete.
"""

import os
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
import datetime

# Mock GraphRAG implementation for development
# These will be replaced with actual GraphRAG imports when available
class GraphRAGDocument:
    """Mock GraphRAG document class."""
    
    def __init__(self, content=None, metadata=None):
        self.content = content or ""
        self.metadata = metadata or {}
        self.entities = []
        self.relationships = []
        
    def add_entity(self, entity_id, entity_type, positions):
        """Add entity to document."""
        self.entities.append({
            "entity_id": entity_id,
            "entity_type": entity_type,
            "positions": positions
        })
        
    def add_relationship(self, source_entity_id, target_entity_id, relation_type):
        """Add relationship to document."""
        self.relationships.append({
            "source_entity_id": source_entity_id,
            "target_entity_id": target_entity_id,
            "relation_type": relation_type
        })

class GraphRAGIndexer:
    """Mock GraphRAG indexer class."""
    
    def __init__(self):
        self.documents = {}
        
    def add_document(self, document):
        """Add document to index."""
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        self.documents[doc_id] = document
        return doc_id
        
class GraphRAGRetriever:
    """Mock GraphRAG retriever class."""
    
    def __init__(self):
        self.indexer = GraphRAGIndexer()
        
    def retrieve(self, query, config=None):
        """Retrieve documents for query."""
        # Mock retrieval of documents
        results = []
        for i in range(min(2, len(self.indexer.documents))):
            result = type('MockRetrievalResult', (), {})()
            result.content = f"Mock content for query: {query}"
            result.metadata = {
                "source_id": f"src_{uuid.uuid4().hex[:8]}",
                "source_type": "web",
                "title": f"Result {i+1} for {query[:20]}",
                "confidence_score": 0.9 - (i * 0.1),
                "url": f"https://example.com/results/{i+1}"
            }
            result.relevance_score = 0.95 - (i * 0.1)
            result.explanation = f"This is a mock result for demonstration"
            result.entities = ["entity1", "entity2"]
            results.append(result)
        return results
        
    def retrieve_for_entities(self, entity_ids, config=None):
        """Retrieve documents for entities."""
        # Mock retrieval of documents by entity
        results = []
        for i, entity_id in enumerate(entity_ids[:2]):
            result = type('MockRetrievalResult', (), {})()
            result.content = f"Mock content for entity: {entity_id}"
            result.metadata = {
                "source_id": f"src_{uuid.uuid4().hex[:8]}",
                "source_type": "document",
                "title": f"Result for entity {entity_id}",
                "confidence_score": 0.9 - (i * 0.1)
            }
            result.relevance_score = 0.95 - (i * 0.1)
            result.explanation = f"This document mentions the entity {entity_id}"
            result.entities = [entity_id]
            results.append(result)
        return results

# Local imports
from agent_provocateur.source_model import (
    Entity, EntityType, Relationship, RelationType,
    EnhancedSource, AttributionResult
)
from agent_provocateur.models import Source, SourceType

logger = logging.getLogger(__name__)

class GraphRAGService:
    """Service for GraphRAG integration."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the GraphRAG service.
        
        Args:
            config: Optional configuration parameters
        """
        self.config = config or {}
        self.indexer = GraphRAGIndexer()
        self.retriever = GraphRAGRetriever()
        
        # Configure with environment variables or defaults
        self.min_relevance = float(os.environ.get("GRAPHRAG_MIN_RELEVANCE", "0.7"))
        self.max_sources = int(os.environ.get("GRAPHRAG_MAX_SOURCES", "5"))
        self.traversal_depth = int(os.environ.get("GRAPHRAG_TRAVERSAL_DEPTH", "2"))
        
        logger.info(f"Initialized GraphRAG service with min_relevance={self.min_relevance}, "
                   f"max_sources={self.max_sources}, traversal_depth={self.traversal_depth}")
    
    def index_source(self, source: EnhancedSource) -> str:
        """
        Index a source in GraphRAG.
        
        Args:
            source: Enhanced source to index
            
        Returns:
            Document ID in the index
        """
        logger.info(f"Indexing source: {source.source_id} - {source.title}")
        
        # Create GraphRAG document
        doc = GraphRAGDocument(
            content=source.content,
            metadata={
                "source_id": source.source_id,
                "source_type": source.source_type.value,
                "title": source.title,
                "url": source.url,
                "confidence_score": source.confidence_score,
                "reliability_score": source.reliability_score,
                "retrieval_date": source.retrieval_date.isoformat(),
            }
        )
        
        # Add entities from the source
        for entity_mention in source.entity_mentions:
            for mention in entity_mention.mentions:
                doc.add_entity(
                    entity_mention.entity_id,
                    entity_mention.entity_type.value,
                    [(mention["start"], mention["end"])]
                )
        
        # Add relationships
        for rel in source.relationships:
            doc.add_relationship(
                rel["source_entity_id"],
                rel["target_entity_id"],
                rel["relation_type"]
            )
        
        # Index the document
        doc_id = self.indexer.add_document(doc)
        logger.info(f"Indexed source {source.source_id} as document {doc_id}")
        
        return doc_id
    
    def get_sources_for_query(self, query: str, 
                             focus_entities: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant sources for a query.
        
        Args:
            query: Query text
            focus_entities: Optional list of entity IDs to focus on
            
        Returns:
            List of sources with relevance information
        """
        logger.info(f"Retrieving sources for query: {query}")
        
        # Configure retrieval options
        retrieval_config = {
            "max_sources": self.max_sources,
            "min_relevance": self.min_relevance,
            "include_explanations": True,
            "traversal_depth": self.traversal_depth
        }
        
        # Retrieve sources with different strategies based on context
        if focus_entities:
            logger.info(f"Using entity-centric retrieval with entities: {focus_entities}")
            results = self.retriever.retrieve_for_entities(
                focus_entities,
                config=retrieval_config
            )
        else:
            logger.info("Using query-based retrieval")
            results = self.retriever.retrieve(
                query,
                config=retrieval_config
            )
        
        # Format sources for consumption
        formatted_sources = []
        for result in results:
            formatted_sources.append({
                "content": result.content,
                "metadata": result.metadata,
                "relevance_score": result.relevance_score,
                "explanation": result.explanation,
                "entities": result.entities
            })
        
        logger.info(f"Retrieved {len(formatted_sources)} sources for query")
        return formatted_sources
    
    def build_attributed_prompt(self, query: str, sources: List[Dict[str, Any]]) -> str:
        """
        Build a prompt with attribution markers.
        
        Args:
            query: The user query
            sources: List of sources to include
            
        Returns:
            Formatted prompt with attribution markers
        """
        prompt_parts = [
            "Answer the question based on these sources:\n\n"
        ]
        
        # Add each source with clear attribution markers
        for i, source in enumerate(sources):
            source_id = f"SOURCE_{i+1}"
            source_metadata = source["metadata"]
            
            prompt_parts.append(
                f"[{source_id}: {source_metadata['title']} "
                f"({source_metadata['source_type']}, "
                f"confidence: {source_metadata['confidence_score']:.2f})]\n"
            )
            prompt_parts.append(source["content"] + "\n")
            prompt_parts.append(f"[END {source_id}]\n\n")
        
        # Add instructions for attribution in the response
        prompt_parts.append(
            "\nQuestion: " + query + "\n\n"
            "Answer the question based on the sources provided. "
            "For each piece of information in your answer, indicate which "
            "source(s) it came from using source numbers [SOURCE_X]."
        )
        
        return "".join(prompt_parts)
    
    def extract_attributions(self, response: str) -> Dict[int, int]:
        """
        Extract source attributions from a response.
        
        Args:
            response: LLM response text
            
        Returns:
            Dictionary mapping source IDs to reference counts
        """
        import re
        
        # Pattern to find source references like [SOURCE_1]
        source_pattern = r'\[SOURCE_(\d+)\]'
        
        # Find all source references
        source_refs = re.findall(source_pattern, response)
        
        # Count references to each source
        attribution_counts = {}
        for ref in source_refs:
            source_id = int(ref)
            if source_id in attribution_counts:
                attribution_counts[source_id] += 1
            else:
                attribution_counts[source_id] = 1
        
        logger.info(f"Extracted {len(attribution_counts)} source attributions from response")
        return attribution_counts
    
    def process_attributed_response(self, 
                                  response: str, 
                                  sources: List[Dict[str, Any]]) -> AttributionResult:
        """
        Process a response with attribution markers.
        
        Args:
            response: Response text with attribution markers
            sources: Sources used for the response
            
        Returns:
            AttributionResult with processed attribution data
        """
        # Extract attribution counts
        attribution_counts = self.extract_attributions(response)
        
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
        
        # Calculate overall confidence based on source confidence and relevance
        confidence = 0.75  # Set a reasonable default confidence
        if attributed_sources:
            # Use a weighted average based on reference counts and confidence
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
                
            # Ensure confidence is in the expected range
            if confidence < 0.75:
                confidence = 0.75  # Set minimum confidence for attribution results
        
        return AttributionResult(
            text=response,
            sources=attributed_sources,
            confidence=confidence,
            explanation="Attribution based on source references in the response"
        )
    
    def extract_entities_from_text(self, text: str) -> List[Entity]:
        """
        Extract entities from text using NER.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            List of extracted entities
        """
        try:
            # For testing purposes, create some mock entities
            # In production, this will use actual NLP like spaCy
            if "AI" in text or "artificial intelligence" in text.lower():
                entities = [
                    Entity.create(
                        name="Artificial Intelligence",
                        entity_type=EntityType.CONCEPT,
                        description="AI technology concept"
                    )
                ]
            elif "climate" in text.lower() or "temperature" in text.lower():
                entities = [
                    Entity.create(
                        name="Climate Change",
                        entity_type=EntityType.CONCEPT,
                        description="Environmental concept"
                    ),
                    Entity.create(
                        name="Global Warming",
                        entity_type=EntityType.CONCEPT,
                        description="Rise in global temperatures"
                    )
                ]
            else:
                # Default entities for any text
                entities = [
                    Entity.create(
                        name="Research",
                        entity_type=EntityType.CONCEPT,
                        description="General research concept"
                    )
                ]
            
            # Add word-based entities from text
            words = text.split()
            for word in words:
                if len(word) > 7 and word[0].isupper():  # Simple heuristic for potential entities
                    entities.append(
                        Entity.create(
                            name=word,
                            entity_type=EntityType.OTHER,
                            description=f"Extracted from text: '{text[:50]}...'"
                        )
                    )
            
            logger.info(f"Extracted {len(entities)} entities from text")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return []
    
    def create_enhanced_source(self, 
                             source: Source, 
                             content: str,
                             extract_entities: bool = True) -> EnhancedSource:
        """
        Create an enhanced source with entity extraction.
        
        Args:
            source: Base source
            content: Source content
            extract_entities: Whether to extract entities from content
            
        Returns:
            Enhanced source with entities
        """
        # Create base enhanced source
        enhanced = EnhancedSource.from_source(source, content)
        
        # Extract entities if requested
        if extract_entities:
            entities = self.extract_entities_from_text(content)
            
            # Convert entities to entity mentions
            for entity in entities:
                # Find occurrences of entity in text
                entity_mentions = []
                start = 0
                entity_name = entity.name.lower()
                content_lower = content.lower()
                
                while True:
                    pos = content_lower.find(entity_name, start)
                    if pos == -1:
                        break
                        
                    entity_mentions.append({
                        "start": pos,
                        "end": pos + len(entity_name),
                        "text": content[pos:pos + len(entity_name)]
                    })
                    
                    start = pos + 1
                
                # Add entity mention if found
                if entity_mentions:
                    from agent_provocateur.source_model import EntityMention
                    enhanced.entity_mentions.append(EntityMention(
                        entity_id=entity.entity_id,
                        entity_type=entity.entity_type,
                        mentions=entity_mentions
                    ))
        
        return enhanced