"""Test fixtures for Agent Provocateur."""

import os
import pytest
from pathlib import Path

@pytest.fixture
def xml_test_dir():
    """Return the path to the XML test data directory."""
    return Path(__file__).parent / "test_data" / "xml_documents"

@pytest.fixture
def simple_xml_path(xml_test_dir):
    """Return the path to the simple test XML file."""
    return xml_test_dir / "simple.xml"

@pytest.fixture
def complex_xml_path(xml_test_dir):
    """Return the path to the complex test XML file."""
    return xml_test_dir / "complex.xml"

@pytest.fixture
def simple_xml_content(simple_xml_path):
    """Return the content of the simple test XML file."""
    with open(simple_xml_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def complex_xml_content(complex_xml_path):
    """Return the content of the complex test XML file."""
    with open(complex_xml_path, "r", encoding="utf-8") as f:
        return f.read()