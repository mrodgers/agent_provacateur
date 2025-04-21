"""
Tests for GraphRAG client integration.
"""

import pytest
import aiohttp
import asyncio
from unittest.mock import patch, Mock
import json

from agent_provocateur.graphrag_client import GraphRAGClient

# Sample test data
SAMPLE_TEXT = """
Climate change is a significant challenge facing our planet. Global temperatures have risen by 
approximately 1.1°C since pre-industrial times, leading to various environmental impacts. 
Organizations like the IPCC provide scientific data on climate trends. The Paris Agreement, 
signed in 2015, aims to limit global warming to well below 2°C.
"""

@pytest.fixture
def mock_response():
    """Create a mock aiohttp response."""
    mock = Mock()
    mock.status = 200
    mock.json = Mock(return_value=asyncio.Future())
    mock.json.return_value.set_result({})
    mock.__aenter__ = Mock(return_value=mock)
    mock.__aexit__ = Mock(return_value=None)
    return mock

@pytest.fixture
def mock_session(mock_response):
    """Create a mock aiohttp ClientSession."""
    mock = Mock()
    mock.post = Mock(return_value=mock_response)
    mock.get = Mock(return_value=mock_response)
    mock.__aenter__ = Mock(return_value=mock)
    mock.__aexit__ = Mock(return_value=None)
    return mock

@pytest.mark.asyncio
async def test_call_tool(mock_session, mock_response):
    """Test calling a tool on the GraphRAG MCP server."""
    with patch('aiohttp.ClientSession', return_value=mock_session):
        client = GraphRAGClient(base_url="http://test-server")
        
        # Configure mock response
        mock_response.json.return_value = asyncio.Future()
        mock_response.json.return_value.set_result({
            "success": True,
            "test": "value"
        })
        
        # Call the tool
        result = await client.call_tool("test_tool", {"param": "value"})
        
        # Verify the call
        mock_session.post.assert_called_once_with(
            "http://test-server/api/tools/test_tool",
            json={"param": "value"}
        )
        
        assert result["success"] is True
        assert result["test"] == "value"

@pytest.mark.asyncio
async def test_extract_entities(mock_session, mock_response):
    """Test extracting entities from text."""
    with patch('aiohttp.ClientSession', return_value=mock_session):
        client = GraphRAGClient(base_url="http://test-server")
        
        # Configure mock response
        mock_response.json.return_value = asyncio.Future()
        mock_response.json.return_value.set_result({
            "success": True,
            "entities": [
                {
                    "entity_id": "ent_123",
                    "entity_type": "concept",
                    "name": "Climate change",
                    "confidence": 0.95
                },
                {
                    "entity_id": "ent_456",
                    "entity_type": "organization",
                    "name": "IPCC",
                    "confidence": 0.9
                }
            ]
        })
        
        # Extract entities
        entities = await client.extract_entities(SAMPLE_TEXT)
        
        # Verify the call
        mock_session.post.assert_called_once_with(
            "http://test-server/api/tools/graphrag_extract_entities",
            json={"text": SAMPLE_TEXT, "options": {}}
        )
        
        assert len(entities) == 2
        assert entities[0]["entity_id"] == "ent_123"
        assert entities[0]["name"] == "Climate change"
        assert entities[1]["entity_type"] == "organization"

@pytest.mark.asyncio
async def test_get_sources_for_query(mock_session, mock_response):
    """Test getting sources for a query."""
    with patch('aiohttp.ClientSession', return_value=mock_session):
        client = GraphRAGClient(base_url="http://test-server")
        
        # Configure mock response
        mock_response.json.return_value = asyncio.Future()
        mock_response.json.return_value.set_result({
            "success": True,
            "sources": [
                {
                    "content": "Climate change data shows...",
                    "metadata": {
                        "source_id": "src_123",
                        "title": "Climate Report",
                        "confidence_score": 0.9
                    },
                    "relevance_score": 0.95
                }
            ],
            "attributed_prompt": "Answer based on these sources: [SOURCE_1]..."
        })
        
        # Get sources
        sources, prompt = await client.get_sources_for_query(
            "What are the effects of climate change?",
            focus_entities=["ent_123"]
        )
        
        # Verify the call
        mock_session.post.assert_called_once_with(
            "http://test-server/api/tools/graphrag_query",
            json={
                "query": "What are the effects of climate change?",
                "focus_entities": ["ent_123"],
                "options": {}
            }
        )
        
        assert len(sources) == 1
        assert sources[0]["metadata"]["source_id"] == "src_123"
        assert sources[0]["relevance_score"] == 0.95
        assert "Answer based on these sources" in prompt

@pytest.mark.asyncio
async def test_process_attributed_response():
    """Test processing an attributed response."""
    client = GraphRAGClient(base_url="http://test-server")
    
    # Sample response and sources
    response = "Climate change is a serious issue [SOURCE_1]. The Paris Agreement was signed in 2015 [SOURCE_2]."
    sources = [
        {
            "content": "Climate change is a serious global issue.",
            "metadata": {
                "source_id": "src_123",
                "title": "Climate Report",
                "confidence_score": 0.9
            },
            "relevance_score": 0.95
        },
        {
            "content": "The Paris Agreement was signed in 2015.",
            "metadata": {
                "source_id": "src_456",
                "title": "Paris Agreement",
                "confidence_score": 0.85
            },
            "relevance_score": 0.8
        }
    ]
    
    # Process response
    result = await client.process_attributed_response(response, sources)
    
    # Verify the result
    assert len(result["sources"]) == 2
    assert result["sources"][0]["source_id"] == "src_123"
    assert result["sources"][0]["reference_count"] == 1
    assert result["sources"][1]["source_id"] == "src_456"
    assert result["sources"][1]["reference_count"] == 1
    assert 0.7 < result["confidence"] < 0.95  # Should be between the source confidence values