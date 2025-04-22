"""Tests for the enhanced entity linking capabilities."""

import asyncio
import pytest
import os
import json
from unittest.mock import AsyncMock, MagicMock, patch

from agent_provocateur.entity_linking import (
    EntityLinker, Entity, Relationship, EntityType, RelationType, get_entity_linker
)
from agent_provocateur.graphrag_client import GraphRAGClient


@pytest.fixture
def sample_text():
    """Sample text for entity extraction testing."""
    return """
    Artificial Intelligence (AI) is changing how we interact with technology. 
    Companies like OpenAI and Google are leading the development of large language models.
    
    The United Nations has discussed the potential impacts of AI on society and economics.
    Dr. Geoffrey Hinton, who worked for Google, is known as one of the godfathers of AI.
    
    In 2022, OpenAI released ChatGPT which gained over 100 million users within two months.
    This tool is part of a broader trend in generative AI technology.
    
    Climate change remains a significant global challenge. The Paris Agreement, signed in 2015,
    is an international treaty addressing this issue. The United States rejoined the agreement in 2021.
    """


@pytest.fixture
def mock_graphrag_client():
    """Create a mock GraphRAG client."""
    client = AsyncMock(spec=GraphRAGClient)
    
    # Setup mock extract_entities method
    client.extract_entities.return_value = [
        {
            "name": "Artificial Intelligence",
            "entity_type": "concept",
            "entity_id": "ent_ai123456",
            "description": "The simulation of human intelligence in machines",
            "aliases": ["AI", "machine intelligence"],
            "confidence": 0.9,
            "metadata": {"source": "graphrag"}
        },
        {
            "name": "OpenAI",
            "entity_type": "organization",
            "entity_id": "ent_openai12",
            "description": "AI research laboratory",
            "confidence": 0.85,
            "metadata": {"source": "graphrag"}
        }
    ]
    
    # Setup mock get_sources_for_query method
    client.get_sources_for_query.return_value = (
        [
            {
                "content": "OpenAI is an AI research laboratory consisting of the for-profit Corporation OpenAI LP and its parent company, the non-profit OpenAI Inc.",
                "relevance_score": 0.85,
                "metadata": {
                    "title": "About OpenAI",
                    "description": "AI research laboratory based in San Francisco",
                    "url": "https://example.com/openai",
                    "source_type": "web"
                }
            }
        ],
        "OpenAI is an AI research company..."
    )
    
    return client


@pytest.fixture
def large_sample_text():
    """Large sample text to test performance with many entities."""
    # Create a text with many repeated entity mentions to test performance
    base_text = """
    Artificial Intelligence research has seen significant advancements in recent years.
    Companies like Microsoft, Google, OpenAI, Meta, and Apple are investing heavily.
    
    The European Union has established regulations around AI development.
    China, the United States, and India are competing for AI supremacy.
    
    Researchers such as Dr. Geoffrey Hinton, Dr. Yoshua Bengio, and Dr. Yann LeCun
    have made fundamental contributions to deep learning techniques.
    
    Climate change continues to affect global weather patterns, with the
    Paris Agreement providing a framework for international cooperation.
    """
    # Repeat the text to create a larger document with many entity mentions
    return base_text * 20


@pytest.fixture
def special_characters_text():
    """Text with special characters and unusual formatting."""
    return """
    Künstliche Intelligenz (AI) ist ein wichtiges Forschungsgebiet. 
    Firmen wie OpenAI™ und Google® entwickeln neue Technologien.
    
    La inteligencia artificial está cambiando el mundo. Apple Inc. y Microsoft Corp.
    son líderes en este campo.
    
    AI研究は急速に進歩しています。テスラとユニクロが新技術に投資しています。
    
    The United Nations' report on AI safety contains {special} [characters] and <tags>.
    
    C++ and Python* are popular programming^2 languages@development.
    
    Multiple     spaces   and\ttabs\tare\tincluded      here.
    """


@pytest.fixture
def error_producing_graphrag_client():
    """Create a mock GraphRAG client that raises errors."""
    client = AsyncMock(spec=GraphRAGClient)
    
    # Setup mock extract_entities method to raise an exception
    client.extract_entities.side_effect = Exception("GraphRAG service unavailable")
    
    # Setup mock get_sources_for_query method to raise an exception
    client.get_sources_for_query.side_effect = Exception("Failed to retrieve sources")
    
    return client


