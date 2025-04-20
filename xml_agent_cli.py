#!/usr/bin/env python3
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

from agent_provocateur.mcp_client import McpClient
from agent_provocateur.xml_parser import (
    load_xml_file,
    identify_researchable_nodes,
    identify_researchable_nodes_advanced,
    analyze_xml_verification_needs
)
from agent_provocateur.xml_agent import XmlAgent
from agent_provocateur.a2a_messaging import InMemoryMessageBroker
from agent_provocateur.a2a_models import TaskRequest


async def advanced_identify(args):
    """Identify researchable nodes with advanced rules."""
    try:
        # Load XML file
        if args.file:
            xml_file_path = Path(args.file)
            if not xml_file_path.exists():
                print(f"Error: File {xml_file_path} does not exist")
                sys.exit(1)
            
            xml_content = load_xml_file(str(xml_file_path))
            print(f"Loaded XML file: {xml_file_path}")
        elif args.doc_id:
            client = McpClient(base_url=args.server)
            xml_content = await client.get_xml_content(args.doc_id)
            print(f"Loaded XML document: {args.doc_id}")
        else:
            print("Error: Either --file or --doc_id must be provided")
            sys.exit(1)
        
        # Load custom rules from file if provided
        keyword_rules = None
        attribute_rules = None
        content_patterns = None
        
        if args.rules_file:
            try:
                with open(args.rules_file, 'r') as f:
                    rules = json.load(f)
                
                keyword_rules = rules.get("keyword_rules")
                attribute_rules = rules.get("attribute_rules")
                content_patterns = rules.get("content_patterns")
                
                print(f"Loaded custom rules from {args.rules_file}")
            except Exception as e:
                print(f"Error loading rules file: {e}")
                sys.exit(1)
        
        # Identify nodes
        print(f"Identifying nodes with confidence threshold: {args.confidence}")
        nodes = identify_researchable_nodes_advanced(
            xml_content,
            keyword_rules=keyword_rules,
            attribute_rules=attribute_rules,
            content_patterns=content_patterns,
            min_confidence=args.confidence
        )
        
        # Display results
        print(f"\nFound {len(nodes)} researchable nodes:")
        
        for i, node in enumerate(nodes, 1):
            print(f"\nNode {i}:")
            print(f"  XPath: {node.xpath}")
            print(f"  Element: {node.element_name}")
            print(f"  Content: {node.content}")
            print(f"  Attributes: {node.attributes}")
            print(f"  Confidence: {node.verification_data.get('confidence', 0):.2f}")
            
            # Show evidence if requested
            if args.evidence and "evidence" in node.verification_data:
                print("  Evidence:")
                for evidence in node.verification_data["evidence"]:
                    print(f"    - {evidence}")
        
        # Save results to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump([node.dict() for node in nodes], f, indent=2)
            print(f"\nResults saved to {args.output}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


async def create_verification_plan(args):
    """Create a verification plan for an XML document."""
    try:
        # Initialize XmlAgent
        broker = InMemoryMessageBroker()
        agent = XmlAgent(agent_id="xml_agent", broker=broker, mcp_url=args.server)
        
        # Create request
        task_request = TaskRequest(
            task_id="cli_task",
            source_agent="cli_user",
            intent="create_verification_plan",
            payload={"doc_id": args.doc_id}
        )
        
        # Call the agent
        print(f"Creating verification plan for document: {args.doc_id}")
        result = await agent.handle_create_verification_plan(task_request)
        
        # Display results
        if not result.get("verification_needed", False):
            print(f"\nVerification not needed: {result.get('reason', 'No reason provided')}")
            return
        
        print(f"\nVerification Plan for '{result.get('title')}':")
        print(f"  Priority: {result.get('priority', 'unknown')}")
        print(f"  Nodes: {result.get('node_count', 0)}")
        print(f"  Estimated time: {result.get('estimated_time_minutes', 0)} minutes")
        print(f"  Approach: {result.get('recommended_approach', 'sequential')}")
        
        tasks = result.get("tasks", [])
        print(f"\nTasks ({len(tasks)}):")
        
        for i, task in enumerate(tasks, 1):
            print(f"\nTask {i} - {task['task_id']}:")
            print(f"  Element Type: {task['element_type']}")
            print(f"  Priority: {task['priority']}")
            print(f"  Nodes: {task['node_count']}")
            print(f"  Estimated time: {task['estimated_minutes']} minutes")
        
        # Save results to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nVerification plan saved to {args.output}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


async def batch_verify(args):
    """Test batch verification of nodes in an XML document."""
    try:
        # Initialize XmlAgent
        broker = InMemoryMessageBroker()
        agent = XmlAgent(agent_id="xml_agent", broker=broker, mcp_url=args.server)
        
        # Create request with options
        options = {
            "search_depth": args.search_depth,
            "verify_all": True,
            "strict_mode": args.strict
        }
        
        task_request = TaskRequest(
            task_id="cli_task",
            source_agent="cli_user",
            intent="batch_verify_nodes",
            payload={
                "doc_id": args.doc_id,
                "options": options
            }
        )
        
        # Call the agent
        print(f"Executing batch verification for document: {args.doc_id}")
        print(f"Options: {json.dumps(options, indent=2)}")
        
        result = await agent.handle_batch_verify_nodes(task_request)
        
        # Display results
        print(f"\nVerification Results:")
        print(f"  Total nodes: {result['total_nodes']}")
        print(f"  Completed: {result['completed_nodes']}")
        
        verification_results = result.get("verification_results", [])
        print(f"\nNode Results ({len(verification_results)}):")
        
        for i, node_result in enumerate(verification_results, 1):
            print(f"\nNode {i}:")
            print(f"  XPath: {node_result['xpath']}")
            print(f"  Element: {node_result['element_name']}")
            print(f"  Status: {node_result['status']}")
            print(f"  Confidence: {node_result['confidence']}")
            
            if node_result.get("sources"):
                print("  Sources:")
                for source in node_result["sources"]:
                    print(f"    - {source}")
        
        # Save results to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nVerification results saved to {args.output}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="XML Agent tool for Agent Provocateur")
    parser.add_argument("--server", default="http://localhost:8000", help="MCP server URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Advanced identification command
    identify_parser = subparsers.add_parser("identify", help="Identify researchable nodes with advanced rules")
    identify_parser.add_argument("--file", help="Path to XML file")
    identify_parser.add_argument("--doc_id", help="Document ID if already uploaded")
    identify_parser.add_argument("--confidence", type=float, default=0.5, help="Minimum confidence threshold (0.0-1.0)")
    identify_parser.add_argument("--rules-file", help="JSON file with custom identification rules")
    identify_parser.add_argument("--evidence", action="store_true", help="Show evidence for node selection")
    identify_parser.add_argument("--output", help="Output file to save results (JSON)")
    
    # Verification plan command
    plan_parser = subparsers.add_parser("plan", help="Create verification plan for XML document")
    plan_parser.add_argument("doc_id", help="Document ID")
    plan_parser.add_argument("--output", help="Output file to save verification plan (JSON)")
    
    # Batch verification command
    verify_parser = subparsers.add_parser("verify", help="Test batch verification of nodes")
    verify_parser.add_argument("doc_id", help="Document ID")
    verify_parser.add_argument("--search-depth", choices=["low", "medium", "high"], default="medium", help="Search depth")
    verify_parser.add_argument("--strict", action="store_true", help="Use strict verification mode")
    verify_parser.add_argument("--output", help="Output file to save verification results (JSON)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "identify":
        asyncio.run(advanced_identify(args))
    elif args.command == "plan":
        asyncio.run(create_verification_plan(args))
    elif args.command == "verify":
        asyncio.run(batch_verify(args))


if __name__ == "__main__":
    main()