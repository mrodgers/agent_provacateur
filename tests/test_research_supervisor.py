"""Tests for the Research Supervisor Agent."""

import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from agent_provocateur.a2a_messaging import InMemoryMessageBroker
from agent_provocateur.a2a_models import TaskRequest, TaskResult, TaskStatus
from agent_provocateur.models import Document, XmlDocument
from agent_provocateur.research_supervisor_agent import ResearchSupervisorAgent


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
def mock_xml_document():
    """Create a mock XML document."""
    return XmlDocument(
        doc_id="xml1",
        doc_type="xml",
        title="Test XML Document",
        content="<root><entity>Test Entity</entity></root>",
        root_element="root",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
        namespaces={},
        researchable_nodes=[]
    )


@pytest.mark.asyncio
async def test_detect_document_type_xml(mock_xml_document):
    """Test detecting XML document type."""
    # Create mock client
    mock_client = AsyncMock()
    mock_client.get_document = AsyncMock(return_value=mock_xml_document)
    
    # Create agent
    broker = InMemoryMessageBroker()
    agent = ResearchSupervisorAgent("test_supervisor", broker)
    agent.async_mcp_client = mock_client
    
    # Test document type detection
    result = await agent.detect_document_type("xml1")
    
    # Verify results
    assert result["doc_id"] == "xml1"
    assert result["is_xml"] is True
    assert result["needs_verification"] is True
    assert result["needs_research"] is True
    assert result["detected_type"] == "xml"


@pytest.mark.asyncio
async def test_detect_document_type_non_xml():
    """Test detecting non-XML document type."""
    # Create mock document
    text_doc = Document(
        doc_id="text1",
        doc_type="text",
        title="Test Text Document",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
        metadata={}
    )
    
    # Create mock client
    mock_client = AsyncMock()
    mock_client.get_document = AsyncMock(return_value=text_doc)
    
    # Create agent
    broker = InMemoryMessageBroker()
    agent = ResearchSupervisorAgent("test_supervisor", broker)
    agent.async_mcp_client = mock_client
    
    # Test document type detection
    result = await agent.detect_document_type("text1")
    
    # Verify results
    assert result["doc_id"] == "text1"
    assert result["is_xml"] is False
    assert result["detected_type"] == "text"


@pytest.mark.asyncio
async def test_research_entities():
    """Test entity research."""
    # Create test entities
    entities = [
        {
            "name": "ChatGPT",
            "xpath": "/root/entity[1]",
            "confidence": 0.8,
            "context": "ChatGPT is an AI model"
        },
        {
            "name": "Natural Language Processing",
            "xpath": "/root/entity[2]",
            "confidence": 0.7,
            "context": "NLP is used for text analysis"
        }
    ]
    
    # Create agent
    broker = InMemoryMessageBroker()
    agent = ResearchSupervisorAgent("test_supervisor", broker)
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_task",
        source_agent="test_agent",
        target_agent="test_supervisor",
        intent="research_entities",
        payload={"entities": entities}
    )
    
    # Call the handler
    result = await agent.handle_research_entities(task_request)
    
    # Verify results
    assert result["entity_count"] == 2
    assert result["researched_count"] == 2
    
    research_results = result["research_results"]
    assert len(research_results) == 2
    
    # Check first entity result
    gpt_result = next((r for r in research_results if r["entity"] == "ChatGPT"), None)
    assert gpt_result is not None
    assert "definition" in gpt_result
    assert "confidence" in gpt_result
    assert len(gpt_result["sources"]) > 0
    
    # Check second entity result
    nlp_result = next((r for r in research_results if r["entity"] == "Natural Language Processing"), None)
    assert nlp_result is not None
    assert "definition" in nlp_result
    assert "confidence" in nlp_result
    assert len(nlp_result["sources"]) > 0


