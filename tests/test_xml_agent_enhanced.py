"""Tests for the enhanced XML Agent functionality."""

import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from agent_provocateur.a2a_messaging import InMemoryMessageBroker
from agent_provocateur.a2a_models import TaskRequest
from agent_provocateur.xml_agent import XmlAgent


@pytest.fixture
def entity_test_xml() -> str:
    """Load entity test XML file."""
    test_file = os.path.join(
        os.path.dirname(__file__),
        "test_data/xml_documents/entity_test.xml"
    )
    with open(test_file, "r") as f:
        return f.read()


@pytest.fixture
def docbook_test_xml() -> str:
    """Load DocBook test XML file."""
    test_file = os.path.join(
        os.path.dirname(__file__),
        "test_data/xml_documents/docbook_test.xml"
    )
    with open(test_file, "r") as f:
        return f.read()


@pytest.mark.asyncio
async def test_entity_extraction(entity_test_xml):
    """Test entity extraction from XML document."""
    # Create mock client
    mock_client = AsyncMock()
    mock_client.get_xml_content = AsyncMock(return_value=entity_test_xml)
    
    # Create agent
    broker = InMemoryMessageBroker()
    agent = XmlAgent("test_xml_agent", broker)
    agent.async_mcp_client = mock_client
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_task",
        source_agent="test_agent",
        target_agent="test_xml_agent",
        intent="extract_entities",
        payload={"doc_id": "xml1"}
    )
    
    # Call the handler
    result = await agent.handle_extract_entities(task_request)
    
    # Verify results
    assert result["doc_id"] == "xml1"
    assert result["entity_count"] > 0
    
    entities = result["entities"]
    entity_names = [e["name"] for e in entities]
    
    # Check for specific entities
    assert "ChatGPT" in entity_names
    assert "Natural Language Processing" in entity_names
    assert "Large Language Models" in entity_names
    assert "Transformer Architecture" in entity_names
    assert "OpenAI" in entity_names
    
    # Check entity structure
    for entity in entities:
        assert "name" in entity
        assert "xpath" in entity
        assert "confidence" in entity
        assert "context" in entity


@pytest.mark.asyncio
async def test_xml_validation_valid(docbook_test_xml):
    """Test XML validation with valid DocBook document."""
    # Create agent
    broker = InMemoryMessageBroker()
    agent = XmlAgent("test_xml_agent", broker)
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_task",
        source_agent="test_agent",
        target_agent="test_xml_agent",
        intent="validate_xml_output",
        payload={
            "xml_content": docbook_test_xml,
            "schema_url": "http://docbook.org/xml/5.0/xsd/docbook.xsd"
        }
    )
    
    # Call the handler
    result = await agent.handle_validate_xml_output(task_request)
    
    # Verify results
    assert result["valid"] is True
    assert len(result["errors"]) == 0
    assert "schema_url" in result
    assert "schema_type" in result


@pytest.mark.asyncio
async def test_xml_validation_invalid():
    """Test XML validation with invalid XML document."""
    # Create invalid XML
    invalid_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <root>
        <element>Unclosed element
        <another>Missing closing tag
    </root>
    """
    
    # Create agent
    broker = InMemoryMessageBroker()
    agent = XmlAgent("test_xml_agent", broker)
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_task",
        source_agent="test_agent",
        target_agent="test_xml_agent",
        intent="validate_xml_output",
        payload={
            "xml_content": invalid_xml,
            "schema_url": "http://docbook.org/xml/5.0/xsd/docbook.xsd"
        }
    )
    
    # Call the handler
    result = await agent.handle_validate_xml_output(task_request)
    
    # Verify results
    assert result["valid"] is False
    assert len(result["errors"]) > 0


@pytest.mark.asyncio
async def test_context_extraction(entity_test_xml):
    """Test context extraction from XML node."""
    # Create mock client
    mock_client = AsyncMock()
    mock_client.get_xml_content = AsyncMock(return_value=entity_test_xml)
    
    # Create agent
    broker = InMemoryMessageBroker()
    agent = XmlAgent("test_xml_agent", broker)
    agent.async_mcp_client = mock_client
    
    # Extract context directly
    context = agent._extract_context(entity_test_xml, "//entity[@type='organization']")
    
    # Verify context
    assert context is not None
    assert len(context) > 0
    assert "OpenAI" in context
    assert "research team" in context