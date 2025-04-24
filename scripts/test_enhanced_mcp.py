#!/usr/bin/env python3

# Note: Run this with UV using:
# uv run scripts/test_enhanced_mcp.py
"""
Test script for the Enhanced MCP Server.

This script:
1. Verifies the enhanced MCP server is running
2. Tests a simple XML upload
3. Tests the system info endpoint
4. Tests the integrated workflow

Usage:
    python scripts/test_enhanced_mcp.py
    python scripts/test_enhanced_mcp.py --host 127.0.0.1 --port 8001
"""

import argparse
import json
import os
import sys
import time
import requests
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parents[1]
sys.path.append(str(project_root))

# Set up coloring for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_status(message, success=True):
    """Print a status message with color."""
    prefix = f"{Colors.OKGREEN}[✓]{Colors.ENDC}" if success else f"{Colors.FAIL}[✗]{Colors.ENDC}"
    print(f"{prefix} {message}")


def print_info(message):
    """Print an info message with color."""
    print(f"{Colors.OKBLUE}[i]{Colors.ENDC} {message}")


def print_section(name):
    """Print a section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {name} ==={Colors.ENDC}\n")


def check_server(base_url):
    """Check if the server is running."""
    try:
        # Try different endpoints since health may not be available
        endpoints = [
            "/api/health",
            "/docs",
            "/api/info",
            "/"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=2)
                if response.status_code == 200:
                    print_status(f"Enhanced MCP server is running (checked {endpoint})")
                    return True
            except requests.RequestException:
                continue
                
        print_status("Server is running but no test endpoints responded successfully", False)
        return False
    except Exception as e:
        print_status(f"Server is not running: {str(e)}", False)
        print_info("Start the server with: ./scripts/run_enhanced_mcp_server.sh")
        return False


def test_system_info(base_url):
    """Test the system info endpoint."""
    print_section("Testing System Info")
    
    try:
        response = requests.get(f"{base_url}/api/info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            print_status("System info endpoint is working")
            
            # Print version info
            print_info(f"System version: {info.get('version')}")
            print_info(f"Build: {info.get('build_number')}")
            
            # Print service status
            print_info("Services status:")
            for service_name, service in info.get('services', {}).items():
                status = service.get('status', 'unknown')
                status_color = Colors.OKGREEN if status == 'running' else Colors.WARNING
                print(f"  - {service_name}: {status_color}{status}{Colors.ENDC} (port: {service.get('port')})")
            
            return True
        else:
            print_status(f"System info returned unexpected status code: {response.status_code}", False)
            print_info(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        print_status(f"Failed to get system info: {str(e)}", False)
        return False


def test_xml_upload(base_url):
    """Test XML document upload."""
    print_section("Testing XML Upload")
    
    # Sample XML content
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<research>
    <metadata>
        <title>Enhanced API Testing</title>
        <date>2025-04-23</date>
    </metadata>
    <findings>
        <finding id="f1">
            <statement>The API documentation improvements significantly enhance system usability.</statement>
            <confidence>high</confidence>
        </finding>
        <finding id="f2">
            <statement>Service integration reduces development complexity by 30%.</statement>
            <confidence>medium</confidence>
        </finding>
    </findings>
</research>"""
    
    try:
        response = requests.post(
            f"{base_url}/xml/upload",
            json={
                "xml_content": xml_content,
                "title": "Enhanced API Test Document"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            doc_id = result.get('doc_id')
            print_status(f"XML upload successful - Document ID: {doc_id}")
            
            # Print some details
            print_info(f"Title: {result.get('title')}")
            print_info(f"Root element: {result.get('root_element')}")
            print_info(f"Researchable nodes found: {len(result.get('researchable_nodes', []))}")
            
            return doc_id
        else:
            print_status(f"XML upload failed with status code: {response.status_code}", False)
            print_info(f"Response: {response.text}")
            return None
    except requests.RequestException as e:
        print_status(f"Failed to upload XML: {str(e)}", False)
        return None


def test_workflow(base_url):
    """Test the end-to-end workflow endpoint."""
    print_section("Testing End-to-End Workflow")
    
    # Sample XML content
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<research>
    <metadata>
        <title>Climate Change Research</title>
        <date>2025-04-23</date>
    </metadata>
    <findings>
        <finding id="f1">
            <statement>Global temperatures have risen by 1.1°C since pre-industrial times.</statement>
            <confidence>high</confidence>
        </finding>
    </findings>
</research>"""
    
    try:
        response = requests.post(
            f"{base_url}/workflow/process-document",
            json={
                "xml_content": xml_content,
                "title": "Workflow Test Document",
                "research_query": "Verify global temperature rise claims"
            },
            timeout=15  # Longer timeout for workflow
        )
        
        if response.status_code == 200:
            result = response.json()
            print_status("Workflow processed successfully")
            
            # Print workflow results
            doc_id = result.get('doc_id')
            entities = result.get('entities', [])
            research = result.get('research')
            status = result.get('status')
            errors = result.get('errors', [])
            
            print_info(f"Document ID: {doc_id}")
            print_info(f"Status: {status}")
            print_info(f"Entities found: {len(entities)}")
            
            # Print top entities if present
            if entities:
                print_info("Top entities:")
                for i, entity in enumerate(entities[:3]):
                    print(f"  {i+1}. {entity.get('entity')} ({entity.get('type')})")
            
            # Print research status
            if research:
                print_info("Research completed successfully")
                sources = research.get('sources', [])
                print_info(f"Sources found: {len(sources)}")
            elif status == "partial_success":
                print_info("Research not completed (services may be unavailable)")
            
            # Print any errors
            if errors:
                print_info("Errors encountered:")
                for error in errors:
                    print(f"  - {error}")
            
            return True
        else:
            print_status(f"Workflow failed with status code: {response.status_code}", False)
            print_info(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        print_status(f"Failed to execute workflow: {str(e)}", False)
        return False


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description="Test the Enhanced MCP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    args = parser.parse_args()
    
    base_url = f"http://{args.host}:{args.port}"
    print_info(f"Testing Enhanced MCP Server at {base_url}")
    
    # Check if server is running
    if not check_server(base_url):
        sys.exit(1)
    
    # Run tests
    overall_success = True
    
    # Test system info
    if not test_system_info(base_url):
        overall_success = False
    
    # Test XML upload
    doc_id = test_xml_upload(base_url)
    if not doc_id:
        overall_success = False
    
    # Test workflow
    if not test_workflow(base_url):
        overall_success = False
    
    # Print final result
    print_section("Test Results")
    if overall_success:
        print_status("All tests passed successfully")
    else:
        print_status("Some tests failed", False)
    
    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()