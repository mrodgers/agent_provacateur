import asyncio
import logging
import sys
import time
import httpx
from argparse import ArgumentParser
from typing import Dict, Optional

from agent_provocateur.a2a_messaging import InMemoryMessageBroker
from agent_provocateur.agent_implementations import (
    DocAgent,
    JiraAgent,
    ManagerAgent,
    PdfAgent,
    SearchAgent,
    SynthesisAgent,
)


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
        
        result = manager_agent.messaging.send_task_request(
            target_agent="manager_agent",
            intent="research_query",
            payload=payload,
        )
        
        # Wait for result
        task_result = await manager_agent.messaging.wait_for_task_result(
            task_id=result,
            timeout_sec=30,
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if task_result:
            print(f"Workflow completed in {duration:.2f} seconds")
            return task_result.output
        else:
            print(f"Workflow timed out after {duration:.2f} seconds")
            return {"error": "Workflow timed out"}
    
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


async def check_server(url: str) -> bool:
    """Check if the MCP server is running.
    
    Args:
        url: The server URL to check
        
    Returns:
        bool: True if server is running, False otherwise
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{url}/config", timeout=2.0)
            return response.status_code == 200
    except (httpx.ConnectError, httpx.ConnectTimeout):
        return False

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
    
    # Check if server is running
    if not await check_server(args.server):
        print(f"ERROR: MCP server not running at {args.server}")
        print("Please start the server with: ./scripts/ap.sh server")
        return 1
    
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