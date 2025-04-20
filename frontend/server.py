"""Frontend server for Agent Provocateur.

This server provides a web-based user interface for Agent Provocateur.
It serves a React application that communicates with the backend API.

Run this server with:
    python frontend/server.py

Options:
    --host: Host to bind the server to (default: 127.0.0.1)
    --port: Port to bind the server to (default: 3000)
    --backend-url: URL of the backend API (default: http://localhost:8000)
    --reload: Enable auto-reload on code changes
"""

import argparse
import logging
import os
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Agent Provocateur UI")

# Get the directory of this file
base_dir = os.path.dirname(os.path.abspath(__file__))

# Mount static files directory
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backend API URL
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the index page."""
    return templates.TemplateResponse(
        "index.html", {"request": request, "backend_url": BACKEND_API_URL}
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "backend_url": BACKEND_API_URL}


def main() -> int:
    """Entry point for the frontend server."""
    parser = argparse.ArgumentParser(description="Agent Provocateur UI Server")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=3000, help="Port to bind the server to"
    )
    parser.add_argument(
        "--backend-url", default="http://localhost:8000", help="Backend API URL"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Auto-reload on code changes"
    )

    args = parser.parse_args()

    # Set backend URL from args or environment
    global BACKEND_API_URL
    BACKEND_API_URL = args.backend_url
    os.environ["BACKEND_API_URL"] = BACKEND_API_URL

    logger.info(f"Starting frontend server on {args.host}:{args.port}")
    logger.info(f"Backend API URL: {BACKEND_API_URL}")

    # Start the server
    uvicorn.run(
        "server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
    return 0


if __name__ == "__main__":
    exit(main())