"""Tests for the XML CLI validation functionality."""

import os
import json
import pytest
import asyncio
from unittest.mock import patch, MagicMock

from agent_provocateur.a2a_models import TaskRequest
from agent_provocateur.xml_agent import XmlAgent
from scripts.xml_agent_cli import validate_xml_schema


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
def mock_args_valid():
    """Create mock args for CLI testing."""
    args = MagicMock()
    args.file = "test_data/xml_documents/docbook_test.xml"
    args.doc_id = None
    args.schema = "docbook"
    args.schema_url = None
    args.schema_type = "xsd"
    args.validate_entities = True
    args.validate_attribution = True
    args.json = False
    args.server = "http://localhost:8000"
    return args


@pytest.fixture
def mock_args_invalid():
    """Create mock args for CLI testing with invalid document."""
    args = MagicMock()
    args.file = "test_data/xml_documents/invalid_docbook.xml"
    args.doc_id = None
    args.schema = "docbook"
    args.schema_url = None
    args.schema_type = "xsd"
    args.validate_entities = True
    args.validate_attribution = True
    args.json = False
    args.server = "http://localhost:8000"
    return args


class TestXmlCliValidation:
    """Test XML CLI validation functionality."""
    
    @patch('scripts.xml_agent_cli.XmlAgent')
    @patch('builtins.open')
    @patch('builtins.print')
    @patch('sys.exit')
    @pytest.mark.asyncio
    async def test_validate_valid_docbook(self, mock_exit, mock_print, mock_open, mock_agent_class, 
                                         mock_args_valid, docbook_test_xml):
        """Test validation of valid DocBook file."""
        # Setup mocks
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        mock_open().__enter__().read.return_value = docbook_test_xml
        
        # Setup mock response
        mock_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "schema_url": "http://docbook.org/xml/5.0/xsd/docbook.xsd",
            "schema_type": "xsd",
            "schema_validation_performed": True
        }
        
        mock_agent.handle_validate_xml_output.return_value = mock_result
        
        # Call function
        await validate_xml_schema(mock_args_valid)
        
        # Verify agent was called with correct parameters
        mock_agent_class.assert_called_once()
        mock_agent.handle_validate_xml_output.assert_called_once()
        
        # Verify print was called with success message
        mock_print.assert_any_call("\nDocument is valid against the specified schema.")
        
        # Verify sys.exit was not called
        mock_exit.assert_not_called()
    
    @patch('scripts.xml_agent_cli.XmlAgent')
    @patch('builtins.open')
    @patch('builtins.print')
    @patch('sys.exit')
    @pytest.mark.asyncio
    async def test_validate_invalid_docbook(self, mock_exit, mock_print, mock_open, mock_agent_class, 
                                          mock_args_invalid, invalid_docbook_xml):
        """Test validation of invalid DocBook file."""
        # Setup mocks
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        mock_open().__enter__().read.return_value = invalid_docbook_xml
        
        # Setup mock response
        mock_result = {
            "valid": False,
            "errors": ["XML syntax error: Entity 'myentity' not defined"],
            "warnings": ["No namespace declaration found"],
            "schema_url": "http://docbook.org/xml/5.0/xsd/docbook.xsd",
            "schema_type": "xsd",
            "schema_validation_performed": False
        }
        
        mock_agent.handle_validate_xml_output.return_value = mock_result
        
        # Call function
        await validate_xml_schema(mock_args_invalid)
        
        # Verify agent was called with correct parameters
        mock_agent_class.assert_called_once()
        mock_agent.handle_validate_xml_output.assert_called_once()
        
        # Verify print was called with error message
        mock_print.assert_any_call("\nDocument is not valid against the specified schema.")
        
        # Verify error message was printed
        mock_print.assert_any_call("1. XML syntax error: Entity 'myentity' not defined")
        
        # Verify sys.exit was not called
        mock_exit.assert_not_called()
    
    @patch('scripts.xml_agent_cli.XmlAgent')
    @patch('builtins.open')
    @patch('json.dumps')
    @patch('builtins.print')
    @pytest.mark.asyncio
    async def test_validate_with_json_output(self, mock_print, mock_json_dumps, mock_open, 
                                           mock_agent_class, mock_args_valid, docbook_test_xml):
        """Test validation with JSON output format."""
        # Setup mocks
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        mock_args_valid.json = True
        
        mock_open().__enter__().read.return_value = docbook_test_xml
        
        # Setup mock response
        mock_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "schema_url": "http://docbook.org/xml/5.0/xsd/docbook.xsd",
            "schema_type": "xsd",
            "schema_validation_performed": True
        }
        
        mock_agent.handle_validate_xml_output.return_value = mock_result
        mock_json_dumps.return_value = '{"valid": true}'
        
        # Call function
        await validate_xml_schema(mock_args_valid)
        
        # Verify json.dumps was called with the result
        mock_json_dumps.assert_called_once_with(mock_result, indent=2)
        
        # Verify print was called with the JSON string
        mock_print.assert_called_once_with('{"valid": true}')