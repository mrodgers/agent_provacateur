"""Integration tests for the Agent Provocateur system."""

import os
import sys
import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add necessary paths to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestApiIntegration:
    """Test integration between frontend and backend APIs."""
    
    @pytest.fixture
    def xml_content(self):
        """Return a sample XML document."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<test>
  <title>Integration Test Document</title>
  <content>This is a test document for integration testing.</content>
  <items>
    <item id="1">First item</item>
    <item id="2">Second item</item>
  </items>
</test>
"""
    
    @pytest.fixture
    def mock_frontend_client(self):
        """Create a mock frontend client."""
        from fastapi import FastAPI, UploadFile, Form, File
        from fastapi.responses import JSONResponse
        from fastapi.testclient import TestClient
        import uuid
        from datetime import datetime
        
        app = FastAPI()
        
        # In-memory document store
        document_store = {
            "test1": {
                "doc_id": "test1",
                "title": "Test Document",
                "doc_type": "xml",
                "created_at": datetime.now().isoformat(),
                "metadata": {}
            }
        }
        
        # Upload directory
        upload_dir = tempfile.mkdtemp()
        
        @app.get("/api/health")
        def health_check():
            return {"status": "ok", "backend_url": "http://localhost:8000"}
        
        @app.get("/api/documents")
        def get_documents():
            return list(document_store.values())
        
        @app.post("/documents/upload")
        async def upload_document(
            title: str = Form(...),
            file: UploadFile = File(...)
        ):
            # Generate document ID
            doc_id = f"doc_{uuid.uuid4().hex[:8]}"
            
            # Read file content
            content = await file.read()
            
            # Save to upload directory
            file_path = os.path.join(upload_dir, f"{doc_id}.xml")
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Add to document store
            document_store[doc_id] = {
                "doc_id": doc_id,
                "title": title,
                "doc_type": "xml",
                "created_at": datetime.now().isoformat(),
                "metadata": {
                    "filename": file.filename,
                    "content_type": file.content_type
                }
            }
            
            return {
                "success": True,
                "doc_id": doc_id,
                "title": title
            }
        
        client = TestClient(app)
        return client, upload_dir, document_store
    
    @pytest.fixture
    def mock_backend_client(self):
        """Create a mock backend client."""
        from fastapi import FastAPI, Body
        from fastapi.testclient import TestClient
        import uuid
        from datetime import datetime
        
        app = FastAPI()
        
        # Document store
        document_store = {
            "xml1": {
                "doc_id": "xml1",
                "doc_type": "xml",
                "title": "Backend Test Document",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "content": "<test>Test content</test>",
                "root_element": "test",
                "namespaces": {},
                "researchable_nodes": []
            }
        }
        
        @app.get("/documents")
        def list_documents(doc_type: str = None):
            if doc_type:
                return [doc for doc in document_store.values() if doc["doc_type"] == doc_type]
            return list(document_store.values())
        
        @app.get("/documents/{doc_id}")
        def get_document(doc_id: str):
            if doc_id not in document_store:
                return JSONResponse(
                    status_code=404,
                    content={"detail": f"Document {doc_id} not found"}
                )
            return document_store[doc_id]
        
        @app.post("/xml/upload")
        def upload_xml(
            xml_content: str = Body(...),
            title: str = Body(...)
        ):
            # Generate document ID
            doc_id = f"xml{len(document_store) + 1}"
            now = datetime.now().isoformat()
            
            # Create document
            document_store[doc_id] = {
                "doc_id": doc_id,
                "doc_type": "xml",
                "title": title,
                "created_at": now,
                "updated_at": now,
                "content": xml_content,
                "root_element": "test",
                "namespaces": {},
                "researchable_nodes": []
            }
            
            return document_store[doc_id]
        
        client = TestClient(app)
        return client, document_store
    
    def test_frontend_list_documents(self, mock_frontend_client):
        """Test the frontend API can list documents."""
        client, _, _ = mock_frontend_client
        
        response = client.get("/api/documents")
        assert response.status_code == 200
        
        documents = response.json()
        assert isinstance(documents, list)
        assert len(documents) > 0
        assert "doc_id" in documents[0]
    
    def test_backend_list_documents(self, mock_backend_client):
        """Test the backend API can list documents."""
        client, _ = mock_backend_client
        
        response = client.get("/documents")
        assert response.status_code == 200
        
        documents = response.json()
        assert isinstance(documents, list)
        assert len(documents) > 0
        assert "doc_id" in documents[0]
    
    def test_upload_and_retrieve(self, mock_frontend_client, mock_backend_client, xml_content):
        """Test uploading a document via frontend and retrieving from backend."""
        frontend_client, upload_dir, frontend_store = mock_frontend_client
        backend_client, backend_store = mock_backend_client
        
        # Create a temporary XML file
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as temp_file:
            temp_file.write(xml_content.encode("utf-8"))
            temp_path = temp_file.name
        
        try:
            # Upload via frontend
            with open(temp_path, "rb") as f:
                response = frontend_client.post(
                    "/documents/upload",
                    files={"file": ("test.xml", f, "application/xml")},
                    data={"title": "Integration Test"}
                )
            
            assert response.status_code == 200
            upload_result = response.json()
            assert upload_result["success"] is True
            
            frontend_doc_id = upload_result["doc_id"]
            
            # Verify document exists in frontend store
            assert frontend_doc_id in frontend_store
            
            # Now, simulate forwarding to backend
            with open(os.path.join(upload_dir, f"{frontend_doc_id}.xml"), "r") as f:
                xml_content_to_send = f.read()
            
            # Send to backend
            backend_response = backend_client.post(
                "/xml/upload",
                json={
                    "xml_content": xml_content_to_send,
                    "title": "Integration Test"
                }
            )
            
            assert backend_response.status_code == 200
            backend_result = backend_response.json()
            
            # Verify document in backend
            backend_doc_id = backend_result["doc_id"]
            assert backend_doc_id in backend_store
            
            # Verify document content matches
            assert backend_store[backend_doc_id]["content"] == xml_content_to_send
        
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            shutil.rmtree(upload_dir)