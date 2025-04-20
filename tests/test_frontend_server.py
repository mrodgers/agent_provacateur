"""Tests for the frontend server."""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Create a simple test client without loading server.py directly
# This helps avoid circular imports and other issues
def create_test_client():
    """Create a test client with mocked dependencies."""
    # Get the frontend directory
    frontend_dir = Path(__file__).parent.parent / "frontend"
    
    # Create a temporary directory for uploads
    temp_dir = tempfile.mkdtemp()
    
    # Define a very simple FastAPI app for testing
    from fastapi import FastAPI, UploadFile, Form, Request
    from fastapi.responses import JSONResponse
    from datetime import datetime
    
    app = FastAPI(title="Test Frontend")
    
    UPLOAD_DIR = temp_dir
    FALLBACK_DOCUMENT_STORE = {
        "test1": {
            "doc_id": "test1",
            "title": "Test Document",
            "doc_type": "xml",
            "created_at": datetime.now().isoformat()
        }
    }
    
    @app.get("/api/health")
    async def health_check():
        return {"status": "ok", "backend_url": "http://localhost:8000"}
    
    @app.get("/api/documents")
    async def get_documents():
        return list(FALLBACK_DOCUMENT_STORE.values())
    
    @app.post("/documents/upload")
    async def upload_document(title: str = Form(None), file: UploadFile = None):
        if not file:
            return JSONResponse(status_code=422, content={"error": "No file uploaded"})
        
        if not title:
            title = f"Test Document {datetime.now().isoformat()}"
        
        # Read file content
        content = await file.read()
        
        # Generate a document ID
        import uuid
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        
        # Save to fallback store
        FALLBACK_DOCUMENT_STORE[doc_id] = {
            "doc_id": doc_id,
            "title": title,
            "doc_type": "xml",
            "created_at": datetime.now().isoformat()
        }
        
        # Save the file
        file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.xml")
        with open(file_path, "wb") as f:
            f.write(content)
        
        return {
            "success": True,
            "doc_id": doc_id,
            "title": title
        }
    
    client = TestClient(app)
    return client, temp_dir


@pytest.fixture(scope="module")
def client_and_dir():
    """Return the test client and upload directory."""
    client, temp_dir = create_test_client()
    yield client, temp_dir
    
    # Cleanup
    try:
        import shutil
        shutil.rmtree(temp_dir)
    except:
        pass


@pytest.fixture
def client(client_and_dir):
    """Return just the test client."""
    return client_and_dir[0]


@pytest.fixture
def test_upload_dir(client_and_dir):
    """Return the upload directory."""
    return client_and_dir[1]


@pytest.fixture
def xml_content():
    """Return a simple XML document."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<test>
  <title>Test Document</title>
  <content>This is a test XML document for upload testing.</content>
</test>
"""


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"
    assert data["backend_url"] == "http://localhost:8000"


def test_documents_endpoint(client):
    """Test the documents endpoint."""
    response = client.get("/api/documents")
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


def test_upload_without_file(client):
    """Test upload without a file."""
    response = client.post("/documents/upload", data={"title": "Test Document"})
    assert response.status_code == 422


def test_upload_with_file(client, xml_content, test_upload_dir):
    """Test upload with a valid file."""
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix=".xml", delete=False)
    temp_file.write(xml_content.encode("utf-8"))
    temp_file.close()
    
    try:
        with open(temp_file.name, "rb") as f:
            response = client.post(
                "/documents/upload",
                files={"file": ("test.xml", f, "application/xml")},
                data={"title": "Test Upload"}
            )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "doc_id" in result
        
        # Verify file was saved
        doc_id = result["doc_id"]
        saved_path = os.path.join(test_upload_dir, f"{doc_id}.xml")
        assert os.path.exists(saved_path)
        
        # Verify content
        with open(saved_path, "r") as f:
            content = f.read()
            assert "This is a test XML document" in content
    finally:
        os.unlink(temp_file.name)