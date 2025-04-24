"""
Command-line entry point for running various Agent Provocateur components.
"""

import argparse
import os
import sys
import logging
import uvicorn
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("agent_provocateur")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Agent Provocateur CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Enhanced MCP server command
    mcp_parser = subparsers.add_parser("mcp", help="Run the enhanced MCP server")
    mcp_parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    mcp_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    mcp_parser.add_argument(
        "--entity-detector", 
        default="http://localhost:8082", 
        help="Entity Detector URL"
    )
    mcp_parser.add_argument(
        "--graphrag", 
        default="http://localhost:8084", 
        help="GraphRAG URL"
    )
    mcp_parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )

    # Parse arguments
    args = parser.parse_args()

    # Set log level
    if hasattr(args, "log_level"):
        numeric_level = getattr(logging, args.log_level)
        logger.setLevel(numeric_level)

    # Handle commands
    if args.command == "mcp":
        run_enhanced_mcp(args)
    else:
        parser.print_help()
        sys.exit(1)


def run_enhanced_mcp(args):
    """Run the enhanced MCP server."""
    from agent_provocateur.enhanced_mcp_server import create_enhanced_app

    # Set environment variables for service URLs
    os.environ["ENTITY_DETECTOR_URL"] = args.entity_detector
    os.environ["GRAPHRAG_URL"] = args.graphrag

    logger.info(f"Starting Enhanced MCP server on {args.host}:{args.port}")
    logger.info(f"- Entity Detector URL: {args.entity_detector}")
    logger.info(f"- GraphRAG URL: {args.graphrag}")

    # Create and run the app
    app = create_enhanced_app()
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()