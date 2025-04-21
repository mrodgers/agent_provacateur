#!/usr/bin/env python3
"""
Demonstration of the Goal Refiner with XML processing capabilities.
This script:
1. Starts the necessary agents
2. Accepts a high-level goal from the user
3. Uses Goal Refiner to break it down into tasks
4. Has the appropriate agents process the tasks
5. Returns the results
"""

import asyncio
import sys
import json
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the agent_provocateur package
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_provocateur.a2a_messaging import InMemoryMessageBroker
from agent_provocateur.a2a_models import TaskRequest
from agent_provocateur.research_supervisor_agent import ResearchSupervisorAgent
from scripts.xml_command_agent import XmlCommandAgent

async def run_goal_refiner_demo(goal: str, doc_id: str = None, json_output: bool = False):
    """Run a full demonstration of the Goal Refiner with XML Command Agent."""
    # Create message broker for inter-agent communication
    broker = InMemoryMessageBroker()
    
    # Create the agents
    supervisor = ResearchSupervisorAgent("research_supervisor_agent", broker)
    xml_agent = XmlCommandAgent("xml_agent", broker)
    
    # Start the agents
    await supervisor.start()
    await xml_agent.start()
    
    try:
        print(f"\n===== Goal Refiner Demo =====")
        print(f"Goal: {goal}")
        if doc_id:
            print(f"Document ID: {doc_id}")
        print()
        
        # Build options
        options = {}
        if doc_id:
            options["doc_id"] = doc_id
        
        # Prepare the goal request
        task_request = TaskRequest(
            task_id="demo_goal",
            source_agent="demo",
            target_agent=supervisor.agent_id,
            intent="process_goal",
            payload={
                "goal": goal,
                "options": options
            }
        )
        
        # Process the goal - this will refine it and execute the tasks
        print("Processing goal...")
        result = await supervisor.handle_process_goal(task_request)
        
        # Print the result
        if json_output:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"\n===== Goal Processing Results =====")
            print(f"Workflow ID: {result.get('workflow_id')}")
            print(f"Tasks: {result.get('task_count', 0)}")
            print(f"Status: {result.get('status', 'unknown')}")
            
            # Print task results
            task_results = result.get("results", [])
            for i, task_result in enumerate(task_results, 1):
                print(f"\n----- Task {i}: {task_result.get('description', 'Unnamed task')} -----")
                print(f"Agent: {task_result.get('agent', 'unknown')}")
                print(f"Intent: {task_result.get('intent', 'unknown')}")
                
                # Get the result from this task
                task_output = task_result.get("result", {})
                
                # Different formatting based on task type
                if task_result.get("intent") == "extract_entities":
                    command_count = task_output.get("command_count", 0)
                    print(f"Command Count: {command_count}")
                    
                    # Show the formatted output, if available
                    formatted_output = task_output.get("formatted_output")
                    if formatted_output:
                        print("\nExtracted Commands:")
                        print("=" * 60)
                        print(formatted_output[:500] + "..." if len(formatted_output) > 500 else formatted_output)
                        print("=" * 60)
                
                elif task_result.get("intent") == "validate":
                    is_valid = task_output.get("is_valid", False)
                    print(f"Validation: {'Valid' if is_valid else 'Invalid'}")
                    
                    # Show issues, if any
                    issues = task_output.get("issues", [])
                    if issues:
                        print("\nIssues:")
                        for issue in issues:
                            print(f"- {issue.get('severity', 'unknown')}: {issue.get('message', 'No message')}")
                
                else:
                    # Generic result display
                    status = task_output.get("status", "unknown")
                    print(f"Status: {status}")
                    
                    if "error" in task_output:
                        print(f"Error: {task_output.get('error')}")
        
        return result
        
    finally:
        # Stop the agents
        await supervisor.stop()
        await xml_agent.stop()

async def main():
    """Parse command line arguments and run the demo."""
    parser = argparse.ArgumentParser(description="Goal Refiner Demo")
    parser.add_argument("goal", help="High-level goal to process")
    parser.add_argument("--doc-id", help="Document ID to process")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    await run_goal_refiner_demo(args.goal, args.doc_id, args.json)

if __name__ == "__main__":
    asyncio.run(main())