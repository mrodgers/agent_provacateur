#!/usr/bin/env python3
"""
Unified Command-line tool for working with XML documents in Agent Provocateur.

This tool provides comprehensive XML functionality including:
- Document management (list, get, upload)
- Node analysis and extraction
- Command extraction (for Cisco guides)
- GraphRAG-enhanced entity linking
- Validation and verification

Usage:
  ./unified_xml_cli.py list                     # List all XML documents
  ./unified_xml_cli.py get DOC_ID               # Get a specific XML document
  ./unified_xml_cli.py upload FILE              # Upload a new XML document
  ./unified_xml_cli.py nodes DOC_ID             # Get researchable nodes
  ./unified_xml_cli.py analyze FILE             # Analyze XML using XmlAgent
  ./unified_xml_cli.py entities DOC_ID          # Extract entities with GraphRAG
  ./unified_xml_cli.py commands DOC_ID          # Extract Cisco commands
  ./unified_xml_cli.py validate DOC_ID          # Validate XML structure
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Import shared utilities
from xml_utils import _resolve_file_path, setup_python_path, get_api_url, ensure_server_running

# Set up Python path
setup_python_path()

# Import project modules
from agent_provocateur.mcp_client import McpClient
from agent_provocateur.xml_parser import load_xml_file, identify_researchable_nodes
from agent_provocateur.xml_agent import XmlAgent
from agent_provocateur.xml_graphrag_agent import XmlGraphRAGAgent

# Optional imports for Cisco command extraction
try:
    import re
except ImportError:
    pass

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
    print(f"Created: {doc.created_at}")
    print(f"Root element: {getattr(doc, 'root_element', 'Unknown')}")
    
    if args.content:
        print("\nContent:")
        print("--------")
        content = await client.get_xml_content(args.doc_id)
        print(content)


async def upload_xml_doc(args):
    """Upload a new XML document."""
    file_path = _resolve_file_path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return
    
    # Read XML content
    try:
        with open(file_path, 'r') as f:
            xml_content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Upload to server
    client = McpClient(base_url=args.server)
    title = args.title or file_path.stem
    
    try:
        doc = await client.upload_xml(xml_content, title)
        print(f"Successfully uploaded document: {doc.doc_id}")
        print(f"Title: {doc.title}")
        print(f"Researchable nodes: {len(doc.researchable_nodes)}")
    except Exception as e:
        print(f"Error uploading document: {e}")


async def get_xml_nodes(args):
    """Get researchable nodes for an XML document."""
    client = McpClient(base_url=args.server)
    
    try:
        nodes = await client.get_xml_nodes(args.doc_id)
        
        if args.json:
            print(json.dumps([node.dict() for node in nodes], indent=2))
        else:
            print(f"Found {len(nodes)} researchable nodes:")
            for i, node in enumerate(nodes, 1):
                content = node.content or "N/A"
                if len(content) > 60:
                    content = content[:57] + "..."
                attrs = ", ".join(f"{k}={v}" for k, v in node.attributes.items()) if node.attributes else ""
                print(f"  {i}. {node.element_name} {attrs}: {content}")
    except Exception as e:
        print(f"Error getting nodes: {e}")


async def analyze_xml(args):
    """Analyze XML file with the XML Agent."""
    if args.file:
        file_path = _resolve_file_path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return
        
        # Create XML agent
        agent = XmlAgent()
        
        # Identify nodes
        print(f"Analyzing {file_path}...")
        nodes = await agent.identify_researchable_nodes(
            file_path, 
            min_confidence=args.confidence,
            rules_file=args.rules_file
        )
        
        # Output results
        if args.json:
            print(json.dumps([node.dict() for node in nodes], indent=2))
        else:
            print(f"Found {len(nodes)} researchable nodes:")
            for i, node in enumerate(nodes, 1):
                content = node.content or "N/A"
                if len(content) > 60:
                    content = content[:57] + "..."
                attrs = ", ".join(f"{k}={v}" for k, v in node.attributes.items()) if node.attributes else ""
                print(f"  {i}. {node.element_name} {attrs}: {content}")


async def extract_entities(args):
    """Extract entities from XML with GraphRAG integration."""
    if not args.doc_id:
        print("Error: Document ID is required")
        return
    
    # Use GraphRAG-enhanced XML agent for better entity extraction
    agent = XmlGraphRAGAgent()
    await agent.on_startup()  # Initialize the agent
    
    print(f"Extracting entities from document {args.doc_id}...")
    
    # Task request format
    task_request = {
        "intent": "extract_entities",
        "payload": {
            "doc_id": args.doc_id,
            "use_graphrag": True,
            "min_confidence": args.confidence or 0.6
        }
    }
    
    try:
        # Convert to TaskRequest format that the agent expects
        from agent_provocateur.a2a_models import TaskRequest
        request = TaskRequest(
            task_id=f"task_{args.doc_id}",
            intent="extract_entities",
            payload=task_request["payload"]
        )
        
        # Process extraction
        result = await agent.handle_extract_entities(request)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Extracted {len(result.get('entities', []))} entities:")
            for entity in result.get("entities", []):
                print(f"  - {entity.get('name')}: {entity.get('entity_type')} ({entity.get('confidence', 0.0):.2f})")
                
            if "relationships" in result and result["relationships"]:
                print("\nDetected relationships:")
                for rel in result["relationships"]:
                    source = rel.get("source_entity", {}).get("name", "unknown")
                    target = rel.get("target_entity", {}).get("name", "unknown")
                    relation = rel.get("relation_type", "related")
                    print(f"  - {source} {relation} {target}")
    except Exception as e:
        print(f"Error extracting entities: {e}")


async def extract_cisco_commands(args):
    """Extract configuration commands from Cisco guide XML."""
    client = McpClient(base_url=args.server)
    
    print(f"Fetching XML content for document {args.doc_id}...")
    
    try:
        # Get the XML content
        xml_content = await client.get_xml_content(args.doc_id)
        
        # Parse the XML to extract code blocks
        code_blocks = re.findall(r'<code-block>(.*?)</code-block>', xml_content, re.DOTALL)
        
        print(f"Found {len(code_blocks)} code blocks")
        
        if args.json:
            json_result = {
                "doc_id": args.doc_id,
                "command_blocks": [
                    {
                        "id": i,
                        "content": "\n".join(line.strip() for line in block.strip().split("\n"))
                    } for i, block in enumerate(code_blocks, 1)
                ]
            }
            print(json.dumps(json_result, indent=2))
        else:
            print("\n=== Configuration Commands ===\n")
            
            # Process and display each code block
            for i, block in enumerate(code_blocks, 1):
                # Clean up the block (remove leading/trailing whitespace and indentation)
                clean_block = "\n".join(line.strip() for line in block.strip().split("\n"))
                
                print(f"Command Block {i}:")
                print("-------------------")
                print(clean_block)
                print("-------------------\n")
        
        # Generate a summary if requested
        if args.summary:
            print("\nGenerating structured command summary...")
            all_blocks = "\n\n".join([
                "\n".join(line.strip() for line in block.strip().split("\n"))
                for block in code_blocks
            ])
            
            response = await client.generate_text(
                prompt=f"Summarize the following Cisco router configuration commands in a structured format, grouping similar commands and explaining their purpose:\n\n{all_blocks}",
                max_tokens=1000,
                temperature=0.3
            )
            
            print("\n=== Command Summary ===\n")
            print(response.content)
    
    except Exception as e:
        print(f"Error extracting commands: {e}")


async def validate_xml(args):
    """Validate XML document structure and syntax."""
    client = McpClient(base_url=args.server)
    
    try:
        if args.doc_id:
            # Get XML from server
            xml_content = await client.get_xml_content(args.doc_id)
            print(f"Validating XML document {args.doc_id}...")
        elif args.file:
            # Read from file
            file_path = _resolve_file_path(args.file)
            if not file_path.exists():
                print(f"Error: File not found: {file_path}")
                return
            
            with open(file_path, 'r') as f:
                xml_content = f.read()
            print(f"Validating XML file {file_path}...")
        else:
            print("Error: Either --doc-id or --file must be specified")
            return
        
        # Basic XML well-formedness check
        try:
            from lxml import etree
            parser = etree.XMLParser(recover=True)
            root = etree.fromstring(xml_content.encode('utf-8'), parser)
            
            if parser.error_log:
                print("\n=== XML Validation Errors ===")
                for error in parser.error_log:
                    print(f"Line {error.line}, Column {error.column}: {error.message}")
                print(f"\nTotal errors: {len(parser.error_log)}")
            else:
                print("XML is well-formed.")
                
                # Show basic structure
                print("\n=== XML Structure ===")
                print(f"Root element: {root.tag}")
                
                namespaces = root.nsmap
                if namespaces:
                    print("\nNamespaces:")
                    for prefix, uri in namespaces.items():
                        prefix_str = prefix or "(default)"
                        print(f"  {prefix_str}: {uri}")
                
                # Count elements by type
                element_counts = {}
                for elem in root.iter():
                    tag = elem.tag
                    if '}' in tag:
                        tag = tag.split('}', 1)[1]  # Remove namespace
                    element_counts[tag] = element_counts.get(tag, 0) + 1
                
                print("\nElement counts:")
                for tag, count in sorted(element_counts.items(), key=lambda x: (-x[1], x[0]))[:10]:
                    print(f"  {tag}: {count}")
                
                if len(element_counts) > 10:
                    print(f"  ... and {len(element_counts) - 10} more element types")
                
        except Exception as e:
            print(f"XML parsing error: {e}")
    
    except Exception as e:
        print(f"Error validating XML: {e}")


def setup_parser():
    """Set up command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Unified XML CLI for Agent Provocateur",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Common arguments
    parser.add_argument("--server", help="Server URL", default=get_api_url())
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # List documents
    list_parser = subparsers.add_parser("list", help="List XML documents")
    
    # Get document
    get_parser = subparsers.add_parser("get", help="Get XML document details")
    get_parser.add_argument("doc_id", help="Document ID")
    get_parser.add_argument("--content", action="store_true", help="Show document content")
    
    # Upload document
    upload_parser = subparsers.add_parser("upload", help="Upload XML document")
    upload_parser.add_argument("file", help="XML file path")
    upload_parser.add_argument("--title", help="Document title (defaults to filename)")
    
    # Get nodes
    nodes_parser = subparsers.add_parser("nodes", help="Get researchable nodes")
    nodes_parser.add_argument("doc_id", help="Document ID")
    
    # Analyze XML
    analyze_parser = subparsers.add_parser("analyze", help="Analyze XML with XML Agent")
    analyze_parser.add_argument("file", help="XML file path")
    analyze_parser.add_argument("--confidence", type=float, default=0.5, help="Minimum confidence (0.0-1.0)")
    analyze_parser.add_argument("--rules-file", help="Custom rules file")
    
    # Extract entities
    entities_parser = subparsers.add_parser("entities", help="Extract entities with GraphRAG")
    entities_parser.add_argument("doc_id", help="Document ID")
    entities_parser.add_argument("--confidence", type=float, default=0.6, help="Minimum confidence (0.0-1.0)")
    
    # Extract Cisco commands
    commands_parser = subparsers.add_parser("commands", help="Extract Cisco commands")
    commands_parser.add_argument("doc_id", help="Document ID")
    commands_parser.add_argument("--summary", action="store_true", help="Generate command summary")
    
    # Validate XML
    validate_parser = subparsers.add_parser("validate", help="Validate XML structure")
    validate_group = validate_parser.add_mutually_exclusive_group(required=True)
    validate_group.add_argument("--doc-id", help="Document ID")
    validate_group.add_argument("--file", help="XML file path")
    
    return parser


async def main():
    """Main entry point."""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Check if server is running if needed
    client_commands = ["list", "get", "upload", "nodes", "entities", "commands"]
    if args.command in client_commands:
        server_running = await ensure_server_running(args.server)
        if not server_running:
            print(f"Error: Could not connect to server at {args.server}")
            return
    
    # Execute command
    commands = {
        "list": list_xml_docs,
        "get": get_xml_doc,
        "upload": upload_xml_doc,
        "nodes": get_xml_nodes,
        "analyze": analyze_xml,
        "entities": extract_entities,
        "commands": extract_cisco_commands,
        "validate": validate_xml
    }
    
    if args.command in commands:
        await commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())