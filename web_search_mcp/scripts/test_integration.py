#!/usr/bin/env python3
"""
Test script for verifying the integration between Web Search MCP server 
and Agent Provocateur's WebSearchAgent.

This script creates an instance of WebSearchAgent and tests basic search
functionality with source attribution.

Usage:
    python test_integration.py --query "your search query" --provider brave
"""

import os
import sys
import json
import asyncio
import argparse
import logging
from typing import Dict, Any, List

# Add parent directory to path so we can import agent_provocateur
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".."))

try:
    from agent_provocateur.mcp_client import McpClient
    from agent_provocateur.models import Source, SourceType
    from agent_provocateur.a2a_models import TaskRequest
except ImportError:
    print("Error: Could not import Agent Provocateur modules.")
    print("Make sure Agent Provocateur is installed or added to your PYTHONPATH.")
    sys.exit(1)

# Import our WebSearchAgent implementation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration.web_search_agent_integration import WebSearchAgent

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("web_search_test")

class TestWebSearchAgent(WebSearchAgent):
    """
    Test version of WebSearchAgent that can run independently.
    """
    
    def __init__(self):
        """Initialize the test agent."""
        # Initialize the logger since we don't have BaseAgent.__init__
        self.logger = logging.getLogger("TestWebSearchAgent")
        self.logger.setLevel(logging.INFO)
        
    async def setup(self):
        """Set up the agent for testing."""
        await self.on_startup()
        
    async def perform_search(self, query: str, provider: str = None, max_results: int = 5) -> Dict[str, Any]:
        """
        Perform a search with the given query.
        
        Args:
            query: The search query
            provider: Optional provider override
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with search results and sources
        """
        # Override the preferred provider if specified
        if provider:
            self.search_config["preferred_provider"] = provider
            self.logger.info(f"Using provider: {provider}")
        
        # Create a task request
        task_request = TaskRequest(
            task_id="test_search_task",
            agent_id="test_web_search_agent",
            task_type="web_search",
            payload={
                "query": query,
                "max_results": max_results
            }
        )
        
        # Call the handler
        return await self.handle_search(task_request)
    
    def print_results(self, results: Dict[str, Any]):
        """
        Print the search results in a readable format.
        
        Args:
            results: The search results from handle_search
        """
        if "error" in results:
            print(f"Error: {results['error']}")
            return
            
        print(f"\n=== Search results for: {results['query']} ===")
        print(f"Found {results['result_count']} results\n")
        
        # Print each result with its source attribution
        for i, result in enumerate(results.get("results", [])):
            print(f"[{i+1}] {result['title']}")
            print(f"    {result['snippet']}")
            print(f"    URL: {result['url']}")
            print(f"    Confidence: {result['confidence']:.2f}")
            print(f"    Source ID: {result['source_id']}")
            print()
            
        # Print sources
        print("\n=== Sources ===")
        for source in results.get("sources", []):
            source_obj = source if isinstance(source, dict) else source.dict()
            print(f"ID: {source_obj['source_id']}")
            print(f"Type: {source_obj['source_type']}")
            print(f"Title: {source_obj['title']}")
            print(f"URL: {source_obj.get('url', 'N/A')}")
            print(f"Confidence: {source_obj['confidence']:.2f}")
            print(f"Citation: {source_obj.get('citation', 'N/A')}")
            print()

async def main():
    """Run the test script."""
    parser = argparse.ArgumentParser(description="Test the Web Search MCP integration")
    parser.add_argument("--query", type=str, required=True, help="Search query to test")
    parser.add_argument("--provider", type=str, default="brave", 
                        choices=["brave", "google", "bing"], 
                        help="Search provider to use")
    parser.add_argument("--max-results", type=int, default=5, 
                        help="Maximum number of results to return")
    parser.add_argument("--json", action="store_true", 
                        help="Output results as JSON")
    
    args = parser.parse_args()
    
    try:
        # Create and set up the test agent
        agent = TestWebSearchAgent()
        await agent.setup()
        
        # Perform the search
        logger.info(f"Performing search: {args.query} (provider: {args.provider})")
        results = await agent.perform_search(
            query=args.query, 
            provider=args.provider,
            max_results=args.max_results
        )
        
        # Output results
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            agent.print_results(results)
            
    except Exception as e:
        logger.error(f"Error testing web search: {e}", exc_info=True)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))