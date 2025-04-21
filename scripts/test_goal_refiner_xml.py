#!/usr/bin/env python3
"""
Test script for the enhanced Goal Refiner with XML processing capabilities.
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add the parent directory to the path so we can import the agent_provocateur package
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_provocateur.research_supervisor_agent import ResearchSupervisorAgent
from agent_provocateur.a2a_messaging import InMemoryMessageBroker
from agent_provocateur.a2a_models import TaskRequest

async def test_goal_refiner(goal: str, options: Dict[str, Any] = None):
    """Test the goal refiner with a specific goal."""
    # Create supervisor agent
    broker = InMemoryMessageBroker()
    agent = ResearchSupervisorAgent("research_supervisor_agent", broker)
    
    # Start the agent (initializes capabilities and goal refiner)
    await agent.start()
    
    try:
        print(f"Testing goal: \"{goal}\"")
        
        # Prepare task request
        task_request = TaskRequest(
            task_id="test_goal",
            source_agent="test",
            target_agent="research_supervisor_agent",
            intent="process_goal",
            payload={
                "goal": goal,
                "options": options or {}
            }
        )
        
        # Stage 1: Just refine the goal without executing tasks
        # This allows us to see how the goal gets broken down
        tasks = await agent.goal_refiner.refine_goal(goal)
        
        print("\n=== Refined Tasks ===")
        for i, task in enumerate(tasks, 1):
            print(f"\nTask {i}: {task.get('description')}")
            print(f"Capabilities: {', '.join(task.get('capabilities', []))}")
            print(f"Agent: {task.get('assigned_agent', 'unassigned')}")
            print(f"Priority: {task.get('priority', 'unknown')}")
        
        # Stage 2: Create task payloads
        print("\n=== Task Payloads ===")
        for i, task in enumerate(tasks, 1):
            agent_id = task.get("assigned_agent")
            if agent_id:
                # Map task to intent
                intent = agent._map_task_to_intent(task, agent_id)
                if intent:
                    # Create payload
                    payload = agent._create_task_payload(task, options or {})
                    print(f"\nTask {i} Payload (Agent: {agent_id}, Intent: {intent}):")
                    print(json.dumps(payload, indent=2))
                else:
                    print(f"\nTask {i}: No intent mapping found for {agent_id}")
            else:
                print(f"\nTask {i}: No agent assigned")
        
        return tasks
    
    finally:
        # Stop the agent
        await agent.stop()

async def main():
    """Run tests for various goal types."""
    # Set default options
    options = {"doc_id": "xml3", "max_results": 5}
    
    # Test different goals with XML focus
    await test_goal_refiner("Extract configuration commands from the Cisco router guide", options)
    await test_goal_refiner("Validate the Cisco XML document structure", options)
    await test_goal_refiner("Extract router interface configurations", options)

if __name__ == "__main__":
    asyncio.run(main())