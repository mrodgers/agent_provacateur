import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent_provocateur.mcp_server import create_app
from src.agent_provocateur.models import JiraTicket, SearchResults


@pytest.fixture
def client():
    """Test client for the MCP server."""
    app = create_app()
    return TestClient(app)


def test_server_config(client):
    """Test server configuration endpoint."""
    # Get default config
    response = client.get("/config")
    assert response.status_code == 200
    config = response.json()
    assert config["latency_min_ms"] == 0
    assert config["latency_max_ms"] == 500
    assert config["error_rate"] == 0.0
    
    # Update config
    new_config = {
        "latency_min_ms": 100,
        "latency_max_ms": 1000,
        "error_rate": 0.1,
    }
    response = client.post("/config", json=new_config)
    assert response.status_code == 200
    config = response.json()
    assert config["latency_min_ms"] == 100
    assert config["latency_max_ms"] == 1000
    assert config["error_rate"] == 0.1


def test_fetch_ticket(client):
    """Test fetching a JIRA ticket."""
    # Set zero latency for tests
    client.post("/config", json={"latency_min_ms": 0, "latency_max_ms": 0})
    
    # Test valid ticket
    response = client.get("/jira/ticket/AP-1")
    assert response.status_code == 200
    ticket = JiraTicket(**response.json())
    assert ticket.id == "AP-1"
    assert ticket.status == "Open"
    
    # Test invalid ticket
    response = client.get("/jira/ticket/INVALID")
    assert response.status_code == 404


def test_search_web(client):
    """Test web search."""
    # Set zero latency for tests
    client.post("/config", json={"latency_min_ms": 0, "latency_max_ms": 0})
    
    # Test search with results
    response = client.get("/search", params={"query": "agent protocol"})
    assert response.status_code == 200
    results = SearchResults(**response.json())
    assert len(results.results) > 0
    assert "protocol" in results.results[0].title.lower()
    
    # Test search with no results
    response = client.get("/search", params={"query": "xyzxyzxyz"})
    assert response.status_code == 200
    results = SearchResults(**response.json())
    assert len(results.results) == 0


if __name__ == "__main__":
    # Run the tests directly
    import pytest
    
    exit_code = pytest.main(["-xvs", __file__])
    print("Tests passed!" if exit_code == 0 else f"Tests failed with code {exit_code}")
    sys.exit(exit_code)