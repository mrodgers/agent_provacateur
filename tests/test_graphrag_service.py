"""
Tests for GraphRAG integration service.
"""

import pytest
import datetime
import uuid
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Import the service and models
from agent_provocateur.graphrag_service import GraphRAGService
from agent_provocateur.source_model import (
    Entity, EntityType, Relationship, RelationType,
    EnhancedSource, AttributionResult
)
from agent_provocateur.models import Source, SourceType

# Sample test data
SAMPLE_SOURCE = Source(
    source_id="test_source_1",
    source_type=SourceType.WEB,
    title="Test Web Source",
    url="https://example.com/test",
    confidence=0.8,
    metadata={
        "authors": ["Test Author"],
        "publication_date": "2025-04-01T10:00:00Z",
        "domain": "example.com"
    }
)

SAMPLE_CONTENT = """
Climate change is a significant challenge facing our planet. Global temperatures have risen by 
approximately 1.1°C since pre-industrial times, leading to various environmental impacts. 
Organizations like the IPCC provide scientific data on climate trends. The Paris Agreement, 
signed in 2015, aims to limit global warming to well below 2°C.
"""

@pytest.fixture
def mock_graphrag_document():
    """Mock GraphRAG document."""
    mock = MagicMock()
    mock.add_entity = MagicMock()
    mock.add_relationship = MagicMock()
    return mock

@pytest.fixture
def mock_graphrag_indexer():
    """Mock GraphRAG indexer."""
    mock = MagicMock()
    mock.add_document = MagicMock(return_value="doc_123")
    return mock

@pytest.fixture
def mock_graphrag_retriever():
    """Mock GraphRAG retriever."""
    mock = MagicMock()
    
    # Create mock retrieval results
    mock_result1 = MagicMock()
    mock_result1.content = "Climate change data shows..."
    mock_result1.metadata = {
        "source_id": "source_1",
        "source_type": "web",
        "title": "Climate Data Source",
        "confidence_score": 0.9
    }
    mock_result1.relevance_score = 0.95
    mock_result1.explanation = "This source directly addresses the query topic"
    mock_result1.entities = ["Climate change", "Temperature rise"]
    
    mock_result2 = MagicMock()
    mock_result2.content = "The Paris Agreement specifies..."
    mock_result2.metadata = {
        "source_id": "source_2",
        "source_type": "document",
        "title": "Paris Agreement Summary",
        "confidence_score": 0.85
    }
    mock_result2.relevance_score = 0.8
    mock_result2.explanation = "This source provides context for the query"
    mock_result2.entities = ["Paris Agreement", "Climate policy"]
    
    # Configure mock retriever
    mock.retrieve = MagicMock(return_value=[mock_result1, mock_result2])
    mock.retrieve_for_entities = MagicMock(return_value=[mock_result1, mock_result2])
    
    return mock

@pytest.fixture
def graphrag_service(mock_graphrag_indexer, mock_graphrag_retriever, mock_graphrag_document):
    """Create a GraphRAG service with mocked components."""
    with patch('agent_provocateur.graphrag_service.GraphRAGIndexer', return_value=mock_graphrag_indexer), \
         patch('agent_provocateur.graphrag_service.GraphRAGRetriever', return_value=mock_graphrag_retriever), \
         patch('agent_provocateur.graphrag_service.GraphRAGDocument') as mock_document_class:
        
        # Configure mock document class to return our mock document
        mock_document_class.return_value = mock_graphrag_document
        
        # Create service
        service = GraphRAGService(config={"test_mode": True})
        yield service

def test_create_enhanced_source():
    """Test creating an enhanced source from a basic source."""
    # Create enhanced source without entity extraction
    service = GraphRAGService()
    
    with patch.object(service, 'extract_entities_from_text', return_value=[]):
        enhanced = service.create_enhanced_source(
            SAMPLE_SOURCE, 
            SAMPLE_CONTENT,
            extract_entities=False
        )
    
    # Verify basic fields were copied correctly
    assert enhanced.source_id == SAMPLE_SOURCE.source_id
    assert enhanced.source_type == SAMPLE_SOURCE.source_type
    assert enhanced.title == SAMPLE_SOURCE.title
    assert enhanced.url == SAMPLE_SOURCE.url
    assert enhanced.confidence_score == SAMPLE_SOURCE.confidence
    assert enhanced.content == SAMPLE_CONTENT
    
    # Verify metadata handling
    assert enhanced.authors == SAMPLE_SOURCE.metadata["authors"]
    assert "domain" in enhanced.metadata

def test_extract_entities():
    """Test entity extraction."""
    service = GraphRAGService()
    
    # Create mock entities
    mock_entities = [
        Entity.create("IPCC", EntityType.ORGANIZATION, "Climate organization"),
        Entity.create("Paris Agreement", EntityType.CONCEPT, "Climate treaty")
    ]
    
    # Test with mocked entity extraction
    with patch.object(service, 'extract_entities_from_text', return_value=mock_entities):
        enhanced = service.create_enhanced_source(
            SAMPLE_SOURCE, 
            SAMPLE_CONTENT,
            extract_entities=True
        )
    
    # Should have entity mentions
    assert len(enhanced.entity_mentions) > 0

