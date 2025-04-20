"""Tests for the Research CLI integration."""

import os
import pytest
import sys
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from io import StringIO

from agent_provocateur.cli import run_command, format_research_results
from agent_provocateur.a2a_models import TaskRequest


@pytest.fixture
def research_result():
    """Create a mock research result."""
    return {
        "doc_id": "test1",
        "entity_count": 3,
        "research_count": 2,
        "workflow_id": "research_test1_123456789",
        "summary": "Research completed successfully",
        "research_results": [
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
        ],
        "enriched_xml": "<?xml version=\"1.0\"?><research-document>...</research-document>",
        "validation": {
            "valid": True,
            "errors": [],
            "warnings": ["Basic validation only"]
        }
    }


def test_format_research_results(research_result):
    """Test formatting of research results."""
    formatted = format_research_results(research_result)
    
    # Check that key information is included
    assert "Research Results for Document: test1" in formatted
    assert "Workflow ID: research_test1_123456789" in formatted
    assert "Entities Found: 3" in formatted
    assert "Entities Researched: 2" in formatted
    assert "ChatGPT" in formatted
    assert "Natural Language Processing" in formatted
    assert "Enriched XML Output" in formatted
    assert "Validation: VALID" in formatted


@pytest.mark.asyncio
async def test_research_command_xml_format():
    """Test the research command with XML output format."""
    # Create mock args
    args = MagicMock()
    args.command = "research"
    args.doc_id = "xml1"
    args.format = "xml"
    args.output = "test_output.xml"
    args.max_entities = 5
    args.min_confidence = 0.4
    args.with_search = False
    args.with_jira = False
    args.server = "http://localhost:8000"
    args.json = False
    
    # Create mock agents
    mock_supervisor = MagicMock()
    mock_supervisor.handle_research_document = AsyncMock()
    mock_supervisor.handle_research_document.return_value = {
        "doc_id": "xml1",
        "entity_count": 3,
        "research_count": 2,
        "workflow_id": "research_xml1_123456789",
        "enriched_xml": "<?xml version=\"1.0\"?><research-document>...</research-document>",
        "validation": {"valid": True}
    }
    mock_supervisor.start = AsyncMock()
    mock_supervisor.stop = AsyncMock()
    
    # Create mock for other agents
    mock_agent = MagicMock()
    mock_agent.start = AsyncMock()
    mock_agent.stop = AsyncMock()
    
    # Create mock open for output file
    mock_open = MagicMock()
    
    # Patch necessary imports and functions
    with patch('agent_provocateur.cli.ResearchSupervisorAgent', return_value=mock_supervisor), \
         patch('agent_provocateur.cli.XmlAgent', return_value=mock_agent), \
         patch('agent_provocateur.cli.DocAgent', return_value=mock_agent), \
         patch('agent_provocateur.cli.DecisionAgent', return_value=mock_agent), \
         patch('agent_provocateur.cli.SynthesisAgent', return_value=mock_agent), \
         patch('builtins.open', mock_open), \
         patch('builtins.print'), \
         patch('sys.exit'):
        
        # Run the command
        await run_command(args)
        
        # Verify supervisor was called correctly
        assert mock_supervisor.handle_research_document.call_count == 1
        call_args = mock_supervisor.handle_research_document.call_args[0][0]
        assert isinstance(call_args, TaskRequest)
        assert call_args.intent == "research_document"
        assert call_args.payload["doc_id"] == "xml1"
        assert call_args.payload["options"]["format"] == "xml"
        assert call_args.payload["options"]["max_entities"] == 5
        
        # Verify output file was created
        mock_open.assert_called_once_with("test_output.xml", "w")
        
        # Verify agents were started and stopped
        assert mock_supervisor.start.call_count == 1
        assert mock_supervisor.stop.call_count == 1
        assert mock_agent.start.call_count == 4  # 4 other agents
        assert mock_agent.stop.call_count == 4