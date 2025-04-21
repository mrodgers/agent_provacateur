"""Tests for XML agent source attribution functionality."""

import unittest
import asyncio
import uuid
import datetime
from unittest.mock import MagicMock, patch

from agent_provocateur.xml_agent import XmlAgent
from agent_provocateur.models import XmlNode, Source, SourceType
from agent_provocateur.a2a_models import TaskRequest, TaskStatus


class TestXmlAgentAttribution(unittest.TestCase):
    """Tests for XML agent source attribution."""

    def setUp(self):
        """Set up test environment."""
        self.agent = XmlAgent(agent_id="test-xml-agent")
        self.agent.async_mcp_client = MagicMock()

    def test_add_source_attribution(self):
        """Test adding a source attribution to an XmlNode."""
        # Create an XmlNode
        node = XmlNode(
            xpath="/document/section/para[1]",
            element_name="para",
            content="This is a test paragraph."
        )
        
        # Test source dictionary
        source_dict = {
            "title": "Test Source",
            "url": "https://example.com/test",
            "type": "web"
        }
        
        # Add source attribution
        updated_node = self.agent._add_source_attribution(node, source_dict)
        
        # Verify source was added
        self.assertEqual(len(updated_node.sources), 1)
        self.assertEqual(updated_node.sources[0].title, "Test Source")
        self.assertEqual(updated_node.sources[0].url, "https://example.com/test")
        self.assertEqual(updated_node.sources[0].source_type, SourceType.WEB)
        
        # Check that a source_id was generated
        self.assertIsNotNone(updated_node.sources[0].source_id)

    def test_add_source_object(self):
        """Test adding a Source object to an XmlNode."""
        # Create an XmlNode
        node = XmlNode(
            xpath="/document/section/para[2]",
            element_name="para",
            content="This is another test paragraph."
        )
        
        # Create a Source object
        source = Source(
            source_id=str(uuid.uuid4()),
            source_type=SourceType.DOCUMENT,
            title="Document Source",
            doc_id="doc123",
            confidence=0.8
        )
        
        # Add source to node
        updated_node = self.agent._add_source_attribution(node, source)
        
        # Verify source was added
        self.assertEqual(len(updated_node.sources), 1)
        self.assertEqual(updated_node.sources[0].title, "Document Source")
        self.assertEqual(updated_node.sources[0].source_type, SourceType.DOCUMENT)
        self.assertEqual(updated_node.sources[0].doc_id, "doc123")
        self.assertEqual(updated_node.sources[0].confidence, 0.8)

    def test_add_multiple_sources(self):
        """Test adding multiple sources to an XmlNode."""
        # Create an XmlNode
        node = XmlNode(
            xpath="/document/section/para[3]",
            element_name="para",
            content="This is a third test paragraph."
        )
        
        # Create multiple source dictionaries
        sources = [
            {
                "title": "Primary Source",
                "url": "https://example.com/primary",
                "type": "web"
            },
            {
                "title": "Secondary Source",
                "url": "https://example.com/secondary",
                "type": "web"
            },
            {
                "title": "Tertiary Source",
                "doc_id": "doc456",
                "type": "document"
            }
        ]
        
        # Add multiple sources
        updated_node = self.agent._add_multiple_sources(node, sources)
        
        # Verify all sources were added
        self.assertEqual(len(updated_node.sources), 3)
        
        # Verify confidence values are decreasing by position
        self.assertGreater(updated_node.sources[0].confidence, updated_node.sources[1].confidence)
        self.assertGreater(updated_node.sources[1].confidence, updated_node.sources[2].confidence)
        
        # Verify source types
        self.assertEqual(updated_node.sources[0].source_type, SourceType.WEB)
        self.assertEqual(updated_node.sources[1].source_type, SourceType.WEB)
        self.assertEqual(updated_node.sources[2].source_type, SourceType.DOCUMENT)

    def test_handle_update_node_status_with_sources(self):
        """Test update node status handler with sources."""
        # Create task request
        task_request = TaskRequest(
            task_id="test-task",
            intent="update_node_status",
            payload={
                "doc_id": "doc123",
                "xpath": "/document/section/para[1]",
                "status": "verified",
                "verification_data": {
                    "confidence": 0.85,
                    "sources": [
                        {
                            "title": "Web Source",
                            "url": "https://example.com/source",
                            "type": "web"
                        }
                    ]
                }
            },
            source_agent="test-agent",
            target_agent="xml-agent"
        )
        
        # Call handler using synchronous event loop
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(self.agent.handle_update_node_status(task_request))
        loop.close()
        
        # Verify result
        self.assertEqual(result["doc_id"], "doc123")
        self.assertEqual(result["xpath"], "/document/section/para[1]")
        self.assertEqual(result["new_status"], "verified")
        self.assertIsNotNone(result["sources"])
        self.assertEqual(len(result["sources"]), 1)


if __name__ == "__main__":
    unittest.main()