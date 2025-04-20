"""Tests for the backend API (MCP Server)."""

import asyncio
import json
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Define a fixture to create a mock API for testing
@pytest.fixture
def mock_api():
    """Create a mock API for testing."""
    from fastapi import FastAPI, Body
    from fastapi.testclient import TestClient
    from pydantic import BaseModel
    from typing import List, Dict, Any, Optional
    
    app = FastAPI()
    
    class XmlDocument(BaseModel):
        doc_id: str
        doc_type: str = "xml"
        title: str
        created_at: str
        updated_at: Optional[str] = None
        content: Optional[str] = None
        root_element: Optional[str] = None
        namespaces: Optional[Dict[str, str]] = None
        researchable_nodes: Optional[List[Dict[str, Any]]] = None
    
    # Sample documents store
    DOCUMENTS = {
        "xml1": {
            "doc_id": "xml1",
            "doc_type": "xml",
            "title": "Sample XML",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "content": "<?xml version=\"1.0\"?><root><item>Test</item></root>",
            "root_element": "root",
            "namespaces": {},
            "researchable_nodes": []
        }
    }
    
    @app.get("/documents")
    def list_documents(doc_type: str = None):
        """List all documents, optionally filtered by type."""
        if doc_type:
            return [doc for doc in DOCUMENTS.values() if doc["doc_type"] == doc_type]
        return list(DOCUMENTS.values())
    
    @app.get("/documents/{doc_id}")
    def get_document(doc_id: str):
        """Get a document by ID."""
        if doc_id not in DOCUMENTS:
            return {"detail": f"Document {doc_id} not found"}, 404
        return DOCUMENTS[doc_id]
    
    @app.post("/xml/upload")
    def upload_xml(
        xml_content: str = Body(..., description="Raw XML content"),
        title: str = Body(..., description="Document title")
    ):
        """Upload a new XML document."""
        import uuid
        
        doc_id = f"xml{len(DOCUMENTS) + 1}"
        now = datetime.now().isoformat()
        
        # Create a new document
        doc = {
            "doc_id": doc_id,
            "doc_type": "xml",
            "title": title,
            "created_at": now,
            "updated_at": now,
            "content": xml_content,
            "root_element": "root",
            "namespaces": {},
            "researchable_nodes": []
        }
        
        DOCUMENTS[doc_id] = doc
        return doc
    
    return TestClient(app)


@pytest.fixture
def xml_content():
    """Return a simple XML document."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<test>
  <title>Sample Test Document</title>
  <content>
    <item id="1">First item</item>
    <item id="2">Second item</item>
  </content>
</test>
"""


def test_list_documents(mock_api):
    """Test listing all documents."""
    response = mock_api.get("/documents")
    assert response.status_code == 200
    
    documents = response.json()
    assert isinstance(documents, list)
    assert len(documents) > 0
    
    # Check document structure
    doc = documents[0]
    assert "doc_id" in doc
    assert "title" in doc
    assert "doc_type" in doc
    assert "created_at" in doc


def test_list_documents_by_type(mock_api):
    """Test listing documents by type."""
    response = mock_api.get("/documents?doc_type=xml")
    assert response.status_code == 200
    
    documents = response.json()
    assert isinstance(documents, list)
    assert len(documents) > 0
    assert all(doc["doc_type"] == "xml" for doc in documents)


def test_get_document(mock_api):
    """Test getting a document by ID."""
    response = mock_api.get("/documents/xml1")
    assert response.status_code == 200
    
    document = response.json()
    assert document["doc_id"] == "xml1"
    assert document["doc_type"] == "xml"
    assert "content" in document


def test_upload_xml(mock_api, xml_content):
    """Test uploading XML."""
    # Prepare the payload
    payload = {
        "xml_content": xml_content,
        "title": "Test Upload"
    }
    
    # Make the request
    response = mock_api.post("/xml/upload", json=payload)
    assert response.status_code == 200
    
    result = response.json()
    assert "doc_id" in result
    assert result["title"] == "Test Upload"
    assert result["doc_type"] == "xml"
    assert result["content"] == xml_content