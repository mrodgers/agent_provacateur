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
from pathlib import Path

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
            if hasattr(doc, 'root_element'):
                print(f"- {doc.doc_id}: {doc.title} ({doc.root_element})")
            else:
                print(f"- {doc.doc_id}: {doc.title} (XML Document)")


async def get_xml_doc(args):
    """Get a specific XML document."""
    client = McpClient(base_url=args.server)
    try:
        doc = await client.get_xml_document(args.id)
        if args.json:
            print(json.dumps(doc.dict(), indent=2))
        else:
            print(f"XML Document: {doc.title} ({doc.doc_id})")
            print(f"Root Element: {doc.root_element}")
            print(f"Namespaces: {doc.namespaces}")
            print(f"Created At: {doc.created_at}")
            print(f"Updated At: {doc.updated_at}")
            print(f"Researchable Nodes: {len(doc.researchable_nodes)}")
            
            # Show content if requested
            if args.content:
                print("\nContent:")
                print(doc.content)
            
            # Show nodes if requested
            if args.nodes:
                print("\nResearchable Nodes:")
                for i, node in enumerate(doc.researchable_nodes):
                    print(f"\nNode {i+1}:")
                    print(f"  XPath: {node.xpath}")
                    print(f"  Element: {node.element_name}")
                    print(f"  Content: {node.content}")
                    print(f"  Attributes: {node.attributes}")
                    print(f"  Status: {node.verification_status}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


async def upload_xml(args):
    """Upload a new XML document."""
    client = McpClient(base_url=args.server)
    try:
        # Load XML from file
        file_path = args.file
        # If it's a relative path in examples, adjust it
        if not file_path.startswith('/'):
            file_path = f"examples/{file_path}"
            
        xml_file_path = Path(file_path)
        if not xml_file_path.exists():
            print(f"Error: File {xml_file_path} does not exist")
            sys.exit(1)
        
        xml_content = load_xml_file(str(xml_file_path))
        
        # Check if the content is valid XML
        try:
            nodes = identify_researchable_nodes(xml_content)
            print(f"Found {len(nodes)} researchable nodes")
        except Exception as e:
            print(f"Warning: XML parsing error: {e}")
        
        # Upload the document
        doc = await client.upload_xml(xml_content, args.title)
        
        if args.json:
            print(json.dumps(doc.dict(), indent=2))
        else:
            print(f"Successfully uploaded XML document: {doc.title} ({doc.doc_id})")
            print(f"Root Element: {doc.root_element}")
            print(f"Created At: {doc.created_at}")
            print(f"Researchable Nodes: {len(doc.researchable_nodes)}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="XML document tool for Agent Provocateur")
    parser.add_argument("--server", default="http://localhost:8000", help="MCP server URL")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List XML documents")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get an XML document")
    get_parser.add_argument("id", help="Document ID")
    get_parser.add_argument("--content", action="store_true", help="Show document content")
    get_parser.add_argument("--nodes", action="store_true", help="Show researchable nodes")
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload an XML document")
    upload_parser.add_argument("file", help="Path to XML file")
    upload_parser.add_argument("--title", required=True, help="Document title")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "list":
        asyncio.run(list_xml_docs(args))
    elif args.command == "get":
        asyncio.run(get_xml_doc(args))
    elif args.command == "upload":
        asyncio.run(upload_xml(args))


if __name__ == "__main__":
    main()