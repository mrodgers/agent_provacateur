import asyncio
import logging
import sys
import time
import httpx
from argparse import ArgumentParser
from typing import Dict, Optional

from agent_provocateur.a2a_messaging import InMemoryMessageBroker
from agent_provocateur.a2a_models import TaskStatus
from agent_provocateur.agent_implementations import (
    DocAgent,
    JiraAgent,
    ManagerAgent,
    PdfAgent,
    SearchAgent,
    SynthesisAgent,
)


async def check_server_health(url: str) -> bool:
    """Check if the MCP server is healthy.
    
    Args:
        url: The server URL
        
    Returns:
        bool: True if the server is healthy
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{url}/config", timeout=2.0)
            if response.status_code != 200:
                return False
            
            # Try a simple JIRA ticket request to ensure full functionality
            response = await client.get(f"{url}/jira/ticket/AP-1", timeout=2.0)
            return response.status_code == 200
    except Exception:
        return False

async def run_workflow(
    query: str,
    ticket_id: Optional[str] = None,
    doc_id: Optional[str] = None,
    mcp_url: str = "http://localhost:8000",
) -> Dict:
    """Run the sample agent workflow.
    
    Args:
        query: The research query
        ticket_id: Optional JIRA ticket ID
        doc_id: Optional document ID
        mcp_url: URL of the MCP server
        
    Returns:
        Dict: The research report
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )
    
    # Check if MCP server is running and healthy
    if not await check_server_health(mcp_url):
        return {
            "error": f"MCP server at {mcp_url} is not running or not responding",
            "sections": [
                {
                    "title": "Server Error",
                    "content": f"Please start the MCP server with: ./scripts/ap.sh server"
                }
            ],
            "summary": "Cannot connect to MCP server"
        }
    
    # Create shared message broker
    broker = InMemoryMessageBroker()
    
    # Create agents
    jira_agent = JiraAgent("jira_agent", broker, mcp_url)
    doc_agent = DocAgent("doc_agent", broker, mcp_url)
    pdf_agent = PdfAgent("pdf_agent", broker, mcp_url)
    search_agent = SearchAgent("search_agent", broker, mcp_url)
    synthesis_agent = SynthesisAgent("synthesis_agent", broker, mcp_url)
    manager_agent = ManagerAgent("manager_agent", broker, mcp_url)
    
    # Start all agents
    agents = [
        jira_agent,
        doc_agent,
        pdf_agent,
        search_agent,
        synthesis_agent,
        manager_agent,
    ]
    
    for agent in agents:
        await agent.start()
    
    try:
        # Build payload
        payload = {"query": query}
        if ticket_id:
            payload["ticket_id"] = ticket_id
        if doc_id:
            payload["doc_id"] = doc_id
        
        # Start workflow with manager agent
        start_time = time.time()
        print(f"Starting workflow with query: {query}")
        
        # Send the request
        result = manager_agent.messaging.send_task_request(
            target_agent="manager_agent",
            intent="research_query",
            payload=payload,
        )
        
        # Wait for result with timeout
        print(f"DEBUG: Waiting for result of task: {result}")
        task_result = await manager_agent.messaging.wait_for_task_result(
            task_id=result,
            timeout_sec=60,  # Long enough to complete the task
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if task_result and task_result.status == TaskStatus.COMPLETED:
            print(f"Workflow completed in {duration:.2f} seconds")
            return task_result.output
        else:
            print(f"Workflow timed out or failed after {duration:.2f} seconds")
            return {
                "error": "Workflow timed out or failed",
                "sections": [
                    {
                        "title": "Workflow Error",
                        "content": "The workflow didn't complete in the expected time."
                    }
                ],
                "summary": "Workflow execution failed"
            }
    
    except Exception as e:
        print(f"Error running workflow: {e}")
        return {
            "error": f"Error running workflow: {str(e)}",
            "sections": [{"title": "Error", "content": f"An error occurred: {str(e)}"}],
            "summary": "Workflow execution error"
        }
    
    finally:
        # Stop all agents
        for agent in agents:
            await agent.stop()


def format_report(report: Dict) -> str:
    """Format a research report for display.
    
    Args:
        report: The research report
        
    Returns:
        str: Formatted report string
    """
    if "error" in report:
        return f"Error: {report['error']}"
    
    sections = report.get("sections", [])
    summary = report.get("summary", "No summary available.")
    
    result = ["# Research Report\n"]
    result.append(f"Summary: {summary}\n")
    
    for i, section in enumerate(sections, 1):
        result.append(f"## {section['title']}")
        result.append(f"{section['content']}\n")
    
    return "\n".join(result)


async def main_async() -> int:
    """Async entry point for the sample workflow.
    
    Returns:
        int: Exit code
    """
    parser = ArgumentParser(description="Agent Provocateur Sample Workflow")
    parser.add_argument("query", help="Research query")
    parser.add_argument("--ticket", help="JIRA ticket ID")
    parser.add_argument("--doc", help="Document ID")
    parser.add_argument(
        "--server", default="http://localhost:8000", help="MCP server URL"
    )
    
    args = parser.parse_args()
    
    # We don't need to check server here as run_workflow now does it
    report = await run_workflow(
        query=args.query,
        ticket_id=args.ticket,
        doc_id=args.doc,
        mcp_url=args.server,
    )
    
    print(format_report(report))
    return 0


def main() -> int:
    """CLI entry point for the sample workflow.
    
    Returns:
        int: Exit code
    """
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())