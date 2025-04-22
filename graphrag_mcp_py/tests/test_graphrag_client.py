"""
Test script for GraphRAG client integration.
"""

import sys
import os
import asyncio
import json

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the client implementation
from src.api import app
from fastapi.testclient import TestClient

# Create a test client
client = TestClient(app)

def test_basic_functionality():
    """Test basic functionality of the GraphRAG MCP API."""
    # Test the info endpoint
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "GraphRAG MCP Server"
    
    # Test entity extraction
    response = client.post(
        "/api/tools/graphrag_extract_entities",
        json={"text": "Climate change is a global challenge."}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert len(data["entities"]) > 0
    
    # Test source indexing
    response = client.post(
        "/api/tools/graphrag_index_source",
        json={
            "source": {
                "source_id": "src_test123",
                "source_type": "document",
                "title": "Test Document",
                "content": "This is a test document about climate change.",
                "confidence_score": 0.8,
                "reliability_score": 0.7,
                "retrieval_date": "2025-04-21T00:00:00Z"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "doc_id" in data
    
    # Test querying
    response = client.post(
        "/api/tools/graphrag_query",
        json={
            "query": "What is climate change?",
            "options": {
                "max_results": 5,
                "min_confidence": 0.1
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "sources" in data
    
    # Print success message
    print("✅ All GraphRAG MCP API tests passed!")

if __name__ == "__main__":
    test_basic_functionality()