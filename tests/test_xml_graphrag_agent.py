"""Tests for the enhanced XML GraphRAG agent with entity linking capabilities."""

import os
import asyncio
import re
import pytest
import datetime
import xml.etree.ElementTree as ET
from unittest.mock import AsyncMock, MagicMock, patch, call

from agent_provocateur.xml_graphrag_agent import XmlGraphRAGAgent
from agent_provocateur.a2a_models import TaskRequest, TaskResult, TaskStatus
from agent_provocateur.graphrag_client import GraphRAGClient
from agent_provocateur.entity_linking import Entity, EntityType, RelationType
from agent_provocateur.models import XmlDocument, XmlNode, Source, SourceType


@pytest.fixture
def sample_xml():
    """Sample XML content for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<article>
    <title>Artificial Intelligence and Climate Change</title>
    <abstract>
        <para>This article explores how Artificial Intelligence (AI) technologies
        can help address climate change challenges. Organizations like Google and
        OpenAI are developing solutions to monitor environmental impacts and optimize
        energy usage.</para>
    </abstract>
    <section>
        <title>Introduction</title>
        <para>Climate change presents significant global challenges. The Paris Agreement,
        signed in 2015, aims to limit global warming to well below 2 degrees Celsius.
        The United Nations has emphasized the importance of technological solutions.</para>
    </section>
    <section>
        <title>AI Applications</title>
        <para>Machine learning algorithms can help predict weather patterns and optimize
        renewable energy systems. Neural networks can process satellite imagery to monitor
        deforestation and ice cap melting.</para>
    </section>
</article>"""


@pytest.fixture
def mock_graphrag_client():
    """Create a mock GraphRAG client."""
    client = AsyncMock(spec=GraphRAGClient)
    
    # Setup mock extract_entities method
    client.extract_entities.return_value = [
        {
            "name": "Artificial Intelligence",
            "entity_type": "concept",
            "entity_id": "ent_ai123456",
            "description": "The simulation of human intelligence in machines",
            "aliases": ["AI", "machine intelligence"],
            "confidence": 0.9,
            "metadata": {"source": "graphrag"}
        },
        {
            "name": "Climate Change",
            "entity_type": "concept",
            "entity_id": "ent_cc789012",
            "description": "Long-term change in Earth's climate patterns",
            "confidence": 0.85,
            "metadata": {"source": "graphrag"}
        }
    ]
    
    # Setup mock get_sources_for_query method
    client.get_sources_for_query.return_value = (
        [
            {
                "content": "Artificial Intelligence can help address climate change through predictive analytics and optimization.",
                "relevance_score": 0.88,
                "metadata": {
                    "title": "AI for Climate Action",
                    "url": "https://example.com/ai-climate",
                    "source_type": "web"
                }
            }
        ],
        "Artificial Intelligence can help address climate change..."
    )
    
    return client


@pytest.fixture
def xml_graphrag_agent():
    """Create an XML GraphRAG agent for testing."""
    # Create agent with mocked dependencies
    agent = XmlGraphRAGAgent("test_graphrag_agent")
    
    # Mock messaging
    agent.messaging = MagicMock()
    agent.messaging.send_task_result = MagicMock()
    
    # Mock MCP client
    agent.mcp_client = AsyncMock()
    agent.async_mcp_client = AsyncMock()
    
    return agent


