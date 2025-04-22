"""Tests for DocBook XML validation functionality."""

import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from agent_provocateur.a2a_messaging import InMemoryMessageBroker
from agent_provocateur.a2a_models import TaskRequest
from agent_provocateur.xml_agent import XmlAgent


@pytest.fixture
def docbook_test_xml() -> str:
    """Load DocBook test XML file."""
    test_file = os.path.join(
        os.path.dirname(__file__),
        "test_data/xml_documents/docbook_test.xml"
    )
    with open(test_file, "r") as f:
        return f.read()


@pytest.fixture
def invalid_docbook_xml() -> str:
    """Load invalid DocBook test XML file."""
    test_file = os.path.join(
        os.path.dirname(__file__),
        "test_data/xml_documents/invalid_docbook.xml"
    )
    with open(test_file, "r") as f:
        return f.read()


@pytest.fixture
def valid_docbook_with_entities_xml() -> str:
    """Load valid DocBook with entities XML file."""
    test_file = os.path.join(
        os.path.dirname(__file__),
        "test_data/xml_documents/valid_docbook_with_entities.xml"
    )
    with open(test_file, "r") as f:
        return f.read()


@pytest.fixture
def xml_agent():
    """Create an XML agent with mocked dependencies."""
    broker = InMemoryMessageBroker()
    agent = XmlAgent("test_xml_agent", broker)
    
    # Mock messaging
    agent.messaging = MagicMock()
    agent.messaging.send_task_result = MagicMock()
    
    return agent


@pytest.mark.asyncio
async def test_valid_docbook_validation(xml_agent, docbook_test_xml):
    """Test validation of valid DocBook XML."""
    # Create task request
    task_request = TaskRequest(
        task_id="test_docbook_validation",
        source_agent="test_agent",
        target_agent="xml_agent",
        intent="validate_xml_output",
        payload={
            "xml_content": docbook_test_xml,
            "schema_url": "http://docbook.org/xml/5.0/xsd/docbook.xsd"
        }
    )
    
    # Call the handler
    result = await xml_agent.handle_validate_xml_output(task_request)
    
    # Verify results
    assert result["valid"] is True
    assert len(result["errors"]) == 0
    assert result["schema_validation_performed"] is True
    
    # Verify validation of custom entity/definition elements
    entity_test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns="http://docbook.org/ns/docbook" version="5.0">
    <title>Test with Entity</title>
    <para>This document has an <entity>AI</entity> entity.</para>
    <definition>
        Artificial Intelligence is a field of computer science.
        <sources>
            <source type="web" url="https://example.com">Example</source>
        </sources>
    </definition>
</article>"""
    
    # Create task request for entity test
    entity_task_request = TaskRequest(
        task_id="test_entity_validation",
        source_agent="test_agent",
        target_agent="xml_agent",
        intent="validate_xml_output",
        payload={
            "xml_content": entity_test_xml,
            "schema_url": "http://docbook.org/xml/5.0/xsd/docbook.xsd",
            "validate_entities": True
        }
    )
    
    # Call the handler
    entity_result = await xml_agent.handle_validate_xml_output(entity_task_request)
    
    # The document should be valid - we allow custom elements
    assert entity_result["valid"] is True
    assert entity_result["schema_validation_performed"] is True


@pytest.mark.asyncio
async def test_invalid_docbook_validation(xml_agent, invalid_docbook_xml):
    """Test validation of invalid DocBook XML."""
    # Create task request
    task_request = TaskRequest(
        task_id="test_invalid_docbook_validation",
        source_agent="test_agent",
        target_agent="xml_agent",
        intent="validate_xml_output",
        payload={
            "xml_content": invalid_docbook_xml,
            "schema_url": "http://docbook.org/xml/5.0/xsd/docbook.xsd"
        }
    )
    
    # Call the handler
    result = await xml_agent.handle_validate_xml_output(task_request)
    
    # Verify results
    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert result["schema_validation_performed"] is False
    
    # Verify that we have validation errors
    assert len(result["errors"]) > 0
    
    # Check for various indicators in the output
    all_output = " ".join(result["errors"] + result["warnings"])
    assert any(term in all_output.lower() for term in ["entity", "namespace", "root", "docbook"])


@pytest.mark.asyncio
async def test_valid_docbook_with_entities(xml_agent, valid_docbook_with_entities_xml):
    """Test validation of valid DocBook XML with entity and definition elements."""
    # Create task request
    task_request = TaskRequest(
        task_id="test_docbook_with_entities",
        source_agent="test_agent",
        target_agent="xml_agent",
        intent="validate_xml_output",
        payload={
            "xml_content": valid_docbook_with_entities_xml,
            "schema_url": "http://docbook.org/xml/5.0/xsd/docbook.xsd"
        }
    )
    
    # Call the handler
    result = await xml_agent.handle_validate_xml_output(task_request)
    
    # Verify results
    assert result["valid"] is True
    assert len(result["errors"]) == 0
    assert result["schema_validation_performed"] is True


@pytest.mark.asyncio
async def test_validation_with_custom_schema(xml_agent, docbook_test_xml):
    """Test validation with custom schema URL."""
    # Create task request with custom schema
    task_request = TaskRequest(
        task_id="test_custom_schema",
        source_agent="test_agent",
        target_agent="xml_agent",
        intent="validate_xml_output",
        payload={
            "xml_content": docbook_test_xml,
            "schema_url": "http://custom-schema.org/docbook.xsd"
        }
    )
    
    # Call the handler
    result = await xml_agent.handle_validate_xml_output(task_request)
    
    # Schema validation should still work for DocBook but with warning
    assert result["schema_url"] == "http://custom-schema.org/docbook.xsd"
    assert result["valid"] is True  # The XML is still well-formed DocBook


def test_docbook_schema_validator_direct(xml_agent, docbook_test_xml, invalid_docbook_xml):
    """Test the DocBook validator function directly."""
    # Test with valid DocBook
    valid_result = xml_agent._validate_xml_against_schema(
        docbook_test_xml,
        "http://docbook.org/xml/5.0/xsd/docbook.xsd",
        "xsd"
    )
    
    assert valid_result["valid"] is True
    assert valid_result["schema_validation_performed"] is True
    
    # Test with invalid DocBook
    invalid_result = xml_agent._validate_xml_against_schema(
        invalid_docbook_xml,
        "http://docbook.org/xml/5.0/xsd/docbook.xsd",
        "xsd"
    )
    
    assert invalid_result["valid"] is False
    assert invalid_result["schema_validation_performed"] is False
    
    # Check that we have at least one error
    assert len(invalid_result["errors"]) >= 1
    assert "XML syntax error" in invalid_result["errors"][0]