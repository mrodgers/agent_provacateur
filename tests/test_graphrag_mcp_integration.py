"""
Integration tests for GraphRAG MCP server.
"""

import pytest
import os
import asyncio
import subprocess
import time
import aiohttp
import signal

from agent_provocateur.graphrag_client import GraphRAGClient
from agent_provocateur.xml_graphrag_agent import XmlGraphRAGAgent
from agent_provocateur.xml_agent import XmlAgent
from agent_provocateur.a2a_models import TaskRequest

# Skip these tests if GraphRAG MCP is not enabled
pytestmark = pytest.mark.skipif(
    os.environ.get("GRAPHRAG_MCP_TESTS") != "1",
    reason="GraphRAG MCP tests not enabled, set GRAPHRAG_MCP_TESTS=1 to run"
)

# GraphRAG MCP server URL, default to localhost
GRAPHRAG_MCP_URL = os.environ.get("GRAPHRAG_MCP_URL", "http://localhost:8083")

# Sample XML content
SAMPLE_XML = """
<research>
    <section>
        <title>Climate Change Effects</title>
        <paragraph>
            Global temperatures have risen by 1.1°C since pre-industrial times,
            leading to various environmental impacts.
        </paragraph>
        <paragraph>
            The Paris Agreement aims to limit global warming to well below 2°C.
        </paragraph>
    </section>
</research>
"""