@pytest.fixture
def empty_results_graphrag_client():
    """Create a mock GraphRAG client that returns empty results."""
    client = AsyncMock(spec=GraphRAGClient)
    
    # Setup mock extract_entities method to return empty list
    client.extract_entities.return_value = []
    
    # Setup mock get_sources_for_query method to return empty results
    client.get_sources_for_query.return_value = ([], "")
    
    return client


class TestEntityLinking:
    """Test entity linking capabilities."""
    
    @pytest.mark.asyncio
    async def test_extract_entities_local(self, sample_text):
        """Test extracting entities using local implementation."""
        # Create entity linker without GraphRAG client
        linker = EntityLinker()
        
        # Extract entities
        entities = await linker.extract_entities_from_text(sample_text)
        
        # Verify results
        assert len(entities) > 5  # Should extract multiple entities
        
        # Check for specific entities
        entity_names = [entity.name.lower() for entity in entities]
        assert "artificial intelligence" in [name.lower() for name in entity_names]
        assert "openai" in [name.lower() for name in entity_names]
        assert "google" in [name.lower() for name in entity_names]
        assert "united nations" in [name.lower() for name in entity_names]
        
        # Check entity types
        ai_entity = next((e for e in entities if e.name.lower() == "artificial intelligence"), None)
        assert ai_entity is not None
        assert ai_entity.entity_type == EntityType.CONCEPT
        
        # Check for mentions
        assert len(ai_entity.mentions) > 0
        
        # Check for relationships
        all_relationships = []
        for entity in entities:
            all_relationships.extend(entity.relationships)
        
        assert len(all_relationships) > 0
    
    @pytest.mark.asyncio
    async def test_extract_entities_graphrag(self, sample_text, mock_graphrag_client):
        """Test extracting entities using GraphRAG client."""
        # Create entity linker with mock GraphRAG client
        linker = EntityLinker(mock_graphrag_client)
        
        # Extract entities
        entities = await linker.extract_entities_from_text(sample_text)
        
        # Verify results
        assert len(entities) == 2  # Should get the mocked entities
        
        # Check for specific entities
        entity_names = [entity.name for entity in entities]
        assert "Artificial Intelligence" in entity_names
        assert "OpenAI" in entity_names
        
        # Check entity types
        ai_entity = next(e for e in entities if e.name == "Artificial Intelligence")
        assert ai_entity.entity_type == "concept"
        assert ai_entity.entity_id == "ent_ai123456"
        
        # Verify mock was called with correct parameters
        mock_graphrag_client.extract_entities.assert_called_once_with(sample_text, {})
    
    @pytest.mark.asyncio
    async def test_disambiguate_entity(self, mock_graphrag_client):
        """Test entity disambiguation with GraphRAG."""
        # Create entity linker with mock GraphRAG client
        linker = EntityLinker(mock_graphrag_client)
        
        # Create entity to disambiguate
        entity = Entity(
            name="OpenAI",
            entity_type=EntityType.ORGANIZATION,
            confidence=0.7  # Low enough to trigger disambiguation
        )
        
        # Add some mentions
        entity.add_mention("OpenAI is a company", 0, 6)
        
        # Disambiguate
        context = "OpenAI is a leading AI research company."
        disambiguated = await linker.disambiguate_entity(entity, context)
        
        # Verify results
        assert disambiguated.confidence > entity.confidence
        assert "disambiguation_score" in disambiguated.metadata
        assert disambiguated.metadata.get("source") == "graphrag"
        
        # Check that mentions were preserved
        assert len(disambiguated.mentions) == len(entity.mentions)
        
        # Verify mock was called with correct parameters
        mock_graphrag_client.get_sources_for_query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_entity_map(self):
        """Test creating entity map for visualization."""
        # Create some entities with relationships
        entity1 = Entity(
            name="Artificial Intelligence",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ai123"
        )
        
        entity2 = Entity(
            name="Machine Learning",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ml456"
        )
        
        entity3 = Entity(
            name="OpenAI",
            entity_type=EntityType.ORGANIZATION,
            entity_id="entity_openai789"
        )
        
        # Add relationships
        entity1.add_relationship(
            target_entity_id=entity2.entity_id,
            relation_type=RelationType.HAS_PART
        )
        
        entity3.add_relationship(
            target_entity_id=entity1.entity_id,
            relation_type=RelationType.CREATED_BY
        )
        
        # Create entity linker
        linker = EntityLinker()
        
        # Create entity map
        entity_map = await linker.create_entity_map([entity1, entity2, entity3])
        
        # Verify results
        assert "nodes" in entity_map
        assert "edges" in entity_map
        
        assert len(entity_map["nodes"]) == 3
        assert len(entity_map["edges"]) == 2
        
        # Check node structure
        for node in entity_map["nodes"]:
            assert "id" in node
            assert "label" in node
            assert "type" in node
            assert "data" in node
        
        # Check edge structure
        for edge in entity_map["edges"]:
            assert "id" in edge
            assert "source" in edge
            assert "target" in edge
            assert "label" in edge
            assert "type" in edge
    
    def test_singleton_instance(self, mock_graphrag_client):
        """Test the singleton pattern for entity linker."""
        # Get instance with client
        linker1 = get_entity_linker(mock_graphrag_client)
        
        # Get another instance
        linker2 = get_entity_linker()
        
        # Should be the same instance
        assert linker1 is linker2
        assert linker1.graphrag_client is mock_graphrag_client