def test_index_source(graphrag_service, mock_graphrag_document):
    """Test indexing a source."""
    # Create enhanced source
    enhanced = EnhancedSource.from_source(SAMPLE_SOURCE, SAMPLE_CONTENT)
    
    # Add entity mentions
    from agent_provocateur.source_model import EntityMention
    enhanced.entity_mentions = [
        EntityMention(
            entity_id="ent_123",
            entity_type=EntityType.CONCEPT,
            mentions=[{"start": 0, "end": 13, "text": "Climate change"}]
        )
    ]
    
    # Add relationships
    enhanced.relationships = [
        {
            "source_entity_id": "ent_123",
            "target_entity_id": "ent_456",
            "relation_type": "related_to"
        }
    ]
    
    # Index the source
    doc_id = graphrag_service.index_source(enhanced)
    
    # Verify indexing
    assert doc_id == "doc_123"
    mock_graphrag_document.add_entity.assert_called_once()
    mock_graphrag_document.add_relationship.assert_called_once()

def test_get_sources_for_query(graphrag_service):
    """Test retrieving sources for a query."""
    # Test query-based retrieval
    sources = graphrag_service.get_sources_for_query("What is climate change?")
    
    # Verify results
    assert len(sources) == 2
    assert sources[0]["content"] == "Climate change data shows..."
    assert sources[0]["metadata"]["source_id"] == "source_1"
    assert sources[0]["relevance_score"] == 0.95
    
    # Test entity-focused retrieval
    sources = graphrag_service.get_sources_for_query(
        "What is climate change?",
        focus_entities=["ent_climate"]
    )
    
    # Should use entity-based retrieval
    assert len(sources) == 2

def test_build_attributed_prompt(graphrag_service):
    """Test building an attributed prompt."""
    # Create mock sources
    sources = [
        {
            "content": "Climate change is a major issue.",
            "metadata": {
                "source_id": "src_1",
                "source_type": "web",
                "title": "Climate Science",
                "confidence_score": 0.9
            },
            "relevance_score": 0.85
        },
        {
            "content": "The Paris Agreement was signed in 2015.",
            "metadata": {
                "source_id": "src_2",
                "source_type": "document",
                "title": "Climate Treaties",
                "confidence_score": 0.8
            },
            "relevance_score": 0.75
        }
    ]
    
    # Build prompt
    prompt = graphrag_service.build_attributed_prompt(
        "Explain climate change initiatives",
        sources
    )
    
    # Verify prompt structure
    assert "[SOURCE_1: Climate Science" in prompt
    assert "[SOURCE_2: Climate Treaties" in prompt
    assert "Climate change is a major issue." in prompt
    assert "The Paris Agreement was signed in 2015." in prompt
    assert "Explain climate change initiatives" in prompt
    assert "indicate which source(s) it came from" in prompt

def test_extract_attributions(graphrag_service):
    """Test extracting attributions from a response."""
    # Create a response with attribution markers
    response = (
        "Climate change is a serious global issue [SOURCE_1]. "
        "The Paris Agreement was signed in 2015 [SOURCE_2] and aims to limit "
        "warming to well below 2°C [SOURCE_2]. Scientific evidence supports "
        "the urgent need for action [SOURCE_1]."
    )
    
    # Extract attributions
    attributions = graphrag_service.extract_attributions(response)
    
    # Verify attributions
    assert attributions[1] == 2  # Source 1 referenced twice
    assert attributions[2] == 2  # Source 2 referenced twice

def test_process_attributed_response(graphrag_service):
    """Test processing a response with attributions."""
    # Create a response with attribution markers
    response = (
        "Climate change is a serious global issue [SOURCE_1]. "
        "The Paris Agreement was signed in 2015 [SOURCE_2]."
    )
    
    # Create mock sources
    sources = [
        {
            "content": "Climate change is a major issue.",
            "metadata": {
                "source_id": "src_1",
                "source_type": "web",
                "title": "Climate Science",
                "confidence_score": 0.9
            },
            "relevance_score": 0.85
        },
        {
            "content": "The Paris Agreement was signed in 2015.",
            "metadata": {
                "source_id": "src_2",
                "source_type": "document",
                "title": "Climate Treaties",
                "confidence_score": 0.8
            },
            "relevance_score": 0.75
        }
    ]
    
    # Process response
    result = graphrag_service.process_attributed_response(response, sources)
    
    # Verify result
    assert isinstance(result, AttributionResult)
    assert result.text == response
    assert len(result.sources) == 2
    assert result.sources[0]["source_id"] == "src_1"
    assert result.sources[0]["reference_count"] == 1
    assert result.sources[1]["source_id"] == "src_2"
    assert result.sources[1]["reference_count"] == 1
    assert 0.7 < result.confidence < 0.9  # Should be between source confidence values