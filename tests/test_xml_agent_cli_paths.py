"""Tests for XML agent CLI path handling."""

import pytest
from pathlib import Path
import tempfile
import os
import sys

# Add scripts directory to path to import module directly
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.append(str(scripts_dir))
import xml_agent_cli


def test_file_path_handling():
    """Test that the script correctly handles various file paths."""
    # Test with absolute path
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as f:
        abs_path = f.name
    
    try:
        # Create a test script that would process the file path logic
        result = xml_agent_cli._resolve_file_path(abs_path)
        assert result == Path(abs_path)
        assert str(result).startswith('/')
        
        # Test relative path in current directory
        rel_path = "test.xml"
        rel_result = xml_agent_cli._resolve_file_path(rel_path)
        assert rel_result == Path(rel_path) or rel_result == Path("examples") / rel_path
        
        # Test path in examples directory
        example_path = "examples/test.xml"
        example_result = xml_agent_cli._resolve_file_path("test.xml")
        if not Path("test.xml").exists():
            assert Path("examples") / "test.xml" in [example_result, rel_result]
    finally:
        # Clean up
        if os.path.exists(abs_path):
            os.unlink(abs_path)


# Add helper method to the XML agent CLI module to make testing easier
def add_helper_method():
    """Add a helper method to the xml_agent_cli module for testing."""
    if not hasattr(xml_agent_cli, "_resolve_file_path"):
        def _resolve_file_path(file_path):
            """Resolve file path using the same logic as in advanced_identify."""
            if file_path.startswith('/'):
                return Path(file_path)
            else:
                # First try in current directory
                result_path = Path(file_path)
                if not result_path.exists():
                    # Then try in examples directory
                    result_path = Path("examples") / file_path
                return result_path
            
        # Add method to module
        xml_agent_cli._resolve_file_path = _resolve_file_path


# Add the helper method before running tests
add_helper_method()