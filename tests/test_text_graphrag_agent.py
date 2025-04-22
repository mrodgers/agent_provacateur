"""Tests for the Text GraphRAG agent with markdown and text document support."""

import os
import asyncio
import pytest
import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from agent_provocateur.text_graphrag_agent import TextGraphRAGAgent
from agent_provocateur.a2a_models import TaskRequest, TaskResult, TaskStatus
from agent_provocateur.graphrag_client import GraphRAGClient
from agent_provocateur.entity_linking import Entity, EntityType, RelationType
from agent_provocateur.models import Document, DocumentContent


@pytest.fixture
def sample_markdown():
    """Sample markdown content for testing."""
    return """# Artificial Intelligence and Climate Change

## Introduction

Artificial Intelligence (AI) is changing how we interact with technology. 
Companies like OpenAI and Google are leading the development of large language models.

The United Nations has discussed the potential impacts of AI on society and economics.
Dr. Geoffrey Hinton, who worked for Google, is known as one of the godfathers of AI.

## Recent Developments

In 2022, OpenAI released ChatGPT which gained over 100 million users within two months.
This tool is part of a broader trend in generative AI technology.

## Climate Change Connections

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
            "name": "Climate Change",
            "entity_type": "concept",
            "entity_id": "ent_cc789012",
            "description": "Long-term change in Earth's climate patterns",
            "confidence": 0.85,
            "metadata": {"source": "graphrag"}
        }
    ]
    
    # Setup mock index_text_document method
    client.index_text_document.return_value = "doc_markdown_123"
    
    return client


@pytest.fixture
def text_graphrag_agent():
    """Create a Text GraphRAG agent for testing."""
    # Create agent with mocked dependencies
    agent = TextGraphRAGAgent("test_text_graphrag_agent")
    
    # Mock messaging
    agent.messaging = MagicMock()
    agent.messaging.send_task_result = MagicMock()
    
    return agent


@pytest.mark.asyncio
async def test_on_startup(text_graphrag_agent):
    """Test agent initialization and startup."""
    # Mock GraphRAG client creation
    with patch("agent_provocateur.text_graphrag_agent.GraphRAGClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Set environment variable
        with patch.dict("os.environ", {"GRAPHRAG_MCP_URL": "http://test-graphrag:8083"}):
            await text_graphrag_agent.on_startup()
        
        # Verify GraphRAG client was initialized
        mock_client_class.assert_called_once_with(base_url="http://test-graphrag:8083")
        
        # Verify entity linker was initialized
        assert text_graphrag_agent.entity_linker is not None
        assert hasattr(text_graphrag_agent, "extracted_entities")


@pytest.mark.asyncio
async def test_index_text_document(text_graphrag_agent, mock_graphrag_client, sample_markdown):
    """Test indexing a text document."""
    # Setup agent with mock GraphRAG client
    text_graphrag_agent.graphrag_client = mock_graphrag_client
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_index_doc",
        source_agent="test_agent",
        target_agent="test_text_graphrag_agent",
        intent="index_text_document",
        payload={
            "content": sample_markdown,
            "title": "AI and Climate Change",
            "doc_type": "markdown",
            "metadata": {
                "author": "Test Author",
                "tags": ["AI", "climate"]
            }
        }
    )
    
    # Call the handler
    result = await text_graphrag_agent.handle_index_text_document(task_request)
    
    # Verify results
    assert result["success"] is True
    assert result["doc_id"] == "doc_markdown_123"
    assert "Successfully indexed" in result["message"]
    
    # Verify client was called with correct parameters
    mock_graphrag_client.index_text_document.assert_called_once_with(
        content=sample_markdown,
        title="AI and Climate Change",
        doc_type="markdown",
        metadata={
            "author": "Test Author",
            "tags": ["AI", "climate"]
        }
    )


@pytest.mark.asyncio
async def test_extract_entities(text_graphrag_agent, mock_graphrag_client, sample_markdown):
    """Test extracting entities from text document."""
    # Setup agent with mock GraphRAG client
    text_graphrag_agent.graphrag_client = mock_graphrag_client
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_extract_entities",
        source_agent="test_agent",
        target_agent="test_text_graphrag_agent",
        intent="extract_entities",
        payload={
            "content": sample_markdown,
            "use_graphrag": True
        }
    )
    
    # Call the handler
    result = await text_graphrag_agent.handle_extract_entities(task_request)
    
    # Verify results
    assert "entities" in result
    assert result["entity_count"] == 2
    assert result["extraction_method"] == "graphrag_mcp"
    
    # Verify entity details
    entity_names = [entity["name"] for entity in result["entities"]]
    assert "Artificial Intelligence" in entity_names
    assert "Climate Change" in entity_names


@pytest.mark.asyncio
async def test_extract_enhanced_entities(text_graphrag_agent, sample_markdown):
    """Test enhanced entity extraction with relationships."""
    # Create entity linker mock
    entity_linker = AsyncMock()
    text_graphrag_agent.entity_linker = entity_linker
    
    # Create sample entities for mocking
    entities = [
        Entity(
            name="Artificial Intelligence",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ai123",
            aliases=["AI"],
            confidence=0.9
        ),
        Entity(
            name="Climate Change",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_cc456",
            confidence=0.85
        ),
        Entity(
            name="OpenAI",
            entity_type=EntityType.ORGANIZATION,
            entity_id="entity_oa789",
            confidence=0.8
        )
    ]
    
    # Add relationships
    entities[0].add_relationship(
        target_entity_id=entities[1].entity_id,
        relation_type=RelationType.RELATED_TO
    )
    entities[2].add_relationship(
        target_entity_id=entities[0].entity_id,
        relation_type=RelationType.CREATED_BY
    )
    
    # Setup mock extract_entities_from_text return value
    entity_linker.extract_entities_from_text.return_value = entities
    
    # Setup mock disambiguate_entity to return same entity
    entity_linker.disambiguate_entity.side_effect = lambda entity, _: entity
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_extract_enhanced",
        source_agent="test_agent",
        target_agent="test_text_graphrag_agent",
        intent="extract_enhanced_entities",
        payload={
            "content": sample_markdown,
            "min_confidence": 0.7
        }
    )
    
    # Call the handler
    result = await text_graphrag_agent.handle_extract_enhanced_entities(task_request)
    
    # Verify results
    assert result["status"] == "success"
    assert result["entity_count"] == 3
    assert result["relationship_count"] == 2
    
    # Verify entities_by_type
    assert EntityType.CONCEPT in result["entities_by_type"]
    assert EntityType.ORGANIZATION in result["entities_by_type"]
    assert len(result["entities_by_type"][EntityType.CONCEPT]) == 2
    
    # Verify entity linker methods were called
    entity_linker.extract_entities_from_text.assert_called_once()
    assert entity_linker.disambiguate_entity.call_count == 3


@pytest.mark.asyncio
async def test_analyze_entity_relationships(text_graphrag_agent):
    """Test analyzing entity relationships."""
    # Setup entity objects
    entities = [
        Entity(
            name="Artificial Intelligence",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ai123",
            confidence=0.9
        ),
        Entity(
            name="Machine Learning",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ml456",
            confidence=0.85
        ),
        Entity(
            name="OpenAI",
            entity_type=EntityType.ORGANIZATION,
            entity_id="entity_oa789",
            confidence=0.8
        )
    ]
    
    # Add relationships
    entities[0].add_relationship(
        target_entity_id=entities[1].entity_id,
        relation_type=RelationType.HAS_PART
    )
    entities[2].add_relationship(
        target_entity_id=entities[0].entity_id,
        relation_type=RelationType.RELATED_TO
    )
    
    # Store entities
    text_graphrag_agent.extracted_entities = {entity.entity_id: entity for entity in entities}
    text_graphrag_agent.entity_clusters = []
    
    # Mock entity linker create_entity_map
    entity_linker = AsyncMock()
    text_graphrag_agent.entity_linker = entity_linker
    entity_linker.create_entity_map.return_value = {
        "nodes": ["node1", "node2", "node3"],
        "edges": ["edge1", "edge2"]
    }
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_analyze_relationships",
        source_agent="test_agent",
        target_agent="test_text_graphrag_agent",
        intent="analyze_entity_relationships",
        payload={}  # Empty payload to use all entities
    )
    
    # Call the handler
    result = await text_graphrag_agent.handle_analyze_entity_relationships(task_request)
    
    # Verify results
    assert result["status"] == "success"
    assert result["entity_count"] == 3
    assert result["relationship_count"] == 2
    
    # Verify relationship types
    assert RelationType.HAS_PART in result["relationship_types"]
    assert RelationType.RELATED_TO in result["relationship_types"]
    
    # Verify entity map was generated
    assert "relationship_map" in result
    assert result["relationship_map"]["nodes"] == ["node1", "node2", "node3"]


@pytest.mark.asyncio
async def test_generate_entity_map(text_graphrag_agent):
    """Test entity map generation."""
    # Setup entity objects
    entities = [
        Entity(
            name="Artificial Intelligence",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ai123",
            confidence=0.9
        ),
        Entity(
            name="Machine Learning",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ml456",
            confidence=0.85
        ),
        Entity(
            name="Climate Change",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_cc789",
            confidence=0.8
        )
    ]
    
    # Add relationships
    entities[0].add_relationship(
        target_entity_id=entities[1].entity_id,
        relation_type=RelationType.HAS_PART
    )
    
    # Store entities
    text_graphrag_agent.extracted_entities = {entity.entity_id: entity for entity in entities}
    text_graphrag_agent.entity_clusters = []
    
    # Mock entity linker create_entity_map
    entity_linker = AsyncMock()
    text_graphrag_agent.entity_linker = entity_linker
    entity_linker.create_entity_map.return_value = {
        "nodes": [
            {"id": "entity_ai123", "label": "Artificial Intelligence"},
            {"id": "entity_ml456", "label": "Machine Learning"}
        ],
        "edges": [
            {"id": "rel1", "source": "entity_ai123", "target": "entity_ml456"}
        ]
    }
    
    # Create task request with specific entity IDs
    task_request = TaskRequest(
        task_id="test_generate_map",
        source_agent="test_agent",
        target_agent="test_text_graphrag_agent",
        intent="generate_entity_map",
        payload={
            "entity_ids": ["entity_ai123", "entity_ml456"]
        }
    )
    
    # Call the handler
    result = await text_graphrag_agent.handle_generate_entity_map(task_request)
    
    # Verify results
    assert result["status"] == "success"
    assert result["node_count"] == 2
    assert result["edge_count"] == 1
    
    # Verify entity map
    assert "entity_map" in result
    assert len(result["entity_map"]["nodes"]) == 2
    assert len(result["entity_map"]["edges"]) == 1