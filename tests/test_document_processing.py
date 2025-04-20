"""Tests for document processing functionality."""

import os
import unittest
import asyncio
import datetime
import json
import pytest

from agent_provocateur.models import (
    Document,
    DocumentContent,
    CodeDocument,
    StructuredDataDocument,
)

from agent_provocateur.agent_implementations import DocumentProcessingAgent


class TestDocumentProcessing(unittest.TestCase):
    """Test the document processing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = os.path.join(os.path.dirname(__file__), "test_data", "documents")
        self.now = datetime.datetime.now().isoformat()
        
        # Create test documents
        self.text_doc = self._create_text_document()
        self.code_doc = self._create_code_document()
        self.json_doc = self._create_json_document()
    
    def _create_text_document(self):
        """Create a test text document."""
        md_path = os.path.join(self.test_data_dir, "text_document.md")
        with open(md_path, "r") as f:
            content = f.read()
        
        return DocumentContent(
            doc_id="test_text_doc",
            doc_type="text",
            title="Sample Text Document",
            created_at=self.now,
            updated_at=self.now,
            markdown=content,
            html=f"<h1>Sample Text Document</h1><p>{content}</p>"
        )
    
    def _create_code_document(self):
        """Create a test code document."""
        code_path = os.path.join(self.test_data_dir, "code_document.py")
        with open(code_path, "r") as f:
            content = f.read()
        
        # Count lines in the file (excluding empty lines)
        line_count = len([line for line in content.split('\n') if line.strip()])
        
        return CodeDocument(
            doc_id="test_code_doc",
            doc_type="code",
            title="Example Agent Code",
            created_at=self.now,
            updated_at=self.now,
            content=content,
            language="python",
            line_count=line_count
        )
    
    def _create_json_document(self):
        """Create a test JSON document."""
        json_path = os.path.join(self.test_data_dir, "structured_data.json")
        with open(json_path, "r") as f:
            data = json.load(f)
        
        return StructuredDataDocument(
            doc_id="test_json_doc",
            doc_type="structured_data",
            title="Agent Configuration",
            created_at=self.now,
            updated_at=self.now,
            data=data,
            format="json"
        )
    
    def test_document_type_detection(self):
        """Test document type detection."""
        self.assertEqual(self.text_doc.doc_type, "text")
        self.assertEqual(self.code_doc.doc_type, "code")
        self.assertEqual(self.json_doc.doc_type, "structured_data")
    
    def test_text_document_content(self):
        """Test text document content access."""
        self.assertTrue("Introduction" in self.text_doc.markdown)
        self.assertTrue("Features" in self.text_doc.markdown)
        self.assertTrue("Conclusion" in self.text_doc.markdown)
    
    def test_code_document_content(self):
        """Test code document content access."""
        self.assertTrue("class ExampleAgent" in self.code_doc.content)
        self.assertTrue("def handle_message" in self.code_doc.content)
        self.assertTrue("def main" in self.code_doc.content)
        self.assertEqual(self.code_doc.language, "python")
    
    def test_json_document_content(self):
        """Test JSON document content access."""
        self.assertTrue("agent_types" in self.json_doc.data)
        self.assertTrue("configuration" in self.json_doc.data)
        self.assertTrue("message_formats" in self.json_doc.data)
        self.assertEqual(len(self.json_doc.data["agent_types"]), 3)
        self.assertEqual(self.json_doc.data["configuration"]["retry_count"], 3)
    
    @pytest.mark.asyncio
    async def test_document_summary_methods(self):
        """Test the document summary methods."""
        # Create a document processing agent instance
        agent = DocumentProcessingAgent(agent_id="test_doc_processor")
        
        # Text document summary
        text_summary = await agent._summarize_text_document(self.text_doc)
        self.assertIn("summary", text_summary)
        self.assertIn("doc_id", text_summary)
        self.assertIn("doc_type", text_summary)
        self.assertIn("word_count", text_summary)
        
        # Code document summary
        code_summary = await agent._summarize_code_document(self.code_doc)
        self.assertIn("summary", code_summary)
        self.assertIn("language", code_summary)
        self.assertIn("line_count", code_summary)
        
        # JSON document summary
        json_summary = await agent._summarize_structured_data_document(self.json_doc)
        self.assertIn("summary", json_summary)
        self.assertIn("format", json_summary)
        self.assertIn("top_level_keys", json_summary)
        self.assertIn("agent_types", json_summary["top_level_keys"])


if __name__ == "__main__":
    unittest.main()