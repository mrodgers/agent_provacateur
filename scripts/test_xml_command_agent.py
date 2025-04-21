#!/usr/bin/env python3
"""
Test the XML Command Agent directly without going through the Goal Refiner.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import the agent_provocateur package
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_provocateur.a2a_models import TaskRequest
from scripts.xml_command_agent import XmlCommandAgent
from agent_provocateur.a2a_messaging import InMemoryMessageBroker

async def test_extract_commands(agent, doc_id):
    """Test the extract_entities capability."""
    # Create a task request
    task_request = TaskRequest(
        task_id="test_extract",
        source_agent="test",
        target_agent="xml_agent",
        intent="extract_entities",
        payload={
            "doc_id": doc_id,
            "extract_type": "commands",
            "format": "text"
        }
    )
    
    # Process the request directly
    result = await agent.handle_extract_entities(task_request)
    
    # Print result summary
    print(f"\nExtraction completed with {result.get('command_count', 0)} command blocks")
    print("\nFormatted Output:")
    print("=" * 60)
    print(result.get("formatted_output", "No output available"))
    print("=" * 60)
    
    return result

async def test_validate_xml(agent, doc_id):
    """Test the validate capability."""
    # Create a task request
    task_request = TaskRequest(
        task_id="test_validate",
        source_agent="test",
        target_agent="xml_agent",
        intent="validate",
        payload={
            "doc_id": doc_id,
            "validation_level": "standard"
        }
    )
    
    # Process the request directly
    result = await agent.handle_validate(task_request)
    
    # Print result
    print(f"\nValidation completed - Document is {'valid' if result.get('is_valid', False) else 'invalid'}")
    if result.get("issues"):
        print("\nIssues found:")
        for issue in result.get("issues", []):
            print(f"- {issue.get('severity', 'unknown')}: {issue.get('message', 'No message')}")
    
    return result

async def main():
    """Run tests for the XML Command Agent."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <doc_id>")
        print(f"Example: {sys.argv[0]} xml3")
        sys.exit(1)
        
    doc_id = sys.argv[1]
    
    # Create message broker and agent
    broker = InMemoryMessageBroker()
    agent = XmlCommandAgent("xml_agent", broker)
    
    # Start the agent
    await agent.start()
    
    try:
        print(f"Testing XML Command Agent with document: {doc_id}")
        
        # Test extract_entities
        extract_result = await test_extract_commands(agent, doc_id)
        
        # Test validate
        validate_result = await test_validate_xml(agent, doc_id)
        
    finally:
        # Stop the agent
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())