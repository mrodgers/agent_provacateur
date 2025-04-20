"""CLI interface for agent-provocateur."""

import argparse
import json
import sys
import platform
import time
from typing import Any, Dict, List

from agent_provocateur.mcp_client import McpClient
import asyncio

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