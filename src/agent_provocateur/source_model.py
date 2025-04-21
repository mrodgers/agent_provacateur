"""
Source attribution models for GraphRAG integration.

This module defines the data models for source attribution using GraphRAG.
"""

from typing import Any, Dict, List, Optional, Union, Tuple
from pydantic import BaseModel, Field, validator
import datetime
import uuid
from enum import Enum
from agent_provocateur.models import Source, SourceType

class EntityType(str, Enum):
    """Types of entities for knowledge graph."""
    
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


class EntityMention(BaseModel):
    """Model for an entity mention in text."""
    
    start: int = Field(..., description="Start character position")
    end: int = Field(..., description="End character position")
    text: str = Field(..., description="Text of the mention")


class Entity(BaseModel):
    """Model for a knowledge graph entity."""
    
    entity_id: str = Field(..., description="Unique identifier for the entity")
    entity_type: EntityType = Field(..., description="Type of entity")
    name: str = Field(..., description="Primary name of the entity")
    aliases: List[str] = Field(default_factory=list, description="Alternative names")
    description: Optional[str] = Field(None, description="Entity description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @classmethod
    def create(cls, name: str, entity_type: Union[str, EntityType], description: Optional[str] = None) -> "Entity":
        """
        Create a new entity with a generated ID.
        
        Args:
            name: Primary name of the entity
            entity_type: Type of entity
            description: Optional description
            
        Returns:
            New Entity instance
        """
        if isinstance(entity_type, str):
            try:
                entity_type = EntityType(entity_type.lower())
            except ValueError:
                entity_type = EntityType.OTHER
                
        return cls(
            entity_id=f"ent_{uuid.uuid4().hex[:8]}",
            entity_type=entity_type,
            name=name,
            description=description or "",
        )


class EntityMention(BaseModel):
    """Model for an entity mention in text."""
    
    entity_id: str = Field(..., description="Entity ID")
    entity_type: EntityType = Field(..., description="Entity type")
    mentions: List[Dict[str, Any]] = Field(default_factory=list, 
                                         description="Text positions where entity is mentioned")


class RelationType(str, Enum):
    """Types of relationships between entities."""
    
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


class Relationship(BaseModel):
    """Model for a relationship between entities."""
    
    relationship_id: str = Field(..., description="Unique identifier for the relationship")
    source_entity_id: str = Field(..., description="Source entity ID")
    target_entity_id: str = Field(..., description="Target entity ID")
    relation_type: RelationType = Field(..., description="Type of relationship")
    confidence: float = Field(1.0, description="Confidence score (0.0-1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @classmethod
    def create(cls, source_id: str, target_id: str, 
               relation_type: Union[str, RelationType],
               confidence: float = 1.0) -> "Relationship":
        """
        Create a new relationship with a generated ID.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relation_type: Type of relationship
            confidence: Confidence score
            
        Returns:
            New Relationship instance
        """
        if isinstance(relation_type, str):
            try:
                relation_type = RelationType(relation_type.lower())
            except ValueError:
                relation_type = RelationType.OTHER
                
        return cls(
            relationship_id=f"rel_{uuid.uuid4().hex[:8]}",
            source_entity_id=source_id,
            target_entity_id=target_id,
            relation_type=relation_type,
            confidence=confidence
        )


class EnhancedSource(BaseModel):
    """Enhanced source model with GraphRAG integration."""
    
    # Base source fields
    source_id: str = Field(..., description="Unique identifier for the source")
    source_type: SourceType = Field(..., description="Type of source")
    title: str = Field(..., description="Title or name of the source")
    content: str = Field(..., description="Full content of the source")
    url: Optional[str] = Field(None, description="URL to the source (if applicable)")
    authors: List[str] = Field(default_factory=list, description="Authors of the source")
    publication_date: Optional[datetime.datetime] = Field(None, description="Publication date")
    retrieval_date: datetime.datetime = Field(default_factory=datetime.datetime.now, 
                                             description="Timestamp when the source was retrieved")
    
    # Quality metrics
    confidence_score: float = Field(0.5, description="Confidence score (0.0-1.0)")
    reliability_score: float = Field(0.5, description="Reliability score (0.0-1.0)")
    
    # Entity and relationship data
    entity_mentions: List[EntityMention] = Field(default_factory=list, 
                                               description="Entities mentioned in the source")
    relationships: List[Dict[str, Any]] = Field(default_factory=list, 
                                              description="Entity relationships from source")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime.datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_source(cls, source: Source, content: str) -> "EnhancedSource":
        """
        Create an EnhancedSource from a basic Source.
        
        Args:
            source: Basic Source object
            content: Full content of the source
            
        Returns:
            Enhanced source with GraphRAG-compatible fields
        """
        return cls(
            source_id=source.source_id,
            source_type=source.source_type,
            title=source.title,
            content=content,
            url=source.url,
            authors=source.metadata.get("authors", []),
            publication_date=source.metadata.get("publication_date"),
            retrieval_date=source.retrieved_at or datetime.datetime.now(),
            confidence_score=source.confidence,
            reliability_score=source.metadata.get("reliability_score", 0.5),
            metadata={k: v for k, v in source.metadata.items() 
                     if k not in ["authors", "publication_date", "reliability_score"]}
        )
    
    def to_source(self) -> Source:
        """
        Convert to a basic Source object.
        
        Returns:
            Basic Source object
        """
        metadata = dict(self.metadata)
        
        if self.authors:
            metadata["authors"] = self.authors
            
        if self.publication_date:
            metadata["publication_date"] = self.publication_date
            
        if self.reliability_score is not None:
            metadata["reliability_score"] = self.reliability_score
            
        return Source(
            source_id=self.source_id,
            source_type=self.source_type,
            title=self.title,
            url=self.url,
            retrieved_at=self.retrieval_date,
            confidence=self.confidence_score,
            metadata=metadata
        )


class AttributionResult(BaseModel):
    """Model for source attribution results."""
    
    text: str = Field(..., description="Original text")
    sources: List[Dict[str, Any]] = Field(..., description="Attributed sources")
    confidence: float = Field(..., description="Overall confidence score")
    explanation: Optional[str] = Field(None, description="Explanation of attribution")


class KnowledgeGraphNode(BaseModel):
    """Model for a node in the knowledge graph."""
    
    id: str = Field(..., description="Node ID")
    label: str = Field(..., description="Node label")
    type: str = Field(..., description="Node type")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")


class KnowledgeGraphEdge(BaseModel):
    """Model for an edge in the knowledge graph."""
    
    id: str = Field(..., description="Edge ID")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: str = Field(..., description="Edge label")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge properties")


class KnowledgeGraph(BaseModel):
    """Model for the complete knowledge graph."""
    
    nodes: List[KnowledgeGraphNode] = Field(..., description="Graph nodes")
    edges: List[KnowledgeGraphEdge] = Field(..., description="Graph edges")