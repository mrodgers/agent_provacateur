#!/usr/bin/env python
"""
CLI for the Goal Refiner component.
Allows users to enter high-level goals and see how they're broken down into tasks.
"""

import os
import sys
import logging
import asyncio
import argparse
import json
from typing import Dict, Any, List

# Add the parent directory to the path so we can import the agent_provocateur package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_provocateur.research_supervisor_agent import ResearchSupervisorAgent
from agent_provocateur.a2a_messaging import InMemoryMessageBroker
from agent_provocateur.a2a_models import TaskRequest, TaskStatus


async def run_goal_refiner(goal: str, options: Dict[str, Any] = None):
    """
    Run the goal refiner with the given goal.
    
    Args:
        goal: The high-level goal to refine
        options: Optional dictionary of options
    
    Returns:
        The refined goal tasks
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize supervisor agent
    broker = InMemoryMessageBroker()
    agent = ResearchSupervisorAgent("research_supervisor_agent", broker)
    
    try:
        # Start the agent
        await agent.start()
        
        # Prepare options
        if options is None:
            options = {}
        
        # Create a task request
        task_request = TaskRequest(
            task_id="cli_goal",
            source_agent="cli",
            target_agent=agent.agent_id,
            intent="process_goal",
            payload={
                "goal": goal,
                "options": options
            }
        )
        
        # Process the goal
        result = await agent.handle_process_goal(task_request)
        
        # Return the result
        return result
    
    finally:
        # Stop the agent
        await agent.stop()


def print_tasks_tree(tasks: List[Dict[str, Any]], indent: int = 0):
    """
    Print tasks in a tree format.
    
    Args:
        tasks: List of task definitions
        indent: Current indentation level
    """
    for i, task in enumerate(tasks):
        task_id = task.get("task_id", f"task{i}")
        description = task.get("description", "Unnamed task")
        agent = task.get("assigned_agent", "unknown")
        
        indent_str = "  " * indent
        print(f"{indent_str}• Task {i+1}: {description}")
        print(f"{indent_str}  Agent: {agent}")
        
        # Print capabilities
        capabilities = task.get("capabilities", [])
        if capabilities:
            print(f"{indent_str}  Capabilities: {', '.join(capabilities)}")
        
        # Print dependencies
        dependencies = task.get("dependencies", [])
        if dependencies:
            print(f"{indent_str}  Dependencies: {', '.join(dependencies)}")
        
        # Print priority
        priority = task.get("priority", "normal")
        print(f"{indent_str}  Priority: {priority}")
        
        # If there are sub-tasks, print them recursively
        sub_tasks = task.get("sub_tasks", [])
        if sub_tasks:
            print(f"{indent_str}  Sub-tasks:")
            print_tasks_tree(sub_tasks, indent + 1)
        
        # Add a blank line between tasks
        if i < len(tasks) - 1:
            print()


async def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Goal Refiner CLI")
    parser.add_argument("goal", help="High-level goal to refine")
    parser.add_argument("--doc-id", help="Document ID to include in options")
    parser.add_argument("--max-results", type=int, default=5, 
                      help="Maximum number of results for search tasks")
    parser.add_argument("--provider", default="brave", 
                      help="Search provider to use (brave, google, bing)")
    parser.add_argument("--json", action="store_true", 
                      help="Output results as JSON")
    
    args = parser.parse_args()
    
    # Build options dictionary
    options = {
        "max_results": args.max_results,
        "search_provider": args.provider,
    }
    
    if args.doc_id:
        options["doc_id"] = args.doc_id
    
    # Run the goal refiner
    result = await run_goal_refiner(args.goal, options)
    
    # Output the results
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n===== Goal Refinement Results =====")
        print(f"Goal: {args.goal}")
        print(f"Workflow ID: {result.get('workflow_id')}")
        print(f"Number of tasks: {result.get('task_count')}")
        print()
        
        # Print the tasks
        if "tasks" in result:
            print("Task breakdown:")
            print_tasks_tree(result.get("tasks", []))
        else:
            # Try to find tasks in the workflow structure
            workflow_id = result.get("workflow_id")
            workflow_tasks = result.get("results", [])
            print("Task execution results:")
            for i, task_result in enumerate(workflow_tasks):
                print(f"\n• Task {i+1}: {task_result.get('description', 'Unnamed task')}")
                print(f"  Agent: {task_result.get('agent', 'unknown')}")
                print(f"  Intent: {task_result.get('intent', 'unknown')}")
                
                # Print summary of result
                task_output = task_result.get("result", {})
                if "error" in task_output:
                    print(f"  Status: Failed - {task_output.get('error')}")
                else:
                    print(f"  Status: {task_output.get('status', 'unknown')}")
                    
                    # Print brief summary of output based on intent
                    intent = task_result.get("intent")
                    if intent == "search" and "results" in task_output:
                        result_count = len(task_output.get("results", []))
                        print(f"  Found {result_count} search results")
                    elif intent == "extract_entities" and "entities" in task_output:
                        entity_count = len(task_output.get("entities", []))
                        print(f"  Extracted {entity_count} entities")


if __name__ == "__main__":
    asyncio.run(main())