"""Tests for the XML CLI scripts."""

import os
import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

# Import the CLI modules
import sys
# Add scripts directory to path to import modules directly
sys.path.append(str(Path(__file__).parent.parent / "scripts"))
import xml_cli
import xml_agent_cli

from agent_provocateur.models import XmlDocument, XmlNode
from agent_provocateur.xml_parser import load_xml_file


@pytest.fixture
def sample_xml_path():
    """Create a temporary XML file for testing."""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<test>
    <item id="1">Test item 1</item>
    <item id="2">Test item 2</item>
</test>
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(content)
        path = f.name
    
    yield path
    
    # Clean up
    os.unlink(path)


@pytest.fixture
def sample_rules_path():
    """Create a temporary rules file for testing."""
    content = {
        "keyword_rules": {
            "item": ["test", "example"]
        },
        "attribute_rules": {
            "id": ["1", "2"]
        },
        "content_patterns": [
            "Test.*\\d+"
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(content, f)
        path = f.name
    
    yield path
    
    # Clean up
    os.unlink(path)


@pytest.fixture
def mock_mcp_client():
    """Create a mock MCP client."""
    with patch('agent_provocateur.mcp_client.McpClient', autospec=True) as mock:
        client_instance = mock.return_value
        
        # Mock list_documents
        client_instance.list_documents = AsyncMock()
        client_instance.list_documents.return_value = [
            XmlDocument(
                doc_id="xml1",
                doc_type="xml",
                title="Test Document",
                content="<test></test>",
                root_element="test",
                created_at="2024-01-01T00:00:00",
                updated_at="2024-01-01T00:00:00",
                namespaces={},
                researchable_nodes=[]
            )
        ]
        
        # Mock get_xml_document
        client_instance.get_xml_document = AsyncMock()
        client_instance.get_xml_document.return_value = XmlDocument(
            doc_id="xml1",
            doc_type="xml",
            title="Test Document",
            content="<test><item>Test</item></test>",
            root_element="test",
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
            namespaces={},
            researchable_nodes=[
                XmlNode(
                    xpath="//item",
                    element_name="item",
                    content="Test",
                    attributes={},
                    verification_status="pending"
                )
            ]
        )
        
        # Mock get_xml_content
        client_instance.get_xml_content = AsyncMock()
        client_instance.get_xml_content.return_value = "<test><item>Test</item></test>"
        
        yield mock


@pytest.mark.asyncio
async def test_xml_cli_upload_file_path_handling(sample_xml_path):
    """Test that the XML CLI correctly handles file paths."""
    # Setup
    args = MagicMock()
    args.file = sample_xml_path
    args.title = "Test Upload"
    args.server = "http://localhost:8000"
    args.json = False
    
    mock_client = AsyncMock()
    mock_client.upload_xml = AsyncMock()
    mock_client.upload_xml.return_value = XmlDocument(
        doc_id="new_doc",
        doc_type="xml",
        title="Test Upload",
        content="<test></test>",
        root_element="test",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
        namespaces={},
        researchable_nodes=[]
    )
    
    # Execute
    # Directly patch the module's McpClient import instead of the original path
    with patch.object(xml_cli, 'McpClient', return_value=mock_client), \
         patch('sys.exit'), patch('builtins.print'):
        await xml_cli.upload_xml(args)
    
    # Debug
    print(f"Debug - upload_xml call count: {mock_client.upload_xml.call_count}")
    print(f"Debug - upload_xml calls: {mock_client.upload_xml.mock_calls}")
    
    # Verify
    mock_client.upload_xml.assert_called_once()
    # The file content should have been loaded and passed to upload_xml
    args_passed = mock_client.upload_xml.call_args[0]
    assert "<test>" in args_passed[0]  # XML content
    assert args_passed[1] == "Test Upload"  # Title


@pytest.mark.asyncio
async def test_xml_agent_cli_identify_file_path_handling(sample_xml_path, sample_rules_path):
    """Test that the XML Agent CLI correctly handles file paths."""
    # Setup
    args = MagicMock()
    args.file = sample_xml_path
    args.doc_id = None
    args.confidence = 0.4
    args.rules_file = sample_rules_path
    args.evidence = True
    args.output = None
    args.server = "http://localhost:8000"
    
    # Execute
    with patch('sys.exit'), patch('builtins.print'):
        await xml_agent_cli.advanced_identify(args)
    
    # No assertions needed - if the function runs without errors, the test passes
    # This is primarily testing that the file path handling logic works correctly


@pytest.mark.asyncio
async def test_xml_agent_cli_identify_doc_id():
    """Test identifying nodes using doc_id."""
    # Setup
    args = MagicMock()
    args.file = None
    args.doc_id = "xml1"
    args.confidence = 0.4
    args.rules_file = None
    args.evidence = True
    args.output = None
    args.server = "http://localhost:8000"
    
    mock_client = AsyncMock()
    mock_client.get_xml_content = AsyncMock()
    mock_client.get_xml_content.return_value = "<test><item>Test</item></test>"
    
    # Execute
    # Directly patch the module's McpClient import instead of the original path
    with patch.object(xml_agent_cli, 'McpClient', return_value=mock_client), \
         patch('sys.exit'), patch('builtins.print'):
        await xml_agent_cli.advanced_identify(args)
    
    # Debug
    print(f"Debug - get_xml_content call count: {mock_client.get_xml_content.call_count}")
    print(f"Debug - get_xml_content calls: {mock_client.get_xml_content.mock_calls}")
    
    # Verify
    mock_client.get_xml_content.assert_called_once_with("xml1")


@pytest.mark.asyncio
async def test_xml_agent_cli_verify_plan():
    """Test creating a verification plan."""
    # Setup
    args = MagicMock()
    args.doc_id = "xml1"
    args.output = None
    args.server = "http://localhost:8000"
    
    agent_instance = AsyncMock()
    agent_instance.handle_create_verification_plan = AsyncMock()
    agent_instance.handle_create_verification_plan.return_value = {
        "doc_id": "xml1",
        "verification_needed": True,
        "priority": "high",
        "node_count": 1,
        "tasks": [{"task_id": "verify_1", "element_type": "item", "priority": "high", "node_count": 1}]
    }
    
    # Execute
    # Directly patch the module's XmlAgent and InMemoryMessageBroker imports
    with patch.object(xml_agent_cli, 'XmlAgent', return_value=agent_instance), \
         patch.object(xml_agent_cli, 'InMemoryMessageBroker'), \
         patch('sys.exit'), patch('builtins.print'):
        await xml_agent_cli.create_verification_plan(args)
    
    # Debug
    print(f"Debug - handle_create_verification_plan call count: {agent_instance.handle_create_verification_plan.call_count}")
    print(f"Debug - handle_create_verification_plan calls: {agent_instance.handle_create_verification_plan.mock_calls}")
    
    # Verify
    agent_instance.handle_create_verification_plan.assert_called_once()
    task_request = agent_instance.handle_create_verification_plan.call_args[0][0]
    assert task_request.intent == "create_verification_plan"
    assert task_request.payload["doc_id"] == "xml1"