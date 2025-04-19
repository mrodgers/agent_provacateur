import argparse
import json
import sys
from typing import Any, Dict, List

from agent_provocateur.mcp_client import SyncMcpClient


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
Assignee: {ticket.get('assignee', 'Unassigned')}
"""


def format_document(doc: Dict[str, Any]) -> str:
    """Format a document for display.
    
    Args:
        doc: The document data
        
    Returns:
        str: Formatted document string
    """
    return f"""
Document ID: {doc['doc_id']}
Content:
{doc['markdown']}
"""


def format_pdf(pdf: Dict[str, Any]) -> str:
    """Format a PDF document for display.
    
    Args:
        pdf: The PDF data
        
    Returns:
        str: Formatted PDF string
    """
    pages_text = "\n".join(
        [f"Page {page['page_number']}: {page['text']}" for page in pdf["pages"]]
    )
    return f"""
PDF URL: {pdf['url']}
Content:
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
    
    formatted = ["Search Results:"]
    for i, result in enumerate(results, 1):
        formatted.append(f"\n{i}. {result['title']}")
        formatted.append(f"   {result['snippet']}")
        formatted.append(f"   URL: {result['url']}")
    
    return "\n".join(formatted)


def main() -> int:
    """CLI entry point.
    
    Returns:
        int: Exit code
    """
    parser = argparse.ArgumentParser(description="Agent Provocateur CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # JIRA ticket command
    jira_parser = subparsers.add_parser("ticket", help="Fetch a JIRA ticket")
    jira_parser.add_argument("ticket_id", help="Ticket ID")
    
    # Document command
    doc_parser = subparsers.add_parser("doc", help="Fetch a document")
    doc_parser.add_argument("doc_id", help="Document ID")
    
    # PDF command
    pdf_parser = subparsers.add_parser("pdf", help="Fetch a PDF document")
    pdf_parser.add_argument("pdf_id", help="PDF ID")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search the web")
    search_parser.add_argument("query", help="Search query")
    
    # Config command
    config_parser = subparsers.add_parser(
        "config", help="Update server configuration"
    )
    config_parser.add_argument(
        "--min-latency", type=int, help="Minimum latency in milliseconds"
    )
    config_parser.add_argument(
        "--max-latency", type=int, help="Maximum latency in milliseconds"
    )
    config_parser.add_argument(
        "--error-rate",
        type=float,
        help="Rate of simulated errors (0.0 to 1.0)",
    )
    
    # Format option
    parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )
    parser.add_argument(
        "--server", default="http://localhost:8000", help="MCP server URL"
    )
    
    args = parser.parse_args()
    
    # Handle no command
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        with SyncMcpClient(args.server) as client:
            result: Any = None
            
            if args.command == "ticket":
                result = client.fetch_ticket(args.ticket_id).dict()
                if not args.json:
                    print(format_jira_ticket(result))
            
            elif args.command == "doc":
                result = client.get_doc(args.doc_id).dict()
                if not args.json:
                    print(format_document(result))
            
            elif args.command == "pdf":
                result = client.get_pdf(args.pdf_id).dict()
                if not args.json:
                    print(format_pdf(result))
            
            elif args.command == "search":
                search_results = [r.dict() for r in client.search_web(args.query)]
                result = search_results
                if not args.json:
                    print(format_search_results(search_results))
            
            elif args.command == "config":
                result = client.update_server_config(
                    args.min_latency, args.max_latency, args.error_rate
                )
                if not args.json:
                    print(f"Server configuration updated: {result}")
            
            # Print JSON if requested
            if args.json and result is not None:
                print(json.dumps(result, indent=2))
            
            return 0
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())