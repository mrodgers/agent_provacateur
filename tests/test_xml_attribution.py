"""
Tests for XML source attribution service.
"""

import pytest
import asyncio
import datetime
import uuid
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Import the service and models
from agent_provocateur.xml_attribution import XmlAttributionService
from agent_provocateur.models import (
    Source, SourceType, XmlDocument, XmlNode
)
from agent_provocateur.source_model import (
    Entity, EntityType, EnhancedSource
)

# Create test data
@pytest.fixture
def sample_xml_doc():
    """Create a sample XML document for testing."""
    return XmlDocument(
        doc_id="test_doc_1",
        doc_type="xml",
        title="Test XML Document",
        created_at=datetime.datetime.now().isoformat(),
        updated_at=datetime.datetime.now().isoformat(),
        content="""
        <research>
            <section>
                <title>Climate Change Effects</title>
                <paragraph>
                    Global temperatures have risen by 1.1°C since pre-industrial times,
                    leading to various environmental impacts.
                </paragraph>
            </section>
        </research>
        """,
        root_element="research",
        researchable_nodes=[
            XmlNode(
                xpath="/research/section/paragraph[1]",
                element_name="paragraph",
                content="Global temperatures have risen by 1.1°C since pre-industrial times, "
                        "leading to various environmental impacts.",
                verification_status="pending"
            )
        ]
    )

@pytest.fixture
def sample_sources():
    """Create sample sources for testing."""
    return [
        {
            "content": "Global temperatures have risen by 1.1°C on average since pre-industrial times.",
            "metadata": {
                "source_id": "src_1",
                "source_type": "web",
                "title": "Climate Science Report",
                "url": "https://example.com/climate",
                "confidence_score": 0.9
            },
            "relevance_score": 0.95,
            "explanation": "This source directly addresses the statement about temperature rise"
        },
        {
            "content": "Environmental impacts of climate change include sea level rise and extreme weather.",
            "metadata": {
                "source_id": "src_2",
                "source_type": "document",
                "title": "Environmental Assessment",
                "confidence_score": 0.85
            },
            "relevance_score": 0.8,
            "explanation": "This source supports the claim about environmental impacts"
        }
    ]

@pytest.fixture
def mock_graphrag_service():
    """Create a mock GraphRAG service."""
    mock = MagicMock()
    
    # Configure methods
    mock.get_sources_for_query = MagicMock()
    mock.extract_entities_from_text = MagicMock()
    mock.index_source = MagicMock()
    mock.create_enhanced_source = MagicMock()
    
    return mock

@pytest.fixture
def attribution_service(mock_graphrag_service):
    """Create an attribution service with mocked GraphRAG."""
    with patch('agent_provocateur.xml_attribution.GraphRAGService', 
              return_value=mock_graphrag_service):
        service = XmlAttributionService()
        yield service

@pytest.mark.asyncio
async def test_attribute_node(attribution_service, mock_graphrag_service, sample_sources, sample_xml_doc):
    """Test attributing a single node."""
    # Configure mock
    mock_graphrag_service.get_sources_for_query.return_value = sample_sources
    
    # Get test node
    node = sample_xml_doc.researchable_nodes[0]
    
    # Attribute node
    result = await attribution_service.attribute_node(node, sample_xml_doc.doc_id)
    
    # Verify attribution
    assert result.verification_status == "verified"
    assert len(result.sources) == 2
    assert result.sources[0].source_type == SourceType.WEB
    assert result.sources[0].title == "Climate Science Report"
    assert "confidence" in result.verification_data
    assert result.verification_data["verification_method"] == "graphrag"

@pytest.mark.asyncio
async def test_process_xml_document(attribution_service, mock_graphrag_service, sample_sources, sample_xml_doc):
    """Test processing a complete XML document."""
    # Configure mock
    mock_graphrag_service.get_sources_for_query.return_value = sample_sources
    
    # Process document
    result = await attribution_service.process_xml_document(sample_xml_doc)
    
    # Verify document processing
    assert result.doc_id == sample_xml_doc.doc_id
    assert len(result.researchable_nodes) == 1
    assert result.researchable_nodes[0].verification_status == "verified"
    assert len(result.researchable_nodes[0].sources) == 2

