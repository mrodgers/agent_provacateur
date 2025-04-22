"""
Test script for GraphRAG client HTTP integration.
"""

import sys
import os
import subprocess
import time
import requests
import json
import unittest

class GraphRAGClientHTTPTest(unittest.TestCase):
    """Test GraphRAG client integration via HTTP."""
    
    @classmethod
    def setUpClass(cls):
        """Start the server before running tests."""
        # Start the server in the background
        cls.server_process = subprocess.Popen(
            ["./scripts/run.sh"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        )
        
        # Wait for the server to start
        time.sleep(5)
        
        # Check if the server is running
        cls.server_url = "http://localhost:8083"
        try:
            response = requests.get(f"{cls.server_url}/api/info")
            response.raise_for_status()
            print("Server started successfully")
        except Exception as e:
            print(f"Error starting server: {e}")
            cls.tearDownClass()
            raise
    
    @classmethod
    def tearDownClass(cls):
        """Stop the server after running tests."""
        # Stop the server
        subprocess.run(
            ["./scripts/stop.sh"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        )
        
        # Terminate the process if still running
        if cls.server_process:
            cls.server_process.terminate()
            cls.server_process.wait(timeout=5)
    
    def test_info_endpoint(self):
        """Test the info endpoint."""
        response = requests.get(f"{self.server_url}/api/info")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "GraphRAG MCP Server")
        self.assertTrue("tools" in data)
    
    def test_entity_extraction(self):
        """Test entity extraction."""
        response = requests.post(
            f"{self.server_url}/api/tools/graphrag_extract_entities",
            json={"text": "Climate change is a global challenge."}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(len(data["entities"]) > 0)
        
        # Check for expected entities
        entity_names = [entity["name"].lower() for entity in data["entities"]]
        self.assertTrue("climate" in entity_names or "climate change" in entity_names)
    
    def test_source_indexing_and_query(self):
        """Test source indexing and querying."""
        # Index a source
        index_response = requests.post(
            f"{self.server_url}/api/tools/graphrag_index_source",
            json={
                "source": {
                    "source_id": "src_test_integration",
                    "source_type": "document",
                    "title": "Integration Test Document",
                    "content": "This is a test document about climate change and its effects on global ecosystems.",
                    "confidence_score": 0.9,
                    "reliability_score": 0.8,
                    "retrieval_date": "2025-04-21T00:00:00Z"
                }
            }
        )
        self.assertEqual(index_response.status_code, 200)
        index_data = index_response.json()
        self.assertTrue(index_data["success"])
        self.assertTrue("doc_id" in index_data)
        
        # Query the indexed source
        query_response = requests.post(
            f"{self.server_url}/api/tools/graphrag_query",
            json={
                "query": "What is climate change?",
                "options": {
                    "max_results": 5,
                    "min_confidence": 0.1
                }
            }
        )
        self.assertEqual(query_response.status_code, 200)
        query_data = query_response.json()
        self.assertTrue(query_data["success"])
        self.assertTrue("sources" in query_data)
        self.assertTrue(len(query_data["sources"]) > 0)
        
        # Check if our document is in the results
        found = False
        for source in query_data["sources"]:
            if source["metadata"]["title"] == "Integration Test Document":
                found = True
                break
        self.assertTrue(found, "Our indexed document should be returned in query results")


if __name__ == "__main__":
    unittest.main()