@pytest.fixture
def complex_xml():
    """Complex XML content with nested elements for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE article PUBLIC "-//OASIS//DTD DocBook XML V5.0//EN" "http://www.oasis-open.org/docbook/xml/5.0/docbook.dtd">
<article xmlns="http://docbook.org/ns/docbook" xmlns:xlink="http://www.w3.org/1999/xlink" version="5.0">
    <info>
        <title>Advanced Machine Learning Techniques for Climate Modeling</title>
        <author>
            <personname>
                <firstname>Jane</firstname>
                <surname>Smith</surname>
            </personname>
            <affiliation>
                <orgname>Climate Research Institute</orgname>
            </affiliation>
        </author>
        <pubdate>2023-11-15</pubdate>
        <abstract>
            <para>This comprehensive article explores various machine learning approaches for climate modeling, 
            with a focus on neural networks and reinforcement learning applied to atmospheric science.</para>
        </abstract>
    </info>
    <section xml:id="introduction">
        <title>Introduction</title>
        <para>Climate modeling presents unique computational challenges that modern machine learning 
        techniques are well-positioned to address. Major research organizations such as NASA, NOAA, 
        and the European Centre for Medium-Range Weather Forecasts (ECMWF) have begun integrating 
        deep learning approaches into their prediction models.</para>
        <para>The <link xlink:href="https://www.ipcc.ch">Intergovernmental Panel on Climate Change (IPCC)</link> 
        has highlighted the potential for AI to improve climate projections in their latest assessment report.</para>
    </section>
    <section xml:id="techniques">
        <title>Machine Learning Techniques</title>
        <section xml:id="neural-networks">
            <title>Neural Networks</title>
            <para>Convolutional Neural Networks (CNNs) have shown particular promise for analyzing 
            spatial data such as satellite imagery and atmospheric patterns.</para>
            <para>Google DeepMind's weather prediction models have demonstrated significant improvements 
            over traditional numerical weather prediction approaches.</para>
        </section>
        <section xml:id="reinforcement-learning">
            <title>Reinforcement Learning</title>
            <para>Reinforcement learning allows models to optimize prediction strategies over time 
            through environmental feedback mechanisms.</para>
        </section>
    </section>
    <section xml:id="challenges">
        <title>Challenges and Limitations</title>
        <para>Despite promising results, several challenges remain, including:</para>
        <itemizedlist>
            <listitem><para>Data quality and standardization issues</para></listitem>
            <listitem><para>Computational resource requirements</para></listitem>
            <listitem><para>Model interpretability concerns</para></listitem>
        </itemizedlist>
    </section>
</article>"""


@pytest.fixture
def malformed_xml():
    """Malformed XML for testing error handling."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<article>
    <title>Malformed XML Document</title>
    <para>This XML is intentionally malformed.
    <unclosed_tag>This tag is not properly closed.
    <nested>This is a nested element</unclosed_nest>
    <self_closing_error / missing angle bracket>
    <empty_attribute attribute=>Empty attribute value</empty_attribute>
</article>"""


@pytest.fixture
def error_producing_graphrag_client():
    """Create a mock GraphRAG client that raises errors."""
    client = AsyncMock(spec=GraphRAGClient)
    
    # Setup mock extract_entities method to raise an exception
    client.extract_entities.side_effect = Exception("GraphRAG service unavailable")
    
    # Setup mock get_sources_for_query method to raise an exception
    client.get_sources_for_query.side_effect = Exception("Failed to retrieve sources")
    
    # Setup mock process_attributed_response method to raise an exception
    client.process_attributed_response.side_effect = Exception("Failed to process response")
    
    return client