@pytest.mark.asyncio
async def test_attribute_node_no_sources(attribution_service, mock_graphrag_service, sample_xml_doc):
    """Test attributing a node when no sources are found."""
    # Configure mock to return no sources
    mock_graphrag_service.get_sources_for_query.return_value = []
    mock_graphrag_service.extract_entities_from_text.return_value = []
    
    # Get test node
    node = sample_xml_doc.researchable_nodes[0]
    
    # Attribute node
    result = await attribution_service.attribute_node(node, sample_xml_doc.doc_id)
    
    # Verify fallback
    assert result.verification_status == "unverified"
    assert len(result.sources) == 1
    assert result.sources[0].source_type == SourceType.OTHER
    assert "fallback" in result.sources[0].metadata
    assert result.verification_data["verification_method"] == "fallback"

@pytest.mark.asyncio
async def test_attribute_node_with_existing_sources(attribution_service, mock_graphrag_service, sample_sources, sample_xml_doc):
    """Test attributing a node that already has sources."""
    # Add existing sources to node
    node = sample_xml_doc.researchable_nodes[0]
    node.sources = [
        Source(
            source_id="existing_src_1",
            source_type=SourceType.DOCUMENT,
            title="Existing Source",
            confidence=0.7,
            metadata={"content": "Some existing content about climate change"}
        )
    ]
    
    # Configure mock
    mock_graphrag_service.get_sources_for_query.return_value = sample_sources
    
    # Attribute node
    result = await attribution_service.attribute_node(node, sample_xml_doc.doc_id)
    
    # Verify attribution and indexing of existing sources
    assert result.verification_status == "verified"
    assert len(result.sources) == 2  # New sources from the query
    mock_graphrag_service.index_source.assert_called_once()  # Should index existing source

@pytest.mark.asyncio
async def test_attribute_document_from_web_search(attribution_service, mock_graphrag_service, sample_sources, sample_xml_doc):
    """Test enhancing attribution with web search results."""
    # Create sample web search results
    web_results = [
        {
            "title": "Climate Change Report",
            "url": "https://example.com/climate-report",
            "snippet": "Global temperatures have risen significantly in the last century.",
            "rank": 1
        },
        {
            "title": "Environmental Impacts",
            "url": "https://example.com/impacts",
            "snippet": "Climate change causes various environmental impacts worldwide.",
            "content": "Full content about environmental impacts including sea level rise.",
            "rank": 2
        }
    ]
    
    # Configure mocks
    mock_graphrag_service.get_sources_for_query.return_value = sample_sources
    
    # Test attribution with web search
    result = await attribution_service.attribute_document_from_web_search(sample_xml_doc, web_results)
    
    # Verify results
    assert result.doc_id == sample_xml_doc.doc_id
    assert len(result.researchable_nodes) == 1
    assert result.researchable_nodes[0].verification_status == "verified"
    
    # Check that web search results were indexed
    assert mock_graphrag_service.create_enhanced_source.call_count == 2
    assert mock_graphrag_service.index_source.call_count >= 2

def test_extract_entities_from_document(attribution_service, mock_graphrag_service, sample_xml_doc):
    """Test extracting entities from a document."""
    # Create sample entities
    entities = [
        Entity.create("Global temperatures", EntityType.CONCEPT),
        Entity.create("climate change", EntityType.CONCEPT)
    ]
    
    # Configure mock
    mock_graphrag_service.extract_entities_from_text.return_value = entities
    
    # Extract entities
    result = attribution_service.extract_entities_from_document(sample_xml_doc)
    
    # Verify entity extraction
    assert len(result) == 2
    assert result[0].name == "Global temperatures"
    assert result[0].entity_type == EntityType.CONCEPT
    assert result[1].name == "climate change"