@pytest.mark.asyncio
async def test_generate_research_xml(entity_test_xml):
    """Test generating enriched XML with research results."""
    # Create mock client
    mock_client = AsyncMock()
    mock_client.get_xml_content = AsyncMock(return_value=entity_test_xml)
    
    # Create agent
    broker = InMemoryMessageBroker()
    agent = ResearchSupervisorAgent("test_supervisor", broker)
    agent.async_mcp_client = mock_client
    
    # Create research results
    research_results = [
        {
            "entity": "ChatGPT",
            "definition": "ChatGPT is a conversational AI model developed by OpenAI.",
            "confidence": 0.9,
            "sources": [
                {"type": "web", "title": "OpenAI Website", "url": "https://openai.com"}
            ]
        },
        {
            "entity": "Natural Language Processing",
            "definition": "NLP is a field of AI focused on the interaction between computers and human language.",
            "confidence": 0.8,
            "sources": [
                {"type": "document", "title": "AI Textbook", "doc_id": "doc1"}
            ]
        }
    ]
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_task",
        source_agent="test_agent",
        target_agent="test_supervisor",
        intent="generate_research_xml",
        payload={
            "original_doc_id": "xml1",
            "research_results": research_results
        }
    )
    
    # Call the handler
    result = await agent.handle_generate_research_xml(task_request)
    
    # Verify results
    assert result["original_doc_id"] == "xml1"
    assert "enriched_xml" in result
    assert result["entity_count"] == 2
    
    # Check that enriched XML contains expected elements
    enriched_xml = result["enriched_xml"]
    assert '<?xml version="1.0" encoding="UTF-8"?>' in enriched_xml
    assert '<research-document>' in enriched_xml
    assert '<original-content>' in enriched_xml
    assert '<research-results>' in enriched_xml
    assert '<entity-research entity="ChatGPT"' in enriched_xml
    assert '<entity-research entity="Natural Language Processing"' in enriched_xml
    assert '<definition>' in enriched_xml
    assert '<sources>' in enriched_xml
    
    # Check validation result
    assert result["validation"]["valid"] is True


@pytest.mark.asyncio
async def test_research_document_workflow():
    """Test the complete document research workflow for XML documents."""
    # Create a mock broker that simulates the messaging system
    mock_broker = MagicMock()
    
    # Configure mock task results
    detect_result = {
        "doc_id": "xml1",
        "is_xml": True,
        "needs_verification": True,
        "needs_research": True,
        "detected_type": "xml"
    }
    
    entity_result = {
        "doc_id": "xml1",
        "entity_count": 2,
        "entities": [
            {
                "name": "ChatGPT",
                "xpath": "/root/entity[1]",
                "confidence": 0.8,
                "context": "ChatGPT is an AI model"
            },
            {
                "name": "Natural Language Processing",
                "xpath": "/root/entity[2]",
                "confidence": 0.7,
                "context": "NLP is used for text analysis"
            }
        ]
    }
    
    # Create a mock send_request_and_wait method
    async def mock_send_request(*args, **kwargs):
        intent = kwargs.get("intent")
        if intent == "extract_entities":
            result = MagicMock()
            result.output = entity_result
            return result
        # Other intents will be handled by the real methods
        return None
    
    # Create agent with mock broker and methods
    agent = ResearchSupervisorAgent("test_supervisor", mock_broker)
    
    # Mock methods
    agent.send_request_and_wait = AsyncMock(side_effect=mock_send_request)
    agent.detect_document_type = AsyncMock(return_value=detect_result)
    
    # Create a task request
    task_request = TaskRequest(
        task_id="test_task",
        source_agent="test_agent",
        target_agent="test_supervisor",
        intent="research_document",
        payload={"doc_id": "xml1"}
    )
    
    # Call the research_document handler
    result = await agent.handle_research_document(task_request)
    
    # Verify workflow execution
    assert result["doc_id"] == "xml1"
    assert "entity_count" in result
    assert "research_count" in result
    assert "enriched_xml" in result
    assert "workflow_id" in result
    
    # Verify the detect_document_type was called
    agent.detect_document_type.assert_called_once_with("xml1")
    
    # Verify the send_request_and_wait was called to extract entities
    agent.send_request_and_wait.assert_any_call(
        target_agent="xml_agent",
        intent="extract_entities",
        payload={"doc_id": "xml1", "options": {}}
    )
    
    # Verify workflow tracking
    workflow_id = result["workflow_id"]
    assert workflow_id in agent.workflows
    assert agent.workflows[workflow_id]["status"] == "completed"
    assert "steps_completed" in agent.workflows[workflow_id]
    assert "detect_document_type" in agent.workflows[workflow_id]["steps_completed"]
    assert "extract_entities" in agent.workflows[workflow_id]["steps_completed"]