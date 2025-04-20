"""CLI interface for agent-provocateur."""

import argparse
import json
import sys
import platform
import time
import os
from typing import Any, Dict, List
from pathlib import Path

from agent_provocateur.mcp_client import McpClient
import asyncio

from agent_provocateur.a2a_messaging import InMemoryMessageBroker
from agent_provocateur.a2a_models import TaskRequest, TaskStatus, TaskResult
from agent_provocateur.agent_implementations import (
    DocAgent, 
    SearchAgent, 
    JiraAgent, 
    SynthesisAgent, 
    DecisionAgent
)
from agent_provocateur.xml_agent import XmlAgent
from agent_provocateur.research_supervisor_agent import ResearchSupervisorAgent

# Import optional Prometheus metrics if available
try:
    from prometheus_client import Counter, Gauge, Histogram, push_to_gateway, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


def format_jira_ticket(ticket: Dict[str, Any]) -> str:
    """Format a JIRA ticket for display.
    
    Args:
        ticket: The ticket data
        
    Returns:
        str: Formatted ticket string
    """
    return f"""
Ticket: {ticket['id']}
Summary: {ticket['summary']}
Status: {ticket['status']}
Assignee: {ticket.get('assignee') or 'Unassigned'}
"""


def format_document(doc: Dict[str, Any]) -> str:
    """Format a document for display.
    
    Args:
        doc: The document data
        
    Returns:
        str: Formatted document string
    """
    return f"""
Document: {doc['doc_id']}
Title: {doc.get('title', 'Untitled')}
Type: {doc.get('doc_type', 'text')}

Content:
{doc.get('markdown', '')}
"""


def format_pdf(pdf: Dict[str, Any]) -> str:
    """Format a PDF document for display.
    
    Args:
        pdf: The PDF data
        
    Returns:
        str: Formatted PDF string
    """
    pages_text = "\n\n".join(
        f"--- Page {page['page_number']} ---\n{page['text']}" for page in pdf["pages"]
    )
    
    return f"""
PDF: {pdf['url']}
Pages: {len(pdf['pages'])}

{pages_text}
"""


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """Format search results for display.
    
    Args:
        results: The search results
        
    Returns:
        str: Formatted search results string
    """
    if not results:
        return "No results found."
    
    formatted_results = "\n\n".join(
        f"{i+1}. {result['title']}\n   {result['url']}\n   {result['snippet']}"
        for i, result in enumerate(results)
    )
    
    return f"""
Search Results ({len(results)} found):

{formatted_results}
"""


def format_research_results(research_result: Dict[str, Any]) -> str:
    """Format research results for display.
    
    Args:
        research_result: The research results
        
    Returns:
        str: Formatted research results string
    """
    doc_id = research_result.get("doc_id", "unknown")
    entity_count = research_result.get("entity_count", 0)
    research_count = research_result.get("research_count", 0)
    summary = research_result.get("summary", "No summary available")
    workflow_id = research_result.get("workflow_id", "unknown")
    
    # Format entities
    entity_details = ""
    if "research_results" in research_result:
        for i, entity in enumerate(research_result["research_results"][:5], 1):  # Show top 5
            entity_name = entity.get("entity", "Unknown")
            definition = entity.get("definition", "No definition available")
            confidence = entity.get("confidence", 0.0)
            
            # Truncate definition if too long
            if len(definition) > 150:
                definition = definition[:147] + "..."
                
            entity_details += f"  {i}. {entity_name} (Confidence: {confidence:.2f})\n"
            entity_details += f"     {definition}\n\n"
    
    result = f"""
Research Results for Document: {doc_id}
Workflow ID: {workflow_id}

Summary: {summary}

Entities Found: {entity_count}
Entities Researched: {research_count}

Top Entities:
{entity_details}
"""
    
    # Add XML output info
    if "enriched_xml" in research_result:
        validation = research_result.get("validation", {})
        valid = validation.get("valid", False)
        errors = validation.get("errors", [])
        
        result += f"\nEnriched XML Output:\n"
        result += f"  Validation: {'VALID' if valid else 'INVALID'}\n"
        
        if errors:
            result += f"  Errors: {len(errors)}\n"
            for error in errors[:3]:  # Show top 3 errors
                result += f"    - {error}\n"
    
    return result


