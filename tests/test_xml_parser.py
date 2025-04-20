"""Tests for the XML parser module."""

import pytest
from defusedxml import ElementTree
from agent_provocateur.xml_parser import (
    parse_xml, 
    create_xml_document, 
    _element_to_dict,
    identify_researchable_nodes,
    load_xml_file
)
from agent_provocateur.models import XmlDocument, XmlNode

def test_parse_xml_simple(simple_xml_content):
    """Test parsing a simple XML document."""
    result, namespaces = parse_xml(simple_xml_content)
    
    # Check structure
    assert isinstance(result, dict)
    
    # The root element becomes the dictionary itself
    assert "metadata" in result
    assert "findings" in result
    assert "references" in result
    
    # Check namespaces
    assert isinstance(namespaces, dict)

def test_parse_xml_complex(complex_xml_content):
    """Test parsing a complex XML document with namespaces."""
    result, namespaces = parse_xml(complex_xml_content)
    
    # Check structure
    assert isinstance(result, dict)
    
    # For a root element with namespaces, we'll have the root element represented as the dict
    assert "product" in result
    
    # Check namespaces
    assert isinstance(namespaces, dict)
    assert "prod" in namespaces
    assert "mfg" in namespaces
    assert namespaces["prod"] == "http://example.com/product"
    assert namespaces["mfg"] == "http://example.com/manufacturer"

def test_element_to_dict():
    """Test converting XML elements to dictionaries."""
    xml = """<root><child1>value1</child1><child2 attr="val">value2</child2></root>"""
    root = ElementTree.fromstring(xml)
    
    result = _element_to_dict(root)
    
    assert "child1" in result
    assert result["child1"]["#text"] == "value1"
    assert "child2" in result
    assert result["child2"]["#text"] == "value2"
    assert "@attributes" in result["child2"]
    assert result["child2"]["@attributes"]["attr"] == "val"

def test_create_xml_document(simple_xml_content):
    """Test creating an XmlDocument from raw XML."""
    doc = create_xml_document(simple_xml_content, "test1", "Test Document")
    
    assert doc.doc_id == "test1"
    assert doc.title == "Test Document"
    assert doc.content == simple_xml_content
    assert doc.root_element == "research"
    assert doc.doc_type == "xml"
    assert "element_count" in doc.metadata
    assert doc.metadata["element_count"] > 0

def test_invalid_xml():
    """Test handling invalid XML."""
    with pytest.raises(ValueError):
        parse_xml("<root>unclosed")
        
def test_identify_researchable_nodes(simple_xml_content):
    """Test identifying researchable nodes in XML."""
    nodes = identify_researchable_nodes(simple_xml_content)
    
    assert len(nodes) > 0
    assert all(isinstance(node, XmlNode) for node in nodes)
    
    # Check that finding nodes are identified
    finding_nodes = [node for node in nodes if node.element_name == "finding"]
    assert len(finding_nodes) == 2
    
    # Check that reference nodes are identified
    reference_nodes = [node for node in nodes if node.element_name == "reference"]
    assert len(reference_nodes) == 2

def test_identify_researchable_nodes_custom_rules(simple_xml_content):
    """Test identifying researchable nodes with custom rules."""
    nodes = identify_researchable_nodes(simple_xml_content, xpath_rules=["//statement"])
    
    assert len(nodes) > 0
    statement_nodes = [node for node in nodes if node.element_name == "statement"]
    assert len(statement_nodes) > 0
    
def test_load_xml_file(simple_xml_path):
    """Test loading XML from a file."""
    content = load_xml_file(str(simple_xml_path))
    
    assert content is not None
    assert len(content) > 0
    assert "<?xml" in content
    assert "<research>" in content