class TestEntity:
    """Test Entity class functionality."""
    
    def test_entity_creation(self):
        """Test creating an entity."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.CONCEPT,
            description="Test description",
            aliases=["TE", "Test"],
            confidence=0.8
        )
        
        assert entity.name == "Test Entity"
        assert entity.entity_type == EntityType.CONCEPT
        assert entity.description == "Test description"
        assert "TE" in entity.aliases
        assert entity.confidence == 0.8
        assert len(entity.mentions) == 0
        assert len(entity.relationships) == 0
    
    def test_entity_to_dict(self):
        """Test converting entity to dictionary."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_test123",
            description="Test description",
            aliases=["TE", "Test"],
            confidence=0.8
        )
        
        entity_dict = entity.to_dict()
        
        assert entity_dict["entity_id"] == "entity_test123"
        assert entity_dict["name"] == "Test Entity"
        assert entity_dict["entity_type"] == EntityType.CONCEPT
        assert entity_dict["description"] == "Test description"
        assert entity_dict["aliases"] == ["TE", "Test"]
        assert entity_dict["confidence"] == 0.8
        assert "mentions" in entity_dict
        assert "relationships" in entity_dict
    
    def test_entity_from_dict(self):
        """Test creating entity from dictionary."""
        entity_dict = {
            "entity_id": "entity_test123",
            "name": "Test Entity",
            "entity_type": EntityType.CONCEPT,
            "description": "Test description",
            "aliases": ["TE", "Test"],
            "confidence": 0.8,
            "mentions": [{"text": "Test", "start": 0, "end": 4, "score": 0.9}],
            "relationships": []
        }
        
        entity = Entity.from_dict(entity_dict)
        
        assert entity.entity_id == "entity_test123"
        assert entity.name == "Test Entity"
        assert entity.entity_type == EntityType.CONCEPT
        assert entity.description == "Test description"
        assert entity.aliases == ["TE", "Test"]
        assert entity.confidence == 0.8
        assert len(entity.mentions) == 1
        assert entity.mentions[0]["text"] == "Test"
    
    def test_add_mention(self):
        """Test adding mention to entity."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.CONCEPT
        )
        
        text = "This is a Test Entity example."
        entity.add_mention(text, 10, 21, 0.9)
        
        assert len(entity.mentions) == 1
        assert entity.mentions[0]["text"] == "Test Entity"
        assert entity.mentions[0]["start"] == 10
        assert entity.mentions[0]["end"] == 21
        assert entity.mentions[0]["score"] == 0.9
    
    def test_add_relationship(self):
        """Test adding relationship to entity."""
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_test123"
        )
        
        target_id = "entity_target456"
        entity.add_relationship(
            target_entity_id=target_id,
            relation_type=RelationType.IS_A,
            confidence=0.85,
            metadata={"notes": "Test relationship"}
        )
        
        assert len(entity.relationships) == 1
        relationship = entity.relationships[0]
        assert relationship["source_entity_id"] == "entity_test123"
        assert relationship["target_entity_id"] == target_id
        assert relationship["relation_type"] == RelationType.IS_A
        assert relationship["confidence"] == 0.85
        assert relationship["metadata"]["notes"] == "Test relationship"


class TestRelationship:
    """Test Relationship class functionality."""
    
    def test_relationship_creation(self):
        """Test creating a relationship."""
        relationship = Relationship(
            source_entity_id="entity_source",
            target_entity_id="entity_target",
            relation_type=RelationType.SUPPORTS,
            confidence=0.8,
            bidirectional=True,
            context="Source supports target",
            metadata={"notes": "Important relationship"}
        )
        
        assert relationship.source_entity_id == "entity_source"
        assert relationship.target_entity_id == "entity_target"
        assert relationship.relation_type == RelationType.SUPPORTS
        assert relationship.confidence == 0.8
        assert relationship.bidirectional is True
        assert relationship.context == "Source supports target"
        assert relationship.metadata["notes"] == "Important relationship"
    
    def test_relationship_to_dict(self):
        """Test converting relationship to dictionary."""
        relationship = Relationship(
            relationship_id="rel_test123",
            source_entity_id="entity_source",
            target_entity_id="entity_target",
            relation_type=RelationType.SUPPORTS,
            confidence=0.8,
            bidirectional=True,
            context="Source supports target"
        )
        
        rel_dict = relationship.to_dict()
        
        assert rel_dict["relationship_id"] == "rel_test123"
        assert rel_dict["source_entity_id"] == "entity_source"
        assert rel_dict["target_entity_id"] == "entity_target"
        assert rel_dict["relation_type"] == RelationType.SUPPORTS
        assert rel_dict["confidence"] == 0.8
        assert rel_dict["bidirectional"] is True
        assert rel_dict["context"] == "Source supports target"
    
    def test_relationship_from_dict(self):
        """Test creating relationship from dictionary."""
        rel_dict = {
            "relationship_id": "rel_test123",
            "source_entity_id": "entity_source",
            "target_entity_id": "entity_target",
            "relation_type": RelationType.SUPPORTS,
            "confidence": 0.8,
            "bidirectional": True,
            "context": "Source supports target",
            "metadata": {"notes": "Important relationship"}
        }
        
        relationship = Relationship.from_dict(rel_dict)
        
        assert relationship.relationship_id == "rel_test123"
        assert relationship.source_entity_id == "entity_source"
        assert relationship.target_entity_id == "entity_target"
        assert relationship.relation_type == RelationType.SUPPORTS
        assert relationship.confidence == 0.8
        assert relationship.bidirectional is True
        assert relationship.context == "Source supports target"
        assert relationship.metadata["notes"] == "Important relationship"


class TestErrorHandling:
    """Test error handling and edge cases in entity linking."""
    
    @pytest.mark.asyncio
    async def test_graphrag_client_error(self, sample_text, error_producing_graphrag_client):
        """Test graceful handling of GraphRAG client errors."""
        # Create entity linker with mock GraphRAG client that raises errors
        linker = EntityLinker(error_producing_graphrag_client)
        
        # Should fall back to local extraction when GraphRAG fails
        entities = await linker.extract_entities_from_text(sample_text)
        
        # Verify local extraction still works
        assert len(entities) > 5
        entity_names = [entity.name.lower() for entity in entities]
        assert "artificial intelligence" in [name.lower() for name in entity_names]
        assert "openai" in [name.lower() for name in entity_names]
    
    @pytest.mark.asyncio
    async def test_empty_text_handling(self):
        """Test handling of empty or null input text."""
        linker = EntityLinker()
        
        # Test with empty string
        entities = await linker.extract_entities_from_text("")
        assert entities == []
        
        # Test with None input
        entities = await linker.extract_entities_from_text(None)
        assert entities == []
        
        # Test with whitespace only
        entities = await linker.extract_entities_from_text("   \n   \t   ")
        assert entities == []
    
    @pytest.mark.asyncio
    async def test_empty_graphrag_results(self, sample_text, empty_results_graphrag_client):
        """Test handling of empty results from GraphRAG client."""
        # Create entity linker with mock GraphRAG client that returns empty results
        linker = EntityLinker(empty_results_graphrag_client)
        
        # Should fall back to local extraction when GraphRAG returns no entities
        entities = await linker.extract_entities_from_text(sample_text)
        
        # Verify local extraction still works
        assert len(entities) > 5
        
        # Try disambiguation with empty sources
        entity = Entity(
            name="Test Entity",
            entity_type=EntityType.CONCEPT,
            confidence=0.6  # Low enough to trigger disambiguation
        )
        
        # Should return original entity when disambiguation fails
        disambiguated = await linker.disambiguate_entity(entity, "Test context")
        assert disambiguated.entity_id == entity.entity_id
        assert disambiguated.confidence == entity.confidence
    
    @pytest.mark.asyncio
    async def test_special_characters(self, special_characters_text):
        """Test entity extraction with special characters and multiple languages."""
        linker = EntityLinker()
        entities = await linker.extract_entities_from_text(special_characters_text)
        
        # Should extract entities despite special characters
        assert len(entities) > 0
        
        # Check for some expected entities
        entity_names = [entity.name.lower() for entity in entities]
        expected_entities = ["ai", "openai", "google", "apple", "microsoft"]
        
        # At least some of the expected entities should be found
        assert any(expected in entity_names for expected in expected_entities)
        
        # Verify no exceptions were raised with special characters
        try:
            # Try creating relationship with special characters
            if len(entities) >= 2:
                entities[0].add_relationship(
                    target_entity_id=entities[1].entity_id,
                    relation_type=RelationType.RELATED_TO,
                    metadata={"context": special_characters_text[:50]}
                )
        except Exception as e:
            pytest.fail(f"Exception raised with special characters: {e}")
    
    @pytest.mark.asyncio
    async def test_large_document_handling(self, large_sample_text):
        """Test handling of large documents with many entities."""
        linker = EntityLinker()
        
        # Extract entities from large text
        entities = await linker.extract_entities_from_text(large_sample_text)
        
        # Should extract multiple entities
        assert len(entities) > 10
        
        # Check for expected entities
        entity_names = [entity.name.lower() for entity in entities]
        assert "artificial intelligence" in [name.lower() for name in entity_names]
        
        # Check for duplicates - entities should be deduplicated
        unique_entity_names = set(entity_names)
        assert len(unique_entity_names) == len(entity_names)
        
        # Generate entity map for large set of entities
        entity_map = await linker.create_entity_map(entities)
        assert "nodes" in entity_map
        assert "edges" in entity_map
        assert len(entity_map["nodes"]) == len(entities)
    
    @pytest.mark.asyncio
    async def test_confidence_thresholds(self, sample_text):
        """Test different confidence thresholds for entity extraction."""
        linker = EntityLinker()
        
        # Test with default threshold
        default_entities = await linker.extract_entities_from_text(sample_text)
        
        # Test with high threshold
        high_threshold_entities = await linker.extract_entities_from_text(
            sample_text, 
            options={"min_confidence": 0.9}
        )
        
        # Test with low threshold
        low_threshold_entities = await linker.extract_entities_from_text(
            sample_text, 
            options={"min_confidence": 0.3}
        )
        
        # Higher threshold should yield fewer or equal number of entities
        assert len(high_threshold_entities) <= len(default_entities)
        
        # Lower threshold should yield more or equal number of entities
        assert len(low_threshold_entities) >= len(default_entities)
        
        # Check that high confidence entities are actually high confidence
        for entity in high_threshold_entities:
            assert entity.confidence >= 0.9
            
        # Check that lower threshold entities have lower confidence allowed
        if len(low_threshold_entities) > len(default_entities):
            # If we have more entities with lower threshold, some must have confidence between 0.3 and default
            lower_confidence_entities = [e for e in low_threshold_entities if e.confidence < 0.5]
            assert len(lower_confidence_entities) > 0