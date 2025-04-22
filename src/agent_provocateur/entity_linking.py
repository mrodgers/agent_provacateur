"""
Enhanced entity linking capabilities for Agent Provocateur.

This module provides advanced entity extraction, linking, and relationship detection 
capabilities for improved document analysis and research workflows.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
import re
import logging
import os
import json
import uuid
from enum import Enum

from .graphrag_client import GraphRAGClient

logger = logging.getLogger(__name__)

class EntityType(str, Enum):
    """Entity types for enhanced entity linking."""
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
    """Relationship types for enhanced entity linking."""
    IS_A = "is_a"
    PART_OF = "part_of"
    HAS_PART = "has_part"
    LOCATED_IN = "located_in"
    CREATED_BY = "created_by"
    WORKS_FOR = "works_for"
    OWNED_BY = "owned_by"
    HAS_PROPERTY = "has_property"
    RELATED_TO = "related_to"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    OTHER = "other"


class Entity:
    """Entity representation with enhanced capabilities."""
    
    def __init__(
        self,
        name: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        description: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        confidence: float = 0.7
    ):
        """
        Initialize an entity.
        
        Args:
            name: Entity name
            entity_type: Entity type (should match EntityType enum)
            entity_id: Optional entity ID (generated if not provided)
            description: Optional entity description
            aliases: Optional list of alternative names
            metadata: Optional additional metadata
            confidence: Confidence score for this entity
        """
        self.entity_id = entity_id or f"entity_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.entity_type = entity_type
        self.description = description
        self.aliases = aliases or []
        self.metadata = metadata or {}
        self.confidence = confidence
        
        # Track mentions and relationships
        self.mentions: List[Dict[str, Any]] = []
        self.relationships: List[Dict[str, Any]] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "entity_type": self.entity_type,
            "description": self.description,
            "aliases": self.aliases,
            "metadata": self.metadata,
            "confidence": self.confidence,
            "mentions": self.mentions,
            "relationships": self.relationships
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create from dictionary representation."""
        entity = cls(
            entity_id=data.get("entity_id"),
            name=data["name"],
            entity_type=data["entity_type"],
            description=data.get("description"),
            aliases=data.get("aliases", []),
            metadata=data.get("metadata", {}),
            confidence=data.get("confidence", 0.7)
        )
        entity.mentions = data.get("mentions", [])
        entity.relationships = data.get("relationships", [])
        return entity
    
    def add_mention(self, text: str, start: int, end: int, score: float = 0.8) -> None:
        """
        Add a mention of this entity in text.
        
        Args:
            text: The text containing the mention
            start: Start position in text
            end: End position in text
            score: Confidence score for this mention
        """
        self.mentions.append({
            "text": text[start:end],
            "start": start,
            "end": end,
            "score": score
        })
    
    def add_relationship(
        self, 
        target_entity_id: str, 
        relation_type: str, 
        confidence: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a relationship to another entity.
        
        Args:
            target_entity_id: ID of the target entity
            relation_type: Type of relationship (should match RelationType enum)
            confidence: Confidence score for this relationship
            metadata: Optional additional metadata
        """
        self.relationships.append({
            "relationship_id": f"rel_{uuid.uuid4().hex[:8]}",
            "source_entity_id": self.entity_id,
            "target_entity_id": target_entity_id,
            "relation_type": relation_type,
            "confidence": confidence,
            "metadata": metadata or {}
        })


class Relationship:
    """Relationship between entities with enhanced contextual information."""
    
    def __init__(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relation_type: str,
        relationship_id: Optional[str] = None,
        confidence: float = 0.7,
        bidirectional: bool = False,
        context: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a relationship.
        
        Args:
            source_entity_id: ID of the source entity
            target_entity_id: ID of the target entity
            relation_type: Type of relationship (should match RelationType enum)
            relationship_id: Optional relationship ID (generated if not provided)
            confidence: Confidence score for this relationship
            bidirectional: Whether the relationship is bidirectional
            context: Optional textual context for this relationship
            metadata: Optional additional metadata
        """
        self.relationship_id = relationship_id or f"rel_{uuid.uuid4().hex[:8]}"
        self.source_entity_id = source_entity_id
        self.target_entity_id = target_entity_id
        self.relation_type = relation_type
        self.confidence = confidence
        self.bidirectional = bidirectional
        self.context = context
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "relationship_id": self.relationship_id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "relation_type": self.relation_type,
            "confidence": self.confidence,
            "bidirectional": self.bidirectional,
            "context": self.context,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create from dictionary representation."""
        return cls(
            relationship_id=data.get("relationship_id"),
            source_entity_id=data["source_entity_id"],
            target_entity_id=data["target_entity_id"],
            relation_type=data["relation_type"],
            confidence=data.get("confidence", 0.7),
            bidirectional=data.get("bidirectional", False),
            context=data.get("context"),
            metadata=data.get("metadata", {})
        )


class EntityLinker:
    """
    Enhanced entity linking system for Document Analysis.
    
    This system provides advanced entity extraction, disambiguation, and 
    relationship detection capabilities. It integrates with GraphRAG for
    knowledge base integration and semantic matching.
    """
    
    def __init__(self, graphrag_client: Optional[GraphRAGClient] = None):
        """
        Initialize the entity linker.
        
        Args:
            graphrag_client: Optional GraphRAG client for enhanced capabilities
        """
        self.graphrag_client = graphrag_client
        
        # Entity type patterns
        self._entity_patterns = {
            EntityType.PERSON: [
                r'(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.) [A-Z][a-z]+(?: [A-Z][a-z]+)+',
                r'[A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)*',
            ],
            EntityType.ORGANIZATION: [
                r'(?:The |)[A-Z][a-z]+(?: [A-Z][a-z]+)* (?:Corporation|Company|Inc\.|Ltd\.|LLC|GmbH|Foundation|Association|University|Institute)',
                r'[A-Z]{2,}(?:\s+[A-Z][a-z]+)*',  # Acronyms like "IBM" or "UNICEF"
                r'[A-Z][a-zA-Z]+',  # Mixed case company names like OpenAI
            ],
            EntityType.LOCATION: [
                r'(?:in |at |from |to )(?:the |)[A-Z][a-z]+(?: [A-Z][a-z]+)*',
                r'(?:northern|southern|eastern|western|north|south|east|west) [A-Z][a-z]+',
            ],
            EntityType.DATE: [
                r'\d{1,2}/\d{1,2}/\d{2,4}',
                r'\d{1,2}-\d{1,2}-\d{2,4}',
                r'(?:January|February|March|April|May|June|July|August|September|October|November|December)(?: \d{1,2})?,? \d{4}',
            ],
            EntityType.CONCEPT: [
                r'(?:concept of |theory of |principle of |idea of |)[A-Z][a-z]+(?: [A-Z][a-z]+)*',
            ],
        }
        
        # Contextual relationship patterns
        self._relationship_patterns = {
            RelationType.IS_A: [
                r'(.*) is an? (.*)',
                r'(.*) are (?:a type|types) of (.*)',
            ],
            RelationType.PART_OF: [
                r'(.*) is (?:part|a part) of (.*)',
                r'(.*) belongs to (.*)',
            ],
            RelationType.LOCATED_IN: [
                r'(.*) is (?:located|situated|based) in (.*)',
                r'(.*) is headquartered in (.*)',
            ],
            RelationType.CREATED_BY: [
                r'(.*) (?:created|developed|invented|designed) by (.*)',
                r'(.*) is the creator of (.*)',
            ],
            RelationType.WORKS_FOR: [
                r'(.*) works for (.*)',
                r'(.*) is (?:employed|hired) by (.*)',
            ],
            RelationType.CONTRADICTS: [
                r'(.*) contradicts (.*)',
                r'(.*) disagrees with (.*)',
            ],
            RelationType.SUPPORTS: [
                r'(.*) supports (.*)',
                r'(.*) confirms (.*)',
            ],
        }
        
        # Entity keyword mapping (well-known entities)
        self._keyword_entity_map = {
            'artificial intelligence': {
                'name': 'Artificial Intelligence',
                'entity_type': EntityType.CONCEPT,
                'aliases': ['AI', 'machine intelligence', 'machine learning'],
                'confidence': 0.95
            },
            'openai': {
                'name': 'OpenAI',
                'entity_type': EntityType.ORGANIZATION,
                'aliases': ['openai'],
                'confidence': 0.95
            },
            'google': {
                'name': 'Google',
                'entity_type': EntityType.ORGANIZATION,
                'aliases': ['google'],
                'confidence': 0.95
            },
            'climate change': {
                'name': 'Climate Change',
                'entity_type': EntityType.CONCEPT,
                'aliases': ['global warming', 'climate crisis'],
                'confidence': 0.95
            },
            'united nations': {
                'name': 'United Nations',
                'entity_type': EntityType.ORGANIZATION,
                'aliases': ['UN'],
                'confidence': 0.95
            },
            'european union': {
                'name': 'European Union',
                'entity_type': EntityType.ORGANIZATION,
                'aliases': ['EU'],
                'confidence': 0.95
            },
            'united states': {
                'name': 'United States',
                'entity_type': EntityType.LOCATION,
                'aliases': ['US', 'USA', 'America'],
                'confidence': 0.95
            },
        }
    
    async def extract_entities_from_text(self, text: str, options: Optional[Dict[str, Any]] = None) -> List[Entity]:
        """
        Extract entities from text with advanced techniques.
        
        This method uses pattern matching, contextual clues, and potentially 
        GraphRAG integration for enhanced entity extraction.
        
        Args:
            text: Text to extract entities from
            options: Optional extraction options
            
        Returns:
            List of extracted entities
        """
        if not text:
            return []
        
        options = options or {}
        min_confidence = options.get('min_confidence', 0.5)
        use_graphrag = options.get('use_graphrag', self.graphrag_client is not None)
        
        # First try GraphRAG if available and requested
        entities = []
        if use_graphrag and self.graphrag_client:
            try:
                graphrag_entities = await self.graphrag_client.extract_entities(text, options)
                
                # Convert GraphRAG entities to our format
                for gent in graphrag_entities:
                    entity = Entity(
                        name=gent['name'],
                        entity_type=gent['entity_type'],
                        entity_id=gent.get('entity_id'),
                        description=gent.get('description'),
                        aliases=gent.get('aliases', []),
                        metadata=gent.get('metadata', {}),
                        confidence=gent.get('confidence', 0.8)
                    )
                    entities.append(entity)
                
                logger.info(f"Extracted {len(entities)} entities from GraphRAG")
                
                # If we got entities from GraphRAG, we can return them directly
                if entities:
                    return entities
            except Exception as e:
                logger.warning(f"Error extracting entities from GraphRAG: {e}")
        
        # If GraphRAG failed or wasn't used, fall back to our own implementation
        logger.info("Using local entity extraction")
        
        # Dictionary to track unique entities
        entity_map: Dict[str, Entity] = {}
        
        # First pass: extract known entities from keyword mapping
        text_lower = text.lower()
        for keyword, entity_info in self._keyword_entity_map.items():
            if keyword in text_lower:
                if keyword not in entity_map:
                    entity = Entity(
                        name=entity_info['name'],
                        entity_type=entity_info['entity_type'],
                        aliases=entity_info.get('aliases', []),
                        confidence=entity_info.get('confidence', 0.9)
                    )
                    
                    # Find positions of mentions
                    start = 0
                    while True:
                        pos = text_lower.find(keyword, start)
                        if pos == -1:
                            break
                        
                        entity.add_mention(text, pos, pos + len(keyword), 0.9)
                        start = pos + 1
                    
                    entity_map[keyword] = entity
        
        # Second pass: extract entities based on pattern matching
        for entity_type, patterns in self._entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    name = match.group(0)
                    
                    # Clean up the name (remove context prefixes like "in" or "from")
                    name = re.sub(r'^(?:in|at|from|to|by|the) ', '', name).strip()
                    
                    # Skip if too short
                    if len(name) < 3:
                        continue
                    
                    # Skip common words that are likely false positives
                    if name.lower() in {'i', 'me', 'you', 'he', 'she', 'it', 'we', 'they', 
                                      'monday', 'tuesday', 'wednesday', 'thursday', 
                                      'friday', 'saturday', 'sunday'}:
                        continue
                    
                    # Skip already added entities
                    name_lower = name.lower()
                    if any(name_lower == key.lower() for key in entity_map.keys()):
                        continue
                    
                    # Determine confidence based on match quality
                    confidence = 0.7  # Base confidence
                    
                    # Adjust confidence based on capitalization
                    if name[0].isupper():
                        confidence += 0.1
                    
                    # Adjust confidence based on context
                    context_score = self._calculate_context_score(text, match.start(), match.end(), entity_type)
                    confidence += context_score
                    
                    # Create entity
                    entity = Entity(
                        name=name,
                        entity_type=entity_type,
                        confidence=min(confidence, 0.95)  # Cap at 0.95
                    )
                    
                    # Add mention
                    entity.add_mention(text, match.start(), match.end(), confidence)
                    
                    # Add to map
                    entity_map[name_lower] = entity
        
        # Convert map to list and apply min confidence filter
        entities = [entity for entity in entity_map.values() if entity.confidence >= min_confidence]
        
        # Third pass: detect relationships between entities
        if len(entities) >= 2:
            self._detect_relationships(entities, text)
        
        logger.info(f"Extracted {len(entities)} entities using local implementation")
        return entities
    
    def _calculate_context_score(self, text: str, start: int, end: int, entity_type: str) -> float:
        """
        Calculate context-based confidence adjustment.
        
        Args:
            text: Full text
            start: Start position of entity
            end: End position of entity
            entity_type: Proposed entity type
            
        Returns:
            Confidence score adjustment
        """
        # Get context around the entity (up to 50 chars before and after)
        context_start = max(0, start - 50)
        context_end = min(len(text), end + 50)
        context = text[context_start:context_end]
        
        # Define context indicators for each entity type
        type_indicators = {
            EntityType.PERSON: ["who", "he", "she", "born", "died", "wrote", "said"],
            EntityType.ORGANIZATION: ["organization", "company", "founded", "based", "employees", "team"],
            EntityType.LOCATION: ["located", "city", "country", "region", "capital", "north", "south", "east", "west"],
            EntityType.CONCEPT: ["concept", "theory", "idea", "approach", "method", "refers to", "defined as"],
            EntityType.PRODUCT: ["product", "device", "tool", "software", "released", "launched", "version"],
        }
        
        # Check if context contains indicators for the proposed type
        score = 0.0
        indicators = type_indicators.get(entity_type, [])
        for indicator in indicators:
            if indicator.lower() in context.lower():
                score += 0.05
                
        # Check if context contains stronger indicators for other types
        for other_type, other_indicators in type_indicators.items():
            if other_type != entity_type:
                for indicator in other_indicators:
                    if indicator.lower() in context.lower():
                        score -= 0.02
        
        return min(score, 0.2)  # Cap adjustment at 0.2
    
    def _detect_relationships(self, entities: List[Entity], text: str) -> None:
        """
        Detect relationships between entities.
        
        Args:
            entities: List of entities
            text: Original text
        """
        # First pass: detect relationships based on patterns
        for pattern_type, patterns in self._relationship_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        # Extract entity mentions from the pattern match
                        source_text = match.group(1).strip()
                        target_text = match.group(2).strip()
                        
                        # Find matching entities
                        source_entity = None
                        target_entity = None
                        
                        for entity in entities:
                            if (entity.name.lower() in source_text.lower() or 
                                any(alias.lower() in source_text.lower() for alias in entity.aliases)):
                                source_entity = entity
                            
                            if (entity.name.lower() in target_text.lower() or 
                                any(alias.lower() in target_text.lower() for alias in entity.aliases)):
                                target_entity = entity
                        
                        # Create relationship if both entities found
                        if source_entity and target_entity and source_entity != target_entity:
                            confidence = 0.7  # Base confidence
                            
                            # Create relationship
                            source_entity.add_relationship(
                                target_entity_id=target_entity.entity_id,
                                relation_type=pattern_type,
                                confidence=confidence,
                                metadata={"context": match.group(0)}
                            )
                    except (IndexError, AttributeError):
                        continue
        
        # Second pass: detect relationships based on proximity in text
        # This is a fallback for entities that don't have explicit relationship patterns
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i+1:], i+1):
                # Skip if already has relationship
                if any(rel["target_entity_id"] == entity2.entity_id for rel in entity1.relationships):
                    continue
                
                # Check if entities are mentioned close to each other
                # Use the first mention of each entity for simplicity
                if entity1.mentions and entity2.mentions:
                    mention1 = entity1.mentions[0]
                    mention2 = entity2.mentions[0]
                    
                    # Calculate distance between mentions
                    distance = min(
                        abs(mention1["end"] - mention2["start"]),
                        abs(mention2["end"] - mention1["start"])
                    )
                    
                    # If mentions are close, create a generic relationship
                    if distance < 100:  # Arbitrary threshold
                        confidence = max(0.5, 0.8 - (distance / 200))  # Confidence decreases with distance
                        
                        # Extract context around the mentions
                        mention_start = min(mention1["start"], mention2["start"])
                        mention_end = max(mention1["end"], mention2["end"])
                        context_start = max(0, mention_start - 20)
                        context_end = min(len(text), mention_end + 20)
                        context = text[context_start:context_end]
                        
                        # Create relationship
                        entity1.add_relationship(
                            target_entity_id=entity2.entity_id,
                            relation_type=RelationType.RELATED_TO,
                            confidence=confidence,
                            metadata={"context": context, "distance": distance}
                        )
    
    async def disambiguate_entity(self, entity: Entity, context: str) -> Entity:
        """
        Disambiguate an entity using available knowledge bases.
        
        Args:
            entity: Entity to disambiguate
            context: Context text for disambiguation
            
        Returns:
            Disambiguated entity (may be the same entity if no better match found)
        """
        # If already has high confidence, return as is
        if entity.confidence > 0.85:
            return entity
        
        # Try to disambiguate using GraphRAG if available
        if self.graphrag_client:
            try:
                # Construct a query to get information about this entity
                query = f"Tell me about {entity.name}"
                focus_entities = [entity.name]
                
                # Get sources from GraphRAG
                sources, _ = await self.graphrag_client.get_sources_for_query(query, focus_entities)
                
                if sources:
                    # Extract best matching entity from sources
                    best_match = None
                    best_score = 0.0
                    
                    for source in sources:
                        score = source.get("relevance_score", 0.0)
                        if score > best_score:
                            best_score = score
                            
                            # Create an entity from the source
                            metadata = source.get("metadata", {})
                            best_match = Entity(
                                name=entity.name,
                                entity_type=entity.entity_type,
                                description=metadata.get("description", ""),
                                aliases=metadata.get("aliases", []),
                                confidence=min(entity.confidence + 0.1, 0.95),
                                metadata={
                                    "source": "graphrag",
                                    "original_confidence": entity.confidence,
                                    "disambiguation_score": score,
                                    **metadata
                                }
                            )
                    
                    if best_match and best_score > 0.6:
                        # Transfer mentions and relationships from original entity
                        best_match.mentions = entity.mentions
                        best_match.relationships = entity.relationships
                        return best_match
            
            except Exception as e:
                logger.warning(f"Error disambiguating entity using GraphRAG: {e}")
        
        # If GraphRAG disambiguation failed, return original entity
        return entity
        
    async def create_entity_map(self, entities: List[Entity]) -> Dict[str, Dict[str, Any]]:
        """
        Create a visual entity map for UI rendering.
        
        Args:
            entities: List of entities
            
        Returns:
            Entity map with nodes and edges
        """
        # Create nodes
        nodes = []
        for entity in entities:
            node = {
                "id": entity.entity_id,
                "label": entity.name,
                "type": entity.entity_type,
                "confidence": entity.confidence,
                "data": {
                    "description": entity.description,
                    "aliases": entity.aliases,
                    "metadata": entity.metadata
                }
            }
            nodes.append(node)
        
        # Create edges
        edges = []
        for entity in entities:
            for relationship in entity.relationships:
                edge = {
                    "id": relationship["relationship_id"],
                    "source": relationship["source_entity_id"],
                    "target": relationship["target_entity_id"],
                    "label": relationship["relation_type"],
                    "type": relationship["relation_type"],
                    "confidence": relationship["confidence"],
                    "data": relationship["metadata"]
                }
                edges.append(edge)
        
        return {
            "nodes": nodes,
            "edges": edges
        }


# Singleton instance
_entity_linker = None


def get_entity_linker(graphrag_client: Optional[GraphRAGClient] = None) -> EntityLinker:
    """
    Get the global entity linker instance.
    
    Args:
        graphrag_client: Optional GraphRAG client to use
        
    Returns:
        EntityLinker instance
    """
    global _entity_linker
    if _entity_linker is None:
        _entity_linker = EntityLinker(graphrag_client)
    return _entity_linker