@pytest.fixture
def xml_document():
    """Create a mock XmlDocument for testing."""
    # Create sample XML nodes
    nodes = [
        XmlNode(
            xpath="//article/abstract/para",
            element_name="para",
            content="This article explores AI technologies for climate change.",
            verification_status="pending",
            confidence=0.7
        ),
        XmlNode(
            xpath="//article/section[1]/para",
            element_name="para",
            content="Climate change presents significant global challenges.",
            verification_status="pending",
            confidence=0.7
        ),
        XmlNode(
            xpath="//article/section[2]/para",
            element_name="para",
            content="Machine learning algorithms can help predict weather patterns.",
            verification_status="pending",
            confidence=0.7
        )
    ]
    
    # Sample XML content
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <article>
        <title>Artificial Intelligence and Climate Change</title>
        <abstract>
            <para>This article explores AI technologies for climate change.</para>
        </abstract>
        <section>
            <title>Introduction</title>
            <para>Climate change presents significant global challenges.</para>
        </section>
        <section>
            <title>AI Applications</title>
            <para>Machine learning algorithms can help predict weather patterns.</para>
        </section>
    </article>"""
    
    # Create XML document
    return XmlDocument(
        doc_id="test_doc",
        title="Artificial Intelligence and Climate Change",
        doc_type="xml",
        created_at=datetime.datetime.now().isoformat(),
        content=xml_content,
        root_element="article",
        researchable_nodes=nodes
    )


@pytest.mark.asyncio
async def test_on_startup(xml_graphrag_agent):
    """Test agent initialization and startup."""
    # Mock GraphRAG client creation
    with patch("agent_provocateur.xml_graphrag_agent.GraphRAGClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Set environment variable
        with patch.dict("os.environ", {"GRAPHRAG_MCP_URL": "http://test-graphrag:8083"}):
            await xml_graphrag_agent.on_startup()
        
        # Verify GraphRAG client was initialized
        mock_client_class.assert_called_once_with(base_url="http://test-graphrag:8083")
        
        # Verify entity linker was initialized
        assert xml_graphrag_agent.entity_linker is not None
        assert hasattr(xml_graphrag_agent, "extracted_entities")


@pytest.mark.asyncio
async def test_extract_enhanced_entities(xml_graphrag_agent, sample_xml, mock_graphrag_client):
    """Test enhanced entity extraction."""
    # Setup agent with mock GraphRAG client
    xml_graphrag_agent.graphrag_client = mock_graphrag_client
    
    # Mock entity linker
    entity_linker = AsyncMock()
    xml_graphrag_agent.entity_linker = entity_linker
    
    # Create entity objects for testing
    entities = [
        Entity(
            name="Artificial Intelligence",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ai123",
            aliases=["AI"],
            confidence=0.9
        ),
        Entity(
            name="Climate Change",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_cc456",
            confidence=0.85
        ),
        Entity(
            name="Paris Agreement",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_pa789",
            confidence=0.8
        )
    ]
    
    # Add relationships to entities
    entities[0].add_relationship(
        target_entity_id=entities[1].entity_id,
        relation_type=RelationType.RELATED_TO,
        confidence=0.75
    )
    
    # Setup mock return values
    entity_linker.extract_entities_from_text.return_value = entities
    entity_linker.disambiguate_entity.side_effect = lambda entity, _: entity
    
    # Mock MCP client to return sample XML
    xml_graphrag_agent.async_mcp_client.get_xml_content.return_value = sample_xml
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_extract_entities",
        source_agent="test_agent",
        target_agent="test_graphrag_agent",
        intent="extract_enhanced_entities",
        payload={
            "doc_id": "test_doc",
            "min_confidence": 0.7
        }
    )
    
    # Call the handler
    result = await xml_graphrag_agent.handle_extract_enhanced_entities(task_request)
    
    # Verify results
    assert result["status"] == "success"
    assert result["doc_id"] == "test_doc"
    assert result["entity_count"] == 3
    assert result["relationship_count"] == 1
    
    # Verify entity_linker methods were called
    entity_linker.extract_entities_from_text.assert_called_once()
    assert entity_linker.disambiguate_entity.call_count == 3  # Once for each entity
    
    # Verify extracted entities were stored
    assert len(xml_graphrag_agent.extracted_entities) == 3
    assert "entity_ai123" in xml_graphrag_agent.extracted_entities
    
    # Verify entities_by_type structure
    assert EntityType.CONCEPT in result["entities_by_type"]
    assert len(result["entities_by_type"][EntityType.CONCEPT]) == 3


@pytest.mark.asyncio
async def test_analyze_entity_relationships(xml_graphrag_agent):
    """Test relationship analysis between entities."""
    # Create entity objects for testing
    entities = [
        Entity(
            name="Artificial Intelligence",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ai123",
            aliases=["AI"],
            confidence=0.9
        ),
        Entity(
            name="Machine Learning",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ml456",
            confidence=0.85
        ),
        Entity(
            name="Google",
            entity_type=EntityType.ORGANIZATION,
            entity_id="entity_go789",
            confidence=0.9
        )
    ]
    
    # Add relationships to entities
    entities[0].add_relationship(
        target_entity_id=entities[1].entity_id,
        relation_type=RelationType.HAS_PART,
        confidence=0.85
    )
    
    entities[2].add_relationship(
        target_entity_id=entities[0].entity_id,
        relation_type=RelationType.CREATED_BY,
        confidence=0.8
    )
    
    # Store entities in agent
    xml_graphrag_agent.extracted_entities = {entity.entity_id: entity for entity in entities}
    xml_graphrag_agent.entity_clusters = []  # Initialize entity_clusters
    
    # Mock entity linker create_entity_map
    entity_linker = AsyncMock()
    xml_graphrag_agent.entity_linker = entity_linker
    entity_linker.create_entity_map.return_value = {
        "nodes": ["node1", "node2", "node3"],
        "edges": ["edge1", "edge2"]
    }
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_analyze_relationships",
        source_agent="test_agent",
        target_agent="test_graphrag_agent",
        intent="analyze_entity_relationships",
        payload={}  # Empty payload to use all entities
    )
    
    # Call the handler
    result = await xml_graphrag_agent.handle_analyze_entity_relationships(task_request)
    
    # Verify results
    assert result["status"] == "success"
    assert result["entity_count"] == 3
    assert result["relationship_count"] == 2
    
    # Verify relationship types
    assert RelationType.HAS_PART in result["relationship_types"]
    assert RelationType.CREATED_BY in result["relationship_types"]
    
    # Verify entity connectivity
    assert "entity_ai123" in result["entity_connectivity"]
    assert "entity_go789" in result["entity_connectivity"]
    
    # Verify clusters
    assert len(result["clusters"]) > 0
    
    # Verify entity map
    assert "relationship_map" in result
    assert result["relationship_map"]["nodes"] == ["node1", "node2", "node3"]
    assert result["relationship_map"]["edges"] == ["edge1", "edge2"]


@pytest.mark.asyncio
async def test_generate_entity_map(xml_graphrag_agent):
    """Test entity map generation for visualization."""
    # Create entity objects for testing
    entities = [
        Entity(
            name="Artificial Intelligence",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ai123",
            confidence=0.9
        ),
        Entity(
            name="Machine Learning",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ml456",
            confidence=0.85
        ),
        Entity(
            name="Neural Networks",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_nn789",
            confidence=0.82
        ),
        Entity(
            name="Low Confidence Entity",
            entity_type=EntityType.OTHER,
            entity_id="entity_lc012",
            confidence=0.5  # Below default threshold
        )
    ]
    
    # Add relationships
    entities[0].add_relationship(
        target_entity_id=entities[1].entity_id,
        relation_type=RelationType.HAS_PART
    )
    
    entities[1].add_relationship(
        target_entity_id=entities[2].entity_id,
        relation_type=RelationType.HAS_PART
    )
    
    # Store entities in agent
    xml_graphrag_agent.extracted_entities = {entity.entity_id: entity for entity in entities}
    xml_graphrag_agent.entity_clusters = []  # Initialize entity_clusters
    
    # Mock entity linker create_entity_map
    entity_linker = AsyncMock()
    xml_graphrag_agent.entity_linker = entity_linker
    entity_linker.create_entity_map.return_value = {
        "nodes": [
            {"id": "entity_ai123", "label": "Artificial Intelligence"},
            {"id": "entity_ml456", "label": "Machine Learning"},
            {"id": "entity_nn789", "label": "Neural Networks"}
        ],
        "edges": [
            {"id": "rel1", "source": "entity_ai123", "target": "entity_ml456"},
            {"id": "rel2", "source": "entity_ml456", "target": "entity_nn789"}
        ]
    }
    
    # Create task request with include_all=True
    task_request = TaskRequest(
        task_id="test_generate_map",
        source_agent="test_agent",
        target_agent="test_graphrag_agent",
        intent="generate_entity_map",
        payload={
            "include_all": True,
            "min_confidence": 0.6
        }
    )
    
    # Call the handler
    result = await xml_graphrag_agent.handle_generate_entity_map(task_request)
    
    # Verify results
    assert result["status"] == "success"
    assert result["node_count"] == 3
    assert result["edge_count"] == 2
    
    # Verify entity types count
    assert EntityType.CONCEPT in result["entity_types"]
    assert result["entity_types"][EntityType.CONCEPT] == 3
    
    # Verify relation types count
    assert RelationType.HAS_PART in result["relation_types"]
    assert result["relation_types"][RelationType.HAS_PART] == 2
    
    # Verify entity linker was called with filtered entities (excluding low confidence)
    args, _ = entity_linker.create_entity_map.call_args
    actual_entities = args[0]
    entity_ids = [e.entity_id for e in actual_entities]
    assert "entity_ai123" in entity_ids
    assert "entity_ml456" in entity_ids
    assert "entity_nn789" in entity_ids
    assert "entity_lc012" not in entity_ids  # Should be filtered out


@pytest.mark.asyncio
async def test_handle_batch_verify_nodes(xml_graphrag_agent, xml_document):
    """Test batch verification of XML nodes."""
    # Setup agent with mock GraphRAG client
    mock_client = AsyncMock(spec=GraphRAGClient)
    xml_graphrag_agent.graphrag_client = mock_client
    
    # Setup mock get_sources_for_query method
    mock_client.get_sources_for_query.return_value = (
        [
            {
                "content": "Climate change is a significant global challenge demanding action.",
                "relevance_score": 0.85,
                "metadata": {
                    "title": "Climate Report",
                    "url": "https://example.com/climate",
                    "source_type": "WEB",
                    "confidence_score": 0.8,
                    "source_id": "src_climate001"
                }
            }
        ],
        "Climate change is a significant global challenge..."
    )
    
    # Mock MCP client to return the XML document
    xml_graphrag_agent.async_mcp_client.get_xml_document.return_value = xml_document
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_batch_verify",
        source_agent="test_agent",
        target_agent="test_graphrag_agent",
        intent="batch_verify_nodes",
        payload={
            "doc_id": "test_doc",
            "options": {
                "use_graphrag": True
            }
        }
    )
    
    # Call the handler
    result = await xml_graphrag_agent.handle_batch_verify_nodes(task_request)
    
    # Verify results
    assert result["doc_id"] == "test_doc"
    assert "verification_results" in result
    assert result["verification_method"] == "graphrag_mcp"
    assert result["total_nodes"] == 3
    assert "completed_nodes" in result
    
    # Verify sources in first result
    if result["verification_results"]:
        first_result = result["verification_results"][0]
        assert "sources" in first_result
        assert "status" in first_result
        assert "confidence" in first_result


@pytest.mark.asyncio
async def test_process_attributed_response(xml_graphrag_agent):
    """Test processing of attributed response."""
    # Setup agent with mock GraphRAG client
    mock_client = AsyncMock(spec=GraphRAGClient)
    xml_graphrag_agent.graphrag_client = mock_client
    
    # Setup mock process_attributed_response method
    mock_client.process_attributed_response.return_value = {
        "text": "Processed response with attribution markers",
        "sources": [
            {
                "source_id": "src001",
                "content": "Source content",
                "metadata": {
                    "title": "Source title",
                    "url": "https://example.com/source"
                }
            }
        ],
        "confidence": 0.85,
        "explanation": "Attribution explanation"
    }
    
    # Test data
    response = "AI can help with climate prediction models [1]."
    sources = [
        {
            "content": "Artificial Intelligence models are useful for climate prediction.",
            "metadata": {
                "title": "AI in Climate Science",
                "url": "https://example.com/ai-climate"
            }
        }
    ]
    
    # Call the method
    result = await xml_graphrag_agent.process_attributed_response(response, sources)
    
    # Verify results
    assert "text" in result
    assert "sources" in result
    assert "confidence" in result
    
    # Verify method was called with correct arguments
    mock_client.process_attributed_response.assert_called_once_with(response, sources)


@pytest.mark.asyncio
async def test_process_attributed_response_with_error(xml_graphrag_agent, error_producing_graphrag_client):
    """Test processing of attributed response with error handling."""
    # Setup agent with error-producing GraphRAG client
    xml_graphrag_agent.graphrag_client = error_producing_graphrag_client
    
    # Test data
    response = "AI can help with climate prediction models [1]."
    sources = [
        {
            "content": "Artificial Intelligence models are useful for climate prediction.",
            "metadata": {
                "title": "AI in Climate Science",
                "url": "https://example.com/ai-climate"
            }
        }
    ]
    
    # Call the method
    result = await xml_graphrag_agent.process_attributed_response(response, sources)
    
    # Verify fallback results
    assert "text" in result
    assert "sources" in result
    assert "confidence" in result
    assert result["text"] == response
    assert result["sources"] == sources
    assert result["confidence"] == 0.75
    assert "explanation" in result
    assert "fallback" in result["explanation"].lower()
    
    # Verify error-producing client was called
    error_producing_graphrag_client.process_attributed_response.assert_called_once_with(response, sources)


@pytest.mark.asyncio
async def test_extract_text_from_xml(xml_graphrag_agent, complex_xml):
    """Test extraction of plain text from XML."""
    # Get access to the private method
    extract_text = xml_graphrag_agent._extract_text_from_xml
    
    # Call the method
    result = extract_text(complex_xml)
    
    # Verify results contain key phrases from the XML
    assert "Machine Learning Techniques" in result
    assert "Climate Research Institute" in result
    assert "Neural Networks" in result
    assert "reinforcement learning" in result
    
    # Verify no XML tags in result
    assert "<" not in result
    assert ">" not in result
    assert "<para>" not in result


@pytest.mark.asyncio
async def test_extract_text_from_malformed_xml(xml_graphrag_agent, malformed_xml):
    """Test extraction of text from malformed XML handles errors gracefully."""
    # Get access to the private method
    extract_text = xml_graphrag_agent._extract_text_from_xml
    
    # Call the method
    result = extract_text(malformed_xml)
    
    # Verify results contain key phrases from the XML despite errors
    assert "Malformed XML Document" in result
    assert "intentionally malformed" in result
    
    # Verify no XML tags in result
    assert "<" not in result
    assert ">" not in result


@pytest.mark.asyncio
async def test_error_handling_extract_entities(xml_graphrag_agent, sample_xml, error_producing_graphrag_client, xml_document):
    """Test error handling in extract_entities method."""
    # Setup agent with error-producing client
    xml_graphrag_agent.graphrag_client = error_producing_graphrag_client
    
    # Mock MCP client to return XML content
    xml_graphrag_agent.async_mcp_client.get_xml_document.return_value = xml_document
    xml_graphrag_agent.async_mcp_client.get_xml_content.return_value = sample_xml
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_extract_entities_error",
        source_agent="test_agent",
        target_agent="test_graphrag_agent",
        intent="extract_entities",
        payload={
            "doc_id": "test_doc",
            "use_graphrag": True  # This should trigger the error path
        }
    )
    
    # Call the handler
    result = await xml_graphrag_agent.handle_extract_entities(task_request)
    
    # Verify the handler gracefully falls back to another implementation
    assert "doc_id" in result
    assert "entities" in result
    assert "extraction_method" in result
    assert "entity_count" in result


@pytest.mark.asyncio
async def test_identify_entity_clusters(xml_graphrag_agent):
    """Test identification of entity clusters."""
    # Create entity objects for testing
    entities = [
        Entity(
            name="Artificial Intelligence",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ai123"
        ),
        Entity(
            name="Machine Learning",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ml456"
        ),
        Entity(
            name="Neural Networks",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_nn789"
        ),
        Entity(
            name="Climate Change",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_cc001"
        ),
        Entity(
            name="Global Warming",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_gw002"
        )
    ]
    
    # Create connections: AI -> ML -> NN (one cluster)
    entities[0].add_relationship(
        target_entity_id=entities[1].entity_id,
        relation_type=RelationType.HAS_PART
    )
    entities[1].add_relationship(
        target_entity_id=entities[2].entity_id,
        relation_type=RelationType.HAS_PART
    )
    
    # Create another cluster: Climate Change -> Global Warming
    entities[3].add_relationship(
        target_entity_id=entities[4].entity_id,
        relation_type=RelationType.RELATED_TO
    )
    
    # Store entities in agent
    xml_graphrag_agent.extracted_entities = {entity.entity_id: entity for entity in entities}
    
    # Call the method (directly accessing private method for testing)
    clusters = xml_graphrag_agent._identify_entity_clusters(entities)
    
    # Verify results
    assert len(clusters) == 2  # Should find two clusters
    
    # Find the larger cluster (AI, ML, NN)
    ai_cluster = next((c for c in clusters if len(c["entity_ids"]) == 3), None)
    assert ai_cluster is not None
    assert "entity_ai123" in ai_cluster["entity_ids"]
    assert "entity_ml456" in ai_cluster["entity_ids"]
    assert "entity_nn789" in ai_cluster["entity_ids"]
    assert ai_cluster["primary_type"] == EntityType.CONCEPT
    
    # Find the smaller cluster (Climate Change, Global Warming)
    climate_cluster = next((c for c in clusters if len(c["entity_ids"]) == 2), None)
    assert climate_cluster is not None
    assert "entity_cc001" in climate_cluster["entity_ids"]
    assert "entity_gw002" in climate_cluster["entity_ids"]


@pytest.mark.asyncio
async def test_entity_map_with_no_entities(xml_graphrag_agent):
    """Test entity map generation with no entities."""
    # Store no entities in agent
    xml_graphrag_agent.extracted_entities = {}
    xml_graphrag_agent.entity_clusters = []
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_empty_map",
        source_agent="test_agent",
        target_agent="test_graphrag_agent",
        intent="generate_entity_map",
        payload={
            "include_all": True
        }
    )
    
    # Call the handler
    result = await xml_graphrag_agent.handle_generate_entity_map(task_request)
    
    # Verify error response
    assert result["status"] == "failed"
    assert "error" in result
    assert "No entities found" in result["error"]


@pytest.fixture
def empty_xml_document():
    """Create a mock XmlDocument with no content."""
    # Create empty XML document
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <article>
    </article>"""
    
    # Create XML document with no researchable nodes
    return XmlDocument(
        doc_id="empty_doc",
        title="Empty Document",
        doc_type="xml",
        created_at=datetime.datetime.now().isoformat(),
        content=xml_content,
        root_element="article",
        researchable_nodes=[]
    )


