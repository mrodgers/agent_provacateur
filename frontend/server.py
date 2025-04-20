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
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Agent Provocateur UI")

# Get the directory of this file
base_dir = os.path.dirname(os.path.abspath(__file__))
logger.info(f"Base directory: {base_dir}")

# Make sure the static directory exists
static_dir = os.path.join(base_dir, "static")
if not os.path.exists(static_dir):
    logger.error(f"Static directory does not exist: {static_dir}")
    sys.exit(1)

# Make sure the templates directory exists
templates_dir = os.path.join(base_dir, "templates")
if not os.path.exists(templates_dir):
    logger.error(f"Templates directory does not exist: {templates_dir}")
    sys.exit(1)

# Log file paths to help with debugging
js_dir = os.path.join(static_dir, "js")
if os.path.exists(js_dir):
    logger.info(f"JS directory found: {js_dir}")
    for file in os.listdir(js_dir):
        logger.info(f"  - {file}")
else:
    logger.error(f"JS directory does not exist: {js_dir}")

# Mount static files directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Setup templates
templates = Jinja2Templates(directory=templates_dir)

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
async def index(request: Request, use_fallback: bool = False):
    """Render the landing page."""
    if use_fallback:
        return templates.TemplateResponse(
            "fallback.html", {"request": request, "backend_url": BACKEND_API_URL}
        )
    else:
        # Modify index.html to use landing.js
        response = templates.TemplateResponse(
            "index.html", {"request": request, "backend_url": BACKEND_API_URL, "page_script": "landing.js"}
        )
        return response

@app.get("/document-viewer", response_class=HTMLResponse)
async def document_viewer(request: Request):
    """Render the document viewer page."""
    # Get document ID from query parameters
    doc_id = request.query_params.get("doc", "")
    
    # Pass the document ID to the template
    return templates.TemplateResponse(
        "index.html", {
            "request": request, 
            "backend_url": BACKEND_API_URL,
            "page_script": "document_viewer.js",
            "doc_id": doc_id
        }
    )
        
@app.get("/fallback", response_class=HTMLResponse)
async def fallback(request: Request):
    """Render the fallback page."""
    return templates.TemplateResponse(
        "fallback.html", {"request": request, "backend_url": BACKEND_API_URL}
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "backend_url": BACKEND_API_URL}

@app.get("/static/js/{script_name}")
async def get_js(script_name: str):
    """Serve JavaScript files directly."""
    js_path = os.path.join(base_dir, "static", "js", script_name)
    logger.info(f"Serving JS file: {js_path}")
    
    if not os.path.exists(js_path):
        logger.error(f"JS file not found: {js_path}")
        return {"error": "File not found"}, 404
    
    return FileResponse(js_path, media_type="application/javascript")


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