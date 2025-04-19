import uvicorn
from argparse import ArgumentParser



def main() -> bool:
    """Main entry point for the application.
    
    Returns:
        bool: True if execution was successful
    """
    parser = ArgumentParser(description="Agent Provocateur MCP Server")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the server to"
    )
    
    args = parser.parse_args()
    
    print(f"Starting MCP server on {args.host}:{args.port}")
    uvicorn.run(
        "agent_provocateur.mcp_server:create_app",
        host=args.host,
        port=args.port,
        factory=True,
    )
    return True


if __name__ == "__main__":
    main()
