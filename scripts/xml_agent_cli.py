#!/usr/bin/env python3
# Path to run: scripts/xml_agent_cli.py
"""
Command-line tool for XML Agent functionality in Agent Provocateur.

This tool allows interactive testing of the XML Agent for advanced
node identification and verification planning.
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
from agent_provocateur.xml_agent import XmlAgent


async def identify_xml_nodes(args):
    """Identify researchable nodes in an XML document."""
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
            print(json.dumps(nodes, indent=2))
        else:
            print(f"Found {len(nodes)} researchable nodes:")
            for i, node in enumerate(nodes, 1):
                path = node.get('xpath', 'Unknown')
                confidence = node.get('confidence', 0.0)
                print(f"{i}. {path} (confidence: {confidence:.2f})")
                if args.evidence and 'evidence' in node and node['evidence']:
                    print(f"   Evidence: {node['evidence']}")
    
    elif args.doc_id:
        # Use existing document from server
        client = McpClient(base_url=args.server)
        doc = await client.get_document(args.doc_id)
        
        agent = XmlAgent()
        
        # Identify nodes
        print(f"Analyzing document {args.doc_id}...")
        nodes = await agent.analyze_document(
            doc, 
            min_confidence=args.confidence,
            rules_file=args.rules_file
        )
        
        # Output results
        if args.json:
            print(json.dumps(nodes, indent=2))
        else:
            print(f"Found {len(nodes)} researchable nodes:")
            for i, node in enumerate(nodes, 1):
                path = node.get('xpath', 'Unknown')
                confidence = node.get('confidence', 0.0)
                print(f"{i}. {path} (confidence: {confidence:.2f})")
                if args.evidence and 'evidence' in node and node['evidence']:
                    print(f"   Evidence: {node['evidence']}")
    
    else:
        print("Error: Either --file or --doc_id must be specified")


async def plan_verification(args):
    """Plan verification for an XML document."""
    client = McpClient(base_url=args.server)
    doc = await client.get_document(args.doc_id)
    
    agent = XmlAgent()
    
    # Create verification plan
    print(f"Creating verification plan for document {args.doc_id}...")
    plan = await agent.create_verification_plan(doc)
    
    # Output results
    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print("\nVerification Plan:")
        print("=" * 50)
        print(f"Document: {doc.doc_id} - {doc.title}")
        print(f"Root Element: {getattr(doc, 'root_element', 'Unknown')}")
        print(f"Total tasks: {len(plan)}")
        print("=" * 50)
        
        for i, task in enumerate(plan, 1):
            print(f"\nTask {i}: {task.get('task_type', 'Unknown')}")
            print(f"Node: {task.get('xpath', 'Unknown')}")
            print(f"Priority: {task.get('priority', 0)}")
            if 'search_query' in task:
                print(f"Search query: {task['search_query']}")
            if 'note' in task:
                print(f"Note: {task['note']}")
            if 'verification_steps' in task:
                print("Verification steps:")
                for j, step in enumerate(task['verification_steps'], 1):
                    print(f"  {j}. {step}")


async def verify_xml(args):
    """Run verification on an XML document."""
    client = McpClient(base_url=args.server)
    doc = await client.get_document(args.doc_id)
    
    agent = XmlAgent()
    
    # Run verification
    print(f"Verifying document {args.doc_id}...")
    print(f"Search depth: {args.search_depth}")
    
    results = await agent.verify_document(
        doc, 
        search_depth=args.search_depth,
        max_nodes=args.max_nodes
    )
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("\nVerification Results:")
        print("=" * 50)
        print(f"Document: {doc.doc_id} - {doc.title}")
        print(f"Nodes verified: {len(results)}")
        print("=" * 50)
        
        for i, result in enumerate(results, 1):
            print(f"\nNode {i}: {result.get('xpath', 'Unknown')}")
            print(f"Confidence: {result.get('confidence', 0.0):.2f}")
            
            if 'verification_result' in result:
                vr = result['verification_result']
                print(f"Verified: {vr.get('verified', False)}")
                print(f"Confidence score: {vr.get('confidence_score', 0.0):.2f}")
                
                if 'evidence' in vr:
                    print("Evidence:")
                    for j, evidence in enumerate(vr['evidence'], 1):
                        print(f"  {j}. {evidence}")
                
                if 'search_results' in vr:
                    print(f"Search results: {len(vr['search_results'])}")
                    if args.verbose:
                        for j, sr in enumerate(vr['search_results'], 1):
                            print(f"  {j}. {sr.get('title', 'Untitled')}")
                            print(f"     URL: {sr.get('url', 'N/A')}")
                            if 'snippet' in sr:
                                print(f"     Snippet: {sr['snippet'][:100]}...")


def main():
    parser = argparse.ArgumentParser(description='XML Agent CLI')
    parser.add_argument('--server', default=get_api_url(), help='Server URL')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Identify command
    identify_parser = subparsers.add_parser('identify', help='Identify researchable nodes')
    identify_parser.add_argument('--file', help='XML file to analyze')
    identify_parser.add_argument('--doc_id', help='Document ID to analyze')
    identify_parser.add_argument('--confidence', type=float, default=0.5, 
                               help='Minimum confidence threshold (0.0-1.0)')
    identify_parser.add_argument('--rules-file', help='Path to custom rules file')
    identify_parser.add_argument('--evidence', action='store_true', 
                               help='Show evidence for each node')
    
    # Plan command
    plan_parser = subparsers.add_parser('plan', help='Create verification plan')
    plan_parser.add_argument('doc_id', help='Document ID to plan verification for')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify XML document')
    verify_parser.add_argument('doc_id', help='Document ID to verify')
    verify_parser.add_argument('--search-depth', choices=['low', 'medium', 'high'],
                             default='medium', help='Search depth for verification')
    verify_parser.add_argument('--max-nodes', type=int, default=5,
                             help='Maximum number of nodes to verify')
    verify_parser.add_argument('--verbose', action='store_true',
                             help='Show detailed results')
    
    args = parser.parse_args()
    
    # Check if server is running
    ensure_server_running()
    
    if args.command == 'identify':
        asyncio.run(identify_xml_nodes(args))
    elif args.command == 'plan':
        asyncio.run(plan_verification(args))
    elif args.command == 'verify':
        asyncio.run(verify_xml(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()