def run_metrics_test(args: argparse.Namespace) -> None:
    """Run the metrics test command."""
    if not PROMETHEUS_AVAILABLE:
        print("Error: Prometheus client library not installed.")
        print("Install with: pip install prometheus-client")
        return
    
    # Create a registry for our metrics
    registry = CollectorRegistry()
    
    # Create test metrics
    test_counter = Counter(
        'ap_test_counter_total', 
        'Test counter for verification', 
        registry=registry
    )
    
    test_gauge = Gauge(
        'ap_test_gauge',
        'Test gauge for verification',
        ['instance', 'system'],
        registry=registry
    )
    
    test_histogram = Histogram(
        'ap_test_duration_seconds',
        'Test histogram for verification',
        ['operation'],
        registry=registry
    )
    
    # Process iterations
    print(f"Starting Prometheus metrics test with Pushgateway at {args.pushgateway}")
    print(f"Running {args.iterations} iterations with {args.delay}s delay between each")
    
    # Run multiple iterations
    for i in range(args.iterations):
        print(f"\nIteration {i+1}/{args.iterations}")
        
        # Increment counter
        test_counter.inc()
        print(f"Counter incremented to {test_counter._value.get()}")
        
        # Set gauge to random value
        import random
        gauge_value = random.uniform(0, 100)
        test_gauge.labels(
            instance=platform.node(),
            system=platform.system()
        ).set(gauge_value)
        print(f"Gauge set to {gauge_value:.2f}")
        
        # Record histogram observation
        duration = random.uniform(0.1, 2.0)
        test_histogram.labels(operation="test").observe(duration)
        print(f"Histogram recorded duration: {duration:.4f}s")
        
        # Push metrics to Pushgateway
        try:
            push_to_gateway(
                args.pushgateway, 
                job='ap_test_metrics',
                registry=registry
            )
            print(f"Successfully pushed metrics to Pushgateway at {args.pushgateway}")
        except Exception as e:
            print(f"Error pushing to Pushgateway: {e}")
        
        # Wait before next iteration
        if i < args.iterations - 1:
            print(f"Waiting {args.delay}s before next iteration...")
            time.sleep(args.delay)
    
    print("\nTest completed!")
    print("\nVerify metrics in Prometheus/Grafana:")
    print("1. Prometheus UI: http://localhost:9090")
    print("   - Search for metrics: ap_test_counter_total, ap_test_gauge, ap_test_duration_seconds")
    print("2. Grafana: http://localhost:3000/d/dejfjfc93klc0a/agent-provocateur-test-dashboard")
    print("   - Login with admin/agent_provocateur")