@pytest.fixture(scope="module")
async def graphrag_mcp_server():
    """Start GraphRAG MCP server for testing."""
    # Check if server is already running
    server_running = False
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GRAPHRAG_MCP_URL}/api/info") as response:
                if response.status == 200:
                    server_running = True
    except:
        pass
    
    if server_running:
        # Use existing server
        print(f"Using existing GraphRAG MCP server at {GRAPHRAG_MCP_URL}")
        yield
    else:
        # Start server for testing
        print("Starting GraphRAG MCP server for tests...")
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "scripts",
            "run_graphrag_mcp.sh"
        )
        
        if not os.path.exists(script_path):
            pytest.skip("GraphRAG MCP script not found, skipping test")
        
        # Make sure script is executable
        os.chmod(script_path, 0o755)
        
        # Start server
        process = subprocess.Popen([script_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        
        # Wait for server to start
        for _ in range(10):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{GRAPHRAG_MCP_URL}/api/info") as response:
                        if response.status == 200:
                            break
            except:
                pass
            time.sleep(1)
        else:
            # Kill process if server didn't start
            process.terminate()
            pytest.skip("Failed to start GraphRAG MCP server, skipping test")
        
        # Run tests
        yield
        
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

@pytest.fixture
async def graphrag_client():
    """Create GraphRAG client for tests."""
    return GraphRAGClient(base_url=GRAPHRAG_MCP_URL)

@pytest.mark.asyncio
async def test_graphrag_client_info(graphrag_mcp_server, graphrag_client):
    """Test getting GraphRAG MCP server info."""
    info = await graphrag_client.get_server_info()
    assert "name" in info
    assert "version" in info
    assert "tools" in info
    assert len(info["tools"]) > 0

@pytest.mark.asyncio
async def test_extract_entities(graphrag_mcp_server, graphrag_client):
    """Test extracting entities from text."""
    # Extract entities
    entities = await graphrag_client.extract_entities(
        "Climate change is a significant challenge. The Paris Agreement was signed in 2015."
    )
    
    # Check results
    assert len(entities) > 0
    assert any(e["name"].lower() == "climate change" for e in entities)
    assert any(e["name"].lower() == "paris agreement" for e in entities)

@pytest.mark.asyncio
async def test_get_sources_for_query(graphrag_mcp_server, graphrag_client):
    """Test getting sources for a query."""
    # Get sources
    sources, prompt = await graphrag_client.get_sources_for_query(
        "What are the effects of climate change?"
    )
    
    # Check results
    assert len(sources) > 0
    assert sources[0]["metadata"]["title"]
    assert sources[0]["relevance_score"] > 0
    assert "sources" in prompt.lower()

@pytest.mark.asyncio
async def test_xml_graphrag_agent_integration(graphrag_mcp_server):
    """Test XML GraphRAG agent integration."""
    # Create agent
    agent = XmlGraphRAGAgent(
        agent_id="test_xml_graphrag_agent",
        agent_type="xml_graphrag",
        capabilities=["xml_verification"]
    )
    
    # Mock XML document
    from agent_provocateur.models import XmlDocument, XmlNode
    xml_doc = XmlDocument(
        doc_id="test_doc",
        title="Test Document",
        content=SAMPLE_XML,
        doc_type="xml",
        root_element="research",
        researchable_nodes=[
            XmlNode(
                xpath="/research/section/paragraph[1]",
                element_name="paragraph",
                content="Global temperatures have risen by 1.1°C since pre-industrial times, leading to various environmental impacts.",
                verification_status="pending"
            ),
            XmlNode(
                xpath="/research/section/paragraph[2]",
                element_name="paragraph",
                content="The Paris Agreement aims to limit global warming to well below 2°C.",
                verification_status="pending"
            )
        ]
    )
    
    # Mock async_mcp_client
    agent.async_mcp_client = type('MockMcpClient', (), {})()
    agent.async_mcp_client.get_xml_document = asyncio.coroutine(lambda doc_id: xml_doc)
    
    # Initialize agent
    await agent.on_startup()
    
    # Test entity extraction
    task_request = TaskRequest(
        task_id="test_task",
        intent="extract_entities",
        source_agent="test_agent",
        target_agent="test_xml_graphrag_agent",
        payload={
            "doc_id": "test_doc",
            "use_graphrag": True
        }
    )
    
    result = await agent.handle_extract_entities(task_request)
    
    # Check results
    assert result["doc_id"] == "test_doc"
    assert len(result["entities"]) > 0
    assert result["extraction_method"] == "graphrag_mcp"
    assert any(e["name"].lower() == "climate change" for e in result["entities"]) or \
           any(e["name"].lower() == "global temperatures" for e in result["entities"]) or \
           any(e["name"].lower() == "paris agreement" for e in result["entities"])

@pytest.mark.asyncio
async def test_xml_graphrag_agent_fallback(graphrag_mcp_server):
    """Test XML GraphRAG agent fallback to base implementation."""
    # Create agent
    agent = XmlGraphRAGAgent(
        agent_id="test_xml_graphrag_agent",
        agent_type="xml_graphrag",
        capabilities=["xml_verification"]
    )
    
    # Mock XML document
    from agent_provocateur.models import XmlDocument, XmlNode
    xml_doc = XmlDocument(
        doc_id="test_doc",
        title="Test Document",
        content=SAMPLE_XML,
        doc_type="xml",
        root_element="research",
        researchable_nodes=[
            XmlNode(
                xpath="/research/section/paragraph[1]",
                element_name="paragraph",
                content="Global temperatures have risen by 1.1°C since pre-industrial times, leading to various environmental impacts.",
                verification_status="pending"
            )
        ]
    )
    
    # Mock async_mcp_client
    agent.async_mcp_client = type('MockMcpClient', (), {})()
    agent.async_mcp_client.get_xml_document = asyncio.coroutine(lambda doc_id: xml_doc)
    agent.async_mcp_client.find_agent_by_capability = asyncio.coroutine(lambda cap: None)
    
    # Modify GraphRAG client to force fallback
    agent.graphrag_client.extract_entities = asyncio.coroutine(lambda text: [][0])  # Will raise IndexError
    
    # Initialize agent
    await agent.on_startup()
    
    # Test entity extraction with fallback
    task_request = TaskRequest(
        task_id="test_task",
        intent="extract_entities",
        source_agent="test_agent",
        target_agent="test_xml_graphrag_agent",
        payload={
            "doc_id": "test_doc",
            "use_graphrag": True
        }
    )
    
    # Should not raise an exception
    result = await agent.handle_extract_entities(task_request)
    
    # Check that we got some result (likely from the base implementation)
    assert result["doc_id"] == "test_doc"
    assert "entities" in result