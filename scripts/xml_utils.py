#!/usr/bin/env python3
"""
Shared utilities for XML CLI tools.
"""

from pathlib import Path
import os
import sys

def _resolve_file_path(file_path):
    """
    Resolve file path for XML files.
    
    Args:
        file_path: The input path (absolute or relative)
        
    Returns:
        Path object with the resolved path
    """
    path = Path(file_path)
    
    # Handle absolute paths
    if path.is_absolute():
        return path
    
    # Handle relative paths
    # Try relative to current directory
    if path.exists():
        return path.absolute()
    
    # Try in examples directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    examples_dir = project_root / "examples"
    
    examples_path = examples_dir / path.name
    if examples_path.exists():
        return examples_path
    
    # Not found
    return path.absolute()

def setup_python_path():
    """
    Ensure the project root is in the Python path.
    """
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Add the project root to the Python path if needed
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Also add the src directory
    src_dir = project_root / "src"
    if src_dir.exists() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

def get_api_url():
    """
    Get the API URL from environment or use default.
    """
    return os.environ.get("AP_API_URL", "http://localhost:8000")

def ensure_server_running():
    """
    Check if the server is running and raise an error if it's not.
    """
    import requests
    from requests.exceptions import ConnectionError

    try:
        url = f"{get_api_url()}/health"
        response = requests.get(url, timeout=2)
        if response.status_code != 200:
            print(f"Server returned status code {response.status_code}")
            print(f"Make sure the server is running on {get_api_url()}")
            sys.exit(1)
    except ConnectionError:
        print(f"Failed to connect to server at {get_api_url()}")
        print("Make sure the server is running with: ./scripts/ap.sh server")
        sys.exit(1)
    except Exception as e:
        print(f"Error checking server: {e}")
        print(f"Make sure the server is running on {get_api_url()}")
        sys.exit(1)