@pytest.mark.asyncio
async def test_extract_entities_with_empty_content(xml_graphrag_agent, empty_xml_document):
    """Test entity extraction with empty document content."""
    # Setup agent with mock GraphRAG client
    mock_client = AsyncMock(spec=GraphRAGClient)
    xml_graphrag_agent.graphrag_client = mock_client
    
    # Mock MCP client to return the empty XML document
    xml_graphrag_agent.async_mcp_client.get_xml_document.return_value = empty_xml_document
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_extract_empty",
        source_agent="test_agent",
        target_agent="test_graphrag_agent",
        intent="extract_entities",
        payload={
            "doc_id": "empty_doc",
            "use_graphrag": True
        }
    )
    
    # Call the handler
    result = await xml_graphrag_agent.handle_extract_entities(task_request)
    
    # Verify empty response
    assert result["doc_id"] == "empty_doc"
    assert result["entities"] == []
    assert result["entity_count"] == 0
    assert result["extraction_method"] == "graphrag_mcp"
    assert "error" in result
    assert "No content to extract entities from" in result["error"]


@pytest.mark.asyncio
async def test_extract_entities_with_specific_node_match(xml_graphrag_agent, xml_document):
    """Test entity extraction with specific node matching."""
    # Setup agent with mock GraphRAG client
    mock_client = AsyncMock(spec=GraphRAGClient)
    xml_graphrag_agent.graphrag_client = mock_client
    
    # Setup mock extract_entities method with entity that will match a specific node
    mock_client.extract_entities.return_value = [
        {
            "name": "Climate change",
            "entity_type": "concept",
            "entity_id": "ent_cc123456",
            "description": "Long-term change in Earth's climate patterns",
            "aliases": ["global warming"],
            "confidence": 0.9
        }
    ]
    
    # Mock MCP client to return XML document
    xml_graphrag_agent.async_mcp_client.get_xml_document.return_value = xml_document
    
    # Create task request
    task_request = TaskRequest(
        task_id="test_extract_entities_specific",
        source_agent="test_agent",
        target_agent="test_graphrag_agent",
        intent="extract_entities",
        payload={
            "doc_id": "test_doc",
            "use_graphrag": True
        }
    )
    
    # Call the handler
    result = await xml_graphrag_agent.handle_extract_entities(task_request)
    
    # Verify results
    assert result["doc_id"] == "test_doc"
    assert len(result["entities"]) == 1
    assert result["entity_count"] == 1
    assert result["extraction_method"] == "graphrag_mcp"
    
    # Verify entity details
    entity = result["entities"][0]
    assert entity["name"] == "Climate change"
    assert entity["entity_id"] == "ent_cc123456"
    assert entity["entity_type"] == "concept"
    
    # Should match one of the XPaths from our nodes based on content matching
    assert entity["xpath"] in ["//article/abstract/para", "//article/section[1]/para"]


