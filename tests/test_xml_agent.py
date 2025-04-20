"""Tests for the XML Agent functionality."""

import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from agent_provocateur.a2a_models import TaskRequest, TaskStatus
from agent_provocateur.xml_agent import XmlAgent
from agent_provocateur.models import XmlDocument, XmlNode


SAMPLE_XML_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<research>
    <metadata>
        <title>Sample Research Paper</title>
        <author>John Doe</author>
        <date>2023-01-15</date>
    </metadata>
    <abstract>
        This is a sample abstract that contains statements requiring verification.
    </abstract>
    <findings>
        <finding id="f1">
            <statement>The global temperature has risen by 1.1°C since pre-industrial times.</statement>
            <confidence>high</confidence>
        </finding>
        <finding id="f2">
            <statement>Renewable energy adoption increased by 45% in the last decade.</statement>
            <confidence>medium</confidence>
        </finding>
    </findings>
    <references>
        <reference id="r1">IPCC Climate Report 2022</reference>
        <reference id="r2">Energy Statistics Quarterly, Vol 12</reference>
    </references>
</research>"""


@pytest.fixture
def xml_doc():
    """Create a sample XML document for testing."""
    return XmlDocument(
        doc_id="test_doc",
        doc_type="xml",
        title="Test XML",
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00",
        content=SAMPLE_XML_CONTENT,
        root_element="research",
        namespaces={},
        researchable_nodes=[
            XmlNode(
                xpath="//finding",
                element_name="finding",
                content=None,
                attributes={"id": "f1"},
                verification_status="pending"
            ),
            XmlNode(
                xpath="//statement",
                element_name="statement",
                content="The global temperature has risen by 1.1°C since pre-industrial times.",
                verification_status="pending"
            ),
        ]
    )


@pytest.fixture
def mock_mcp_client():
    """Create a mock MCP client."""
    client = AsyncMock()
    
    # Set up required mock methods
    client.get_xml_document = AsyncMock()
    client.get_xml_content = AsyncMock()
    
    return client


@pytest.fixture
def xml_agent(mock_mcp_client):
    """Create an XML agent with mocked dependencies."""
    agent = XmlAgent(agent_id="test_xml_agent")
    agent.async_mcp_client = mock_mcp_client
    agent.mcp_client = mock_mcp_client
    
    # Mock messaging
    agent.messaging = MagicMock()
    agent.messaging.send_task_result = MagicMock()
    
    # Initialize verification config (needed for tests)
    agent.verification_config = {
        "min_confidence": 0.5,
        "custom_rules": {},
        "prioritize_recent": True,
        "max_nodes_per_task": 5
    }
    
    return agent


@pytest.mark.asyncio
async def test_handle_analyze_xml(xml_agent, xml_doc, mock_mcp_client):
    """Test analyzing XML document."""
    # Setup
    task_request = TaskRequest(
        task_id="test_task",
        source_agent="test_agent",
        target_agent="xml_agent",  # Add required field
        intent="analyze_xml",
        payload={"doc_id": "test_doc"}
    )
    
    # Configure mock
    mock_mcp_client.get_xml_document.return_value = xml_doc
    
    # Execute
    result = await xml_agent.handle_analyze_xml(task_request)
    
    # Verify
    assert result["doc_id"] == "test_doc"
    assert result["title"] == "Test XML"
    assert result["node_count"] == 2
    assert "analysis" in result
    assert result["analysis"]["verification_needed"] is True


@pytest.mark.asyncio
async def test_handle_identify_nodes(xml_agent, mock_mcp_client):
    """Test identifying nodes in XML document."""
    # Setup
    task_request = TaskRequest(
        task_id="test_task",
        source_agent="test_agent",
        target_agent="xml_agent",  # Add required field
        intent="identify_nodes",
        payload={
            "doc_id": "test_doc",
            "min_confidence": 0.4
        }
    )
    
    # Configure mock
    mock_mcp_client.get_xml_content.return_value = SAMPLE_XML_CONTENT
    
    # Execute
    result = await xml_agent.handle_identify_nodes(task_request)
    
    # Verify
    assert result["doc_id"] == "test_doc"
    assert result["node_count"] > 0
    assert "nodes" in result
    assert isinstance(result["nodes"], list)


@pytest.mark.asyncio
async def test_handle_create_verification_plan(xml_agent, xml_doc, mock_mcp_client):
    """Test creating verification plan."""
    # Setup
    task_request = TaskRequest(
        task_id="test_task",
        source_agent="test_agent",
        target_agent="xml_agent",  # Add required field
        intent="create_verification_plan",
        payload={"doc_id": "test_doc"}
    )
    
    # Configure mock
    mock_mcp_client.get_xml_document.return_value = xml_doc
    
    # Execute
    result = await xml_agent.handle_create_verification_plan(task_request)
    
    # Verify
    assert result["doc_id"] == "test_doc"
    assert result["verification_needed"] is True
    assert "tasks" in result
    assert isinstance(result["tasks"], list)
    assert len(result["tasks"]) > 0


@pytest.mark.asyncio
async def test_handle_update_node_status(xml_agent):
    """Test updating node verification status."""
    # Setup
    task_request = TaskRequest(
        task_id="test_task",
        source_agent="test_agent",
        target_agent="xml_agent",  # Add required field
        intent="update_node_status",
        payload={
            "doc_id": "test_doc",
            "xpath": "//finding[@id='f1']",
            "status": "verified",
            "verification_data": {
                "confidence": 0.85,
                "sources": ["Source 1", "Source 2"],
                "notes": "Verified against multiple sources"
            }
        }
    )
    
    # Execute
    result = await xml_agent.handle_update_node_status(task_request)
    
    # Verify
    assert result["doc_id"] == "test_doc"
    assert result["old_status"] == "pending"
    assert result["new_status"] == "verified"
    assert "verification_data" in result


@pytest.mark.asyncio
async def test_handle_batch_verify_nodes(xml_agent, xml_doc, mock_mcp_client):
    """Test batch verification of nodes."""
    # Setup
    task_request = TaskRequest(
        task_id="test_task",
        source_agent="test_agent",
        target_agent="xml_agent",  # Add required field
        intent="batch_verify_nodes",
        payload={
            "doc_id": "test_doc",
            "options": {
                "verify_all": True,
                "search_depth": "medium"
            }
        }
    )
    
    # Configure mock
    mock_mcp_client.get_xml_document.return_value = xml_doc
    
    # Execute
    result = await xml_agent.handle_batch_verify_nodes(task_request)
    
    # Verify
    assert result["doc_id"] == "test_doc"
    assert result["total_nodes"] == 2
    assert result["completed_nodes"] == 2
    assert "verification_results" in result
    assert len(result["verification_results"]) == 2