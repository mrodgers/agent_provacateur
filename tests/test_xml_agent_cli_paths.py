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
    # Import xml_utils for the resolution function
    import sys
    scripts_dir = Path(__file__).parent.parent / "scripts"
    sys.path.append(str(scripts_dir))
    import xml_utils
    
    # Test with absolute path
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as f:
        abs_path = f.name
    
    try:
        # Test using xml_utils _resolve_file_path since that's the actual implementation
        result = xml_utils._resolve_file_path(abs_path)
        assert result == Path(abs_path)
        assert str(result).startswith('/')
        
        # Test relative path (which gets resolved to absolute path by the function)
        rel_path = "test.xml"
        rel_result = xml_utils._resolve_file_path(rel_path)
        
        # If test.xml doesn't exist, it should return an absolute path to the current directory
        if not Path(rel_path).exists():
            assert str(rel_result).endswith(rel_path)
            assert rel_result.is_absolute()
    finally:
        # Clean up
        if os.path.exists(abs_path):
            os.unlink(abs_path)


# No need for helper methods anymore since we're using the actual implementation directly