async def run_command(args: argparse.Namespace) -> None:
    """Run the selected command."""
    # Handle metrics command (synchronous)
    if args.command == "metrics":
        run_metrics_test(args)
        return
    
    client = McpClient(args.server)
    
    result: Any = None
    
    if args.command == "ticket":
        result = (await client.fetch_ticket(args.ticket_id)).dict()
        if not args.json:
            print(format_jira_ticket(result))
    
    elif args.command == "doc":
        result = (await client.get_doc(args.doc_id)).dict()
        if not args.json:
            print(format_document(result))
    
    elif args.command == "pdf":
        result = (await client.get_pdf(args.pdf_id)).dict()
        if not args.json:
            print(format_pdf(result))
    
    elif args.command == "search":
        search_results = await client.search_web(args.query)
        result = search_results
        if not args.json:
            print(format_search_results(result))
    
    elif args.command == "list-documents":
        documents = await client.list_documents(doc_type=args.type)
        result = [doc.dict() for doc in documents]
        if not args.json:
            print(f"\nFound {len(documents)} documents:")
            for doc in documents:
                print(f"  - {doc.doc_id} ({doc.doc_type}): {doc.title}")
                
    elif args.command == "research":
        # Handle research command with all agent setup
        try:
            # Create broker and agents
            broker = InMemoryMessageBroker()
            
            print(f"Setting up agents for research...")
            # Create all required agents
            supervisor = ResearchSupervisorAgent("research_supervisor", broker, args.server)
            xml_agent = XmlAgent("xml_agent", broker, args.server)
            doc_agent = DocAgent("doc_agent", broker, args.server)
            decision_agent = DecisionAgent("decision_agent", broker, args.server)
            synthesis_agent = SynthesisAgent("synthesis_agent", broker, args.server)
            
            # Create secondary agents if needed
            agents = [supervisor, xml_agent, doc_agent, decision_agent, synthesis_agent]
            
            if args.with_search:
                search_agent = SearchAgent("search_agent", broker, args.server)
                agents.append(search_agent)
                
            if args.with_jira:
                jira_agent = JiraAgent("jira_agent", broker, args.server)
                agents.append(jira_agent)
            
            # Start all agents
            for agent in agents:
                await agent.start()
            
            try:
                # Research options
                options = {
                    "format": args.format,
                    "max_entities": args.max_entities,
                    "min_confidence": args.min_confidence
                }
                
                # Execute research
                print(f"Starting research for document: {args.doc_id}")
                start_time = time.time()
                
                # Create task request
                task_request = TaskRequest(
                    task_id=f"cli_research_{int(time.time())}",
                    source_agent="cli",
                    target_agent="research_supervisor",
                    intent="research_document",
                    payload={
                        "doc_id": args.doc_id,
                        "options": options
                    }
                )
                
                research_result = await supervisor.handle_research_document(task_request)
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"Research completed in {duration:.2f} seconds")
                
                # Process results
                if args.format == "xml" and "enriched_xml" in research_result:
                    # Save enriched XML to file
                    output_file = args.output or f"{args.doc_id}_enriched.xml"
                    with open(output_file, "w") as f:
                        f.write(research_result.get("enriched_xml", ""))
                    print(f"Enriched XML saved to: {output_file}")
                
                # Display formatted results or JSON
                if args.json:
                    result = research_result
                else:
                    print(format_research_results(research_result))
                    
            finally:
                # Stop all agents
                print("Shutting down agents...")
                for agent in agents:
                    await agent.stop()
                    
        except Exception as e:
            print(f"Error in research workflow: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # Print JSON if requested
    if args.json and result is not None:
        print(json.dumps(result, indent=2))


def main() -> int:
    """Entry point for the CLI.
    
    Returns:
        int: Exit code
    """
    parser = argparse.ArgumentParser(description="Agent Provocateur CLI")
    parser.add_argument(
        "--server", default="http://localhost:8000", help="URL of the MCP server"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Fetch JIRA ticket
    ticket_parser = subparsers.add_parser("ticket", help="Fetch a JIRA ticket")
    ticket_parser.add_argument("ticket_id", help="ID of the ticket to fetch")
    
    # Get document
    doc_parser = subparsers.add_parser("doc", help="Get a document")
    doc_parser.add_argument("doc_id", help="ID of the document to get")
    
    # Get PDF
    pdf_parser = subparsers.add_parser("pdf", help="Get a PDF document")
    pdf_parser.add_argument("pdf_id", help="ID of the PDF to get")
    
    # Search web
    search_parser = subparsers.add_parser("search", help="Search the web")
    search_parser.add_argument("query", help="Search query")
    
    # List documents
    list_docs_parser = subparsers.add_parser("list-documents", help="List available documents")
    list_docs_parser.add_argument("--type", help="Filter by document type")
    
    # Research documents
    research_parser = subparsers.add_parser("research", help="Research entities in a document")
    research_parser.add_argument("doc_id", help="Document ID to research")
    research_parser.add_argument("--format", choices=["text", "xml"], default="text", help="Output format")
    research_parser.add_argument("--output", help="Output file for XML results")
    research_parser.add_argument("--max-entities", type=int, default=10, help="Maximum entities to research")
    research_parser.add_argument("--min-confidence", type=float, default=0.5, help="Minimum confidence threshold")
    research_parser.add_argument("--with-search", action="store_true", help="Include search agent for research")
    research_parser.add_argument("--with-jira", action="store_true", help="Include JIRA agent for research")
    
    # Configure server
    config_parser = subparsers.add_parser(
        "config", help="Configure server latency and error rate"
    )
    config_parser.add_argument(
        "--min-latency", type=int, default=0, help="Minimum latency in ms"
    )
    config_parser.add_argument(
        "--max-latency", type=int, default=500, help="Maximum latency in ms"
    )
    config_parser.add_argument(
        "--error-rate", type=float, default=0.0, help="Error rate (0.0-1.0)"
    )
    
    # Metrics command
    if PROMETHEUS_AVAILABLE:
        metrics_parser = subparsers.add_parser(
            "metrics", help="Test Prometheus metrics with Pushgateway"
        )
        metrics_parser.add_argument(
            "--pushgateway", default="localhost:9091", help="Pushgateway URL (default: localhost:9091)"
        )
        metrics_parser.add_argument(
            "--iterations", type=int, default=5, help="Number of iterations to run (default: 5)"
        )
        metrics_parser.add_argument(
            "--delay", type=float, default=1.0, help="Delay between iterations in seconds (default: 1.0)"
        )
    
    args = parser.parse_args()
    
    # Handle no command
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Run the command asynchronously
        asyncio.run(run_command(args))
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())