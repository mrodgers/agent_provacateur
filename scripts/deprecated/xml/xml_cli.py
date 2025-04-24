#!/usr/bin/env python3
# Path to run: scripts/xml_cli.py
"""
Command-line tool for working with XML documents in Agent Provocateur.

This is a simple script to test the XML functionality interactively.
"""

import argparse
import asyncio
import json
import sys

# Import shared utilities
from xml_utils import _resolve_file_path, setup_python_path, get_api_url, ensure_server_running

# Set up Python path
setup_python_path()

# Import project modules
from agent_provocateur.mcp_client import McpClient
from agent_provocateur.xml_parser import load_xml_file, identify_researchable_nodes


async def list_xml_docs(args):
    """List all XML documents."""
    client = McpClient(base_url=args.server)
    docs = await client.list_documents(doc_type="xml")
    if args.json:
        print(json.dumps([doc.dict() for doc in docs], indent=2))
    else:
        print(f"Found {len(docs)} XML documents:")
        for doc in docs:
            # Check if it's an XmlDocument with root_element
            root_element = getattr(doc, 'root_element', 'Unknown')
            print(f"  - {doc.doc_id}: {doc.title} ({root_element})")


async def get_xml_doc(args):
    """Get a specific XML document."""
    client = McpClient(base_url=args.server)
    doc = await client.get_document(args.doc_id)
    
    if args.json:
        # Output as JSON
        print(json.dumps(doc.dict(), indent=2))
        return
    
    print(f"Document: {doc.doc_id}")
    print(f"Title: {doc.title}")
    print(f"Type: {doc.doc_type}")
    
    if hasattr(doc, 'root_element'):
        print(f"Root Element: {doc.root_element}")
    
    if args.content:
        print("\nContent:")
        print("=" * 50)
        print(doc.content)
        print("=" * 50)
    
    if args.nodes and hasattr(doc, 'researchable_nodes'):
        print("\nResearchable Nodes:")
        print("=" * 50)
        for i, node in enumerate(doc.researchable_nodes, 1):
            path = node.get('xpath', 'Unknown')
            confidence = node.get('confidence', 0.0)
            print(f"{i}. {path} (confidence: {confidence:.2f})")
            if 'evidence' in node and node['evidence']:
                print(f"   Evidence: {node['evidence']}")
        print("=" * 50)


async def upload_xml_doc(args):
    """Upload a new XML document."""
    file_path = _resolve_file_path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return
    
    # Load the XML file
    xml_content = file_path.read_text()
    
    # Parse the file to get the root element
    try:
        root_element = load_xml_file(file_path).tag
    except Exception as e:
        print(f"Error parsing XML file: {e}")
        return
    
    # Create client and upload
    client = McpClient(base_url=args.server)
    
    if args.analyze:
        # Identify researchable nodes
        print("Analyzing XML for researchable nodes...")
        nodes = identify_researchable_nodes(file_path)
        print(f"Found {len(nodes)} researchable nodes")
        
        # Create document with researchable nodes
        try:
            result = await client.create_xml_document(
                title=args.title or file_path.stem,
                content=xml_content,
                root_element=root_element,
                researchable_nodes=nodes
            )
            print(f"Uploaded document with ID: {result.doc_id}")
            
        except Exception as e:
            print(f"Error uploading document: {e}")
    else:
        # Create document without analysis
        try:
            result = await client.create_xml_document(
                title=args.title or file_path.stem,
                content=xml_content,
                root_element=root_element
            )
            print(f"Uploaded document with ID: {result.doc_id}")
            
        except Exception as e:
            print(f"Error uploading document: {e}")


def main():
    parser = argparse.ArgumentParser(description='XML Document CLI')
    parser.add_argument('--server', default=get_api_url(), help='Server URL')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all XML documents')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get a specific XML document')
    get_parser.add_argument('doc_id', help='Document ID')
    get_parser.add_argument('--content', action='store_true', help='Show content')
    get_parser.add_argument('--nodes', action='store_true', help='Show researchable nodes')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a new XML document')
    upload_parser.add_argument('file', help='XML file to upload')
    upload_parser.add_argument('--title', help='Document title (default: filename)')
    upload_parser.add_argument('--analyze', action='store_true', 
                             help='Analyze for researchable nodes')
    
    args = parser.parse_args()
    
    # Check if server is running
    ensure_server_running()
    
    if args.command == 'list':
        asyncio.run(list_xml_docs(args))
    elif args.command == 'get':
        asyncio.run(get_xml_doc(args))
    elif args.command == 'upload':
        asyncio.run(upload_xml_doc(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()