#!/usr/bin/env python
"""
Test script for the WebSearchAgent with MCP integration.

This script runs a simple search query using the WebSearchAgent
to verify that the Web Search MCP integration works correctly.

Usage:
  python scripts/test_web_search.py --query "your search query"
"""

import os
import sys
import argparse
import asyncio
import logging
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_dir))

from agent_provocateur.web_search_agent import WebSearchAgent
from agent_provocateur.a2a_models import TaskRequest

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test WebSearchAgent with MCP integration")
    parser.add_argument(
        "--query", 
        type=str, 
        default="Why is the sky blue?",
        help="Search query to test"
    )
    parser.add_argument(
        "--provider", 
        type=str, 
        default="brave",
        help="Search provider to use (default: brave)"
    )
    parser.add_argument(
        "--max-results", 
        type=int, 
        default=5,
        help="Maximum number of results to return"
    )
    return parser.parse_args()

async def main():
    """Run a test search using the WebSearchAgent."""
    args = parse_args()
    
    # Create the agent
    agent = WebSearchAgent(agent_id="test-web-search-agent")
    
    try:
        # Initialize the agent
        print(f"Initializing WebSearchAgent...")
        await agent.start()
        
        # Set the provider preference if specified
        if args.provider:
            os.environ["DEFAULT_SEARCH_PROVIDER"] = args.provider
            agent.search_config["preferred_provider"] = args.provider
            print(f"Using search provider: {args.provider}")
        
        # Create a task request
        task_request = TaskRequest(
            task_id="test-search-task",
            intent="search",
            payload={
                "query": args.query,
                "max_results": args.max_results
            },
            source_agent="test-script",
            target_agent="web-search-agent"
        )
        
        # Execute the search
        print(f"Searching for: {args.query}")
        result = await agent.handle_task_request(task_request)
        
        # Print the results
        if result.get("status") == "completed":
            print(f"\nSearch Results ({result.get('result_count', 0)}):")
            print("=" * 50)
            
            for i, item in enumerate(result.get("results", [])):
                print(f"{i+1}. {item.get('title')}")
                print(f"   URL: {item.get('url')}")
                print(f"   Confidence: {item.get('confidence'):.2f}")
                print(f"   {item.get('snippet')}")
                print()
                
            print("\nSources:")
            print("=" * 50)
            for i, source in enumerate(result.get("sources", [])):
                print(f"{i+1}. {source.get('title')}")
                print(f"   Type: {source.get('source_type')}")
                print(f"   Confidence: {source.get('confidence'):.2f}")
                print(f"   Citation: {source.get('citation')}")
                print()
        else:
            print(f"Error: {result.get('error')}")
    finally:
        # Stop the agent
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())