@pytest.mark.asyncio
async def test_generate_entity_map_with_specific_entities(xml_graphrag_agent):
    """Test entity map generation with specific entity IDs."""
    # Create entity objects for testing
    entities = [
        Entity(
            name="Artificial Intelligence",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ai123",
            confidence=0.9
        ),
        Entity(
            name="Machine Learning",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_ml456",
            confidence=0.85
        ),
        Entity(
            name="Neural Networks",
            entity_type=EntityType.CONCEPT,
            entity_id="entity_nn789",
            confidence=0.82
        )
    ]
    
    # Add relationships
    entities[0].add_relationship(
        target_entity_id=entities[1].entity_id,
        relation_type=RelationType.HAS_PART
    )
    
    # Store entities in agent
    xml_graphrag_agent.extracted_entities = {entity.entity_id: entity for entity in entities}
    xml_graphrag_agent.entity_clusters = []
    
    # Mock entity linker create_entity_map
    entity_linker = AsyncMock()
    xml_graphrag_agent.entity_linker = entity_linker
    entity_linker.create_entity_map.return_value = {
        "nodes": [
            {"id": "entity_ai123", "label": "Artificial Intelligence"},
            {"id": "entity_ml456", "label": "Machine Learning"}
        ],
        "edges": [
            {"id": "rel1", "source": "entity_ai123", "target": "entity_ml456"}
        ]
    }
    
    # Create task request with specific entity IDs
    task_request = TaskRequest(
        task_id="test_generate_map_specific",
        source_agent="test_agent",
        target_agent="test_graphrag_agent",
        intent="generate_entity_map",
        payload={
            "entity_ids": ["entity_ai123", "entity_ml456"]  # Only include 2 of the 3 entities
        }
    )
    
    # Call the handler
    result = await xml_graphrag_agent.handle_generate_entity_map(task_request)
    
    # Verify results
    assert result["status"] == "success"
    assert result["node_count"] == 2
    assert result["edge_count"] == 1
    
    # Verify entity linker was called with the specific entities
    args, _ = entity_linker.create_entity_map.call_args
    actual_entities = args[0]
    entity_ids = [e.entity_id for e in actual_entities]
    assert len(entity_ids) == 2
    assert "entity_ai123" in entity_ids
    assert "entity_ml456" in entity_ids
    assert "entity_nn789" not in entity_ids