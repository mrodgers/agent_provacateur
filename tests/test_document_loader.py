"""Tests for document loading and processing."""

import os
import unittest
import datetime

from agent_provocateur.models import (
    Document,
    DocumentContent,
    CodeDocument,
    StructuredDataDocument,
)


class TestDocumentLoader(unittest.TestCase):
    """Test the document loading functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = os.path.join(os.path.dirname(__file__), "test_data", "documents")
        self.now = datetime.datetime.now().isoformat()
    
    def test_load_text_document(self):
        """Test loading a text document."""
        # Load text document file
        md_path = os.path.join(self.test_data_dir, "text_document.md")
        with open(md_path, "r") as f:
            content = f.read()
        
        # Create document model
        doc = DocumentContent(
            doc_id="test_text_doc",
            doc_type="text",
            title="Sample Text Document",
            created_at=self.now,
            updated_at=self.now,
            markdown=content,
            html=f"<h1>Sample Text Document</h1><p>{content}</p>"
        )
        
        # Verify document content
        self.assertEqual(doc.doc_id, "test_text_doc")
        self.assertEqual(doc.doc_type, "text")
        self.assertEqual(doc.title, "Sample Text Document")
        self.assertTrue("Introduction" in doc.markdown)
        self.assertTrue("Usage" in doc.markdown)
        self.assertTrue("<h1>" in doc.html)
    
    def test_load_code_document(self):
        """Test loading a code document."""
        # Load code document file
        code_path = os.path.join(self.test_data_dir, "code_document.py")
        with open(code_path, "r") as f:
            content = f.read()
        
        # Count lines in the file (excluding empty lines)
        line_count = len([line for line in content.split('\n') if line.strip()])
        
        # Create document model
        doc = CodeDocument(
            doc_id="test_code_doc",
            doc_type="code",
            title="Example Agent Code",
            created_at=self.now,
            updated_at=self.now,
            content=content,
            language="python",
            line_count=line_count
        )
        
        # Verify document content
        self.assertEqual(doc.doc_id, "test_code_doc")
        self.assertEqual(doc.doc_type, "code")
        self.assertEqual(doc.language, "python")
        self.assertTrue("class ExampleAgent" in doc.content)
        self.assertTrue("handle_message" in doc.content)
    
    def test_load_structured_data_document(self):
        """Test loading a structured data document."""
        # Load structured data file
        json_path = os.path.join(self.test_data_dir, "structured_data.json")
        with open(json_path, "r") as f:
            import json
            data = json.load(f)
        
        # Create document model
        doc = StructuredDataDocument(
            doc_id="test_json_doc",
            doc_type="structured_data",
            title="Agent Configuration",
            created_at=self.now,
            updated_at=self.now,
            data=data,
            format="json"
        )
        
        # Verify document content
        self.assertEqual(doc.doc_id, "test_json_doc")
        self.assertEqual(doc.doc_type, "structured_data")
        self.assertEqual(doc.format, "json")
        self.assertTrue("agent_types" in doc.data)
        self.assertEqual(len(doc.data["agent_types"]), 3)
        self.assertEqual(doc.data["configuration"]["default_timeout"], 30)
    
    def test_yaml_document(self):
        """Test loading a YAML document."""
        # Load YAML file
        yaml_path = os.path.join(self.test_data_dir, "sample_config.yaml")
        
        try:
            import yaml
            with open(yaml_path, "r") as f:
                data = yaml.safe_load(f)
            
            # Create document model
            doc = StructuredDataDocument(
                doc_id="test_yaml_doc",
                doc_type="structured_data",
                title="Agent Provocateur Configuration",
                created_at=self.now,
                updated_at=self.now,
                data=data,
                format="yaml"
            )
            
            # Verify document content
            self.assertEqual(doc.doc_id, "test_yaml_doc")
            self.assertEqual(doc.doc_type, "structured_data")
            self.assertEqual(doc.format, "yaml")
            self.assertTrue("agents" in doc.data)
            self.assertTrue("server" in doc.data)
            self.assertEqual(doc.data["server"]["port"], 8000)
            
        except ImportError:
            self.skipTest("PyYAML not installed, skipping YAML test")


if __name__ == "__main__":
    unittest.main()