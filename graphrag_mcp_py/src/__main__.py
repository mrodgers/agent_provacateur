"""
Main entry point for GraphRAG MCP Server.
"""

import os
import sys
import uvicorn

from .config import config
from .utils import logger


def main():
    """Run the GraphRAG MCP Server."""
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    
    logger.info(f"Starting GraphRAG MCP Server on {config.HOST}:{config.PORT}")
    logger.info(f"Configuration: {config.__dict__}")
    
    # Run the FastAPI app
    uvicorn.run(
        "graphrag_mcp_py.src.api:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
        log_level=config.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()