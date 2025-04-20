"""Tests for the XML integration with MCP server and client."""

import pytest
import asyncio
from agent_provocateur.mcp_client import McpClient
from agent_provocateur.models import XmlDocument, XmlNode

@pytest.mark.asyncio
async def test_list_xml_documents():
    """Test listing XML documents."""
    client = McpClient(base_url="http://localhost:8000")
    
    # List XML documents
    docs = await client.list_documents(doc_type="xml")
    
    assert len(docs) >= 2  # At least our sample documents
    assert all(doc.doc_type == "xml" for doc in docs)
    
    # Verify that the documents have XML type
    assert len(docs) > 0, "No XML documents found"
    for doc in docs:
        assert doc.doc_type == "xml", f"Document {doc.doc_id} is not of type 'xml'"
        
    # Note: The documents might be returned as generic Document objects in some cases,
    # not as XmlDocument objects with specific XML attributes

@pytest.mark.asyncio
async def test_get_xml_document():
    """Test getting an XML document from the MCP server."""
    client = McpClient(base_url="http://localhost:8000")
    
    # Get a sample XML document
    doc = await client.get_xml_document("xml1")
    
    assert isinstance(doc, XmlDocument)
    assert doc.doc_id == "xml1"
    assert doc.doc_type == "xml"
    assert doc.root_element == "research"
    assert "<research>" in doc.content
    assert len(doc.researchable_nodes) > 0
    assert all(isinstance(node, XmlNode) for node in doc.researchable_nodes)

@pytest.mark.asyncio
async def test_get_xml_content():
    """Test getting raw XML content."""
    client = McpClient(base_url="http://localhost:8000")
    
    # Get XML content
    content = await client.get_xml_content("xml1")
    
    assert content is not None
    assert "<?xml" in content
    assert "<research>" in content

@pytest.mark.asyncio
async def test_get_xml_researchable_nodes():
    """Test getting researchable nodes for an XML document."""
    client = McpClient(base_url="http://localhost:8000")
    
    # Get researchable nodes
    nodes = await client.get_xml_researchable_nodes("xml1")
    
    assert len(nodes) > 0
    assert all(isinstance(node, XmlNode) for node in nodes)
    assert all(hasattr(node, "verification_status") for node in nodes)
    assert all(node.verification_status == "pending" for node in nodes)

@pytest.mark.asyncio
async def test_upload_xml():
    """Test uploading a new XML document."""
    client = McpClient(base_url="http://localhost:8000")
    
    # Create XML content
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
    <title>Test Book</title>
    <author>Test Author</author>
    <chapters>
        <chapter id="1">
            <title>Introduction</title>
            <content>This is the introduction chapter.</content>
        </chapter>
        <chapter id="2">
            <title>Conclusion</title>
            <content>This is the conclusion chapter.</content>
        </chapter>
    </chapters>
</book>
"""
    
    # Upload the XML document
    doc = await client.upload_xml(xml_content, "Test XML Document")
    
    assert isinstance(doc, XmlDocument)
    assert doc.title == "Test XML Document"
    assert doc.doc_type == "xml"
    assert doc.root_element == "book"
    assert "<book>" in doc.content
    
    # Verify that it's added to the document store
    all_xml_docs = await client.list_documents(doc_type="xml")
    assert doc.doc_id in [doc.doc_id for doc in all_xml_docs]