"""Frontend server for Agent Provocateur.

This server provides a web-based user interface for Agent Provocateur.
It serves a React application that communicates with the backend API.

Run this server with:
    python frontend/server.py

Options:
    --host: Host to bind the server to (default: 127.0.0.1)
    --port: Port to bind the server to (default: 3000)
    --backend-url: URL of the backend API (default: http://localhost:8111)
    --reload: Enable auto-reload on code changes
"""

import argparse
import logging
import os
import sys
import uuid
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

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

# In-memory document store for tracking locally uploaded documents
# No longer used for simulation - only tracks real local uploads when backend is temporarily unavailable
FALLBACK_DOCUMENT_STORE = {}

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

# Mount tests directory
tests_dir = os.path.join(base_dir, "tests")
if not os.path.exists(tests_dir):
    os.makedirs(tests_dir)
app.mount("/tests", StaticFiles(directory=tests_dir), name="tests")

# Setup templates
templates = Jinja2Templates(directory=templates_dir)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backend API URL
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8111")

# Create temp uploads directory if not exists
UPLOAD_DIR = os.path.join(base_dir, "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    logger.info(f"Created uploads directory: {UPLOAD_DIR}")


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

@app.get("/agent-management", response_class=HTMLResponse)
async def agent_management(request: Request):
    """Render the agent management console page."""
    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "backend_url": BACKEND_API_URL,
            "page_script": "agent_management.js"
        }
    )

@app.get("/api-test", response_class=HTMLResponse)
async def api_test(request: Request):
    """Render the API test page."""
    return templates.TemplateResponse(
        "api_test.html", {
            "request": request,
            "backend_url": BACKEND_API_URL
        }
    )
        
@app.get("/fallback", response_class=HTMLResponse)
async def fallback(request: Request):
    """Render the fallback page."""
    return templates.TemplateResponse(
        "fallback.html", {"request": request, "backend_url": BACKEND_API_URL}
    )

@app.get("/component-test", response_class=HTMLResponse)
async def component_test(request: Request):
    """Render the component library test page."""
    return templates.TemplateResponse(
        "component-test.html", {"request": request, "backend_url": BACKEND_API_URL}
    )
    
@app.get("/new", response_class=HTMLResponse)
async def index_new(request: Request):
    """Render the new enhanced landing page."""
    return templates.TemplateResponse(
        "index-new.html", {
            "request": request, 
            "backend_url": BACKEND_API_URL,
            "page_script": "landing.js"
        }
    )
    
@app.get("/test-runner", response_class=HTMLResponse)
async def test_runner(request: Request):
    """Render the component library test runner page."""
    return templates.TemplateResponse(
        "test-runner.html", {"request": request, "backend_url": BACKEND_API_URL}
    )

@app.get("/api-test-runner", response_class=HTMLResponse)
async def api_test_runner(request: Request):
    """Render the API test runner page."""
    return templates.TemplateResponse(
        "api_test_runner.html", {"request": request, "backend_url": BACKEND_API_URL}
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "backend_url": BACKEND_API_URL}

@app.get("/api/info")
async def system_info(request: Request):
    """System information endpoint for version and port information."""
    # Retrieve version info from package
    try:
        import importlib.metadata
        version = importlib.metadata.version("agent_provocateur")
    except (importlib.metadata.PackageNotFoundError, ImportError):
        version = "0.1.0"  # Fallback version if package info isn't available
    
    # Get build number from file
    build_number = "unknown"
    build_number_path = os.path.join(base_dir, "build_number.txt")
    if os.path.exists(build_number_path):
        try:
            with open(build_number_path, "r") as f:
                build_number = f.read().strip()
        except Exception as e:
            logger.error(f"Error reading build number: {str(e)}")
    
    # Get server information
    port = request.url.port
    host = request.url.hostname
    
    # Check backend API status
    backend_status = "unknown"
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_API_URL}/api/health",
                timeout=1.0
            )
            if response.status_code == 200:
                backend_status = "available"
            else:
                backend_status = f"error: {response.status_code}"
    except Exception as e:
        backend_status = f"unavailable: {str(e)}"
    
    # Get common ports in use
    backend_port = int(BACKEND_API_URL.split(":")[-1])
    
    # Core ports that are always required
    core_ports = {
        3001: "Frontend UI",
        backend_port: "MCP Server API",
        6111: "Redis"
    }
    
    # Optional ports that may be required based on configuration
    optional_ports = {
        7111: "Ollama",
        8082: "Entity Detector MCP",
        8083: "Web Search MCP",
        8084: "GraphRAG MCP",
        3111: "Grafana",
        9111: "Prometheus",
        9091: "Pushgateway"
    }

    # Check which ports are in use
    ports_status = {}
    
    # Check core ports
    for port_num, service_name in core_ports.items():
        in_use = False
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)  # Very short timeout for quick check
            result = s.connect_ex(('127.0.0.1', port_num))
            if result == 0:
                in_use = True
            s.close()
        except (socket.error, OSError):
            in_use = True
        ports_status[port_num] = {
            "service": service_name,
            "in_use": in_use,
            "required": True
        }
    
    # Check optional ports
    for port_num, service_name in optional_ports.items():
        in_use = False
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)  # Very short timeout for quick check
            result = s.connect_ex(('127.0.0.1', port_num))
            if result == 0:
                in_use = True
            s.close()
        except (socket.error, OSError):
            in_use = True
        ports_status[port_num] = {
            "service": service_name,
            "in_use": in_use,
            "required": False  # Optional ports are not required by default
        }
        
    return {
        "version": version,
        "build_number": build_number,
        "ui_port": port,
        "ui_host": host,
        "backend_url": BACKEND_API_URL,
        "backend_status": backend_status,
        "ports": ports_status,
        "uptime": "N/A"  # Could add server uptime here in a production system
    }

@app.get("/api/debug")
async def debug_info(request: Request):
    """Debug endpoint to help diagnose issues."""
    routes = [
        {
            "path": route.path,
            "name": route.name,
            "type": route.__class__.__name__,
            "methods": [method for method in route.methods] if hasattr(route, 'methods') and route.methods else []
        }
        for route in app.routes
    ]
    
    return {
        "backend_url": BACKEND_API_URL,
        "app_routes": routes,
        "request_url": str(request.url),
        "request_headers": dict(request.headers),
        "server_host": request.client.host,
        "server_port": request.client.port,
    }

@app.get("/api/documents")
async def get_documents():
    """Proxy endpoint to get all documents from the backend API."""
    try:
        import httpx
        # Try to connect to the backend API
        logger.info(f"Fetching documents from backend API: {BACKEND_API_URL}/documents")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{BACKEND_API_URL}/documents",
                    timeout=5.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Error from backend API: {response.status_code} {response.text}")
                    return JSONResponse(
                        status_code=response.status_code,
                        content={
                            "error": f"Backend API error: {response.status_code}",
                            "message": "Unable to retrieve documents from the backend server."
                        }
                    )
                
                # Return the documents directly
                backend_docs = response.json()
                logger.info(f"Retrieved {len(backend_docs)} documents from backend API")
                return backend_docs
            
            except httpx.RequestError as request_error:
                # Connection error (backend unavailable)
                logger.error(f"Backend connection error: {str(request_error)}")
                
                # Check if we have any documents in the local store (real uploads that happened when backend was down)
                local_docs = list(FALLBACK_DOCUMENT_STORE.values())
                
                if local_docs:
                    logger.info(f"Returning {len(local_docs)} locally stored documents (backend unavailable)")
                    # Return the real local documents with a status indicator
                    return JSONResponse(
                        status_code=200,
                        content=local_docs,
                        headers={"X-Backend-Status": "unavailable", "X-Local-Documents": "true"}
                    )
                else:
                    # No documents available - backend down and no local docs
                    return JSONResponse(
                        status_code=503,
                        content={
                            "error": "Service Unavailable",
                            "message": "Backend server is currently unavailable. Please try again later."
                        }
                    )
                
    except Exception as e:
        logger.error(f"Error fetching documents: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An error occurred while retrieving documents.",
                "details": str(e)
            }
        )

# Test upload endpoint
@app.get("/test-upload-form", response_class=HTMLResponse)
async def test_upload_form(request: Request):
    """Serve the test upload form."""
    return templates.TemplateResponse("test_upload.html", {"request": request})

@app.get("/simple-upload", response_class=HTMLResponse)
async def simple_upload_form():
    """Serve the simple upload test page."""
    with open(os.path.join(base_dir, "test_simple_upload.html"), "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.post("/test-upload")
async def test_upload(request: Request):
    """Simple test endpoint for file uploads that logs and returns form data."""
    logger.info("Test upload endpoint called")
    logger.info(f"Request path: {request.url.path}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {request.headers}")
    
    try:
        form = await request.form()
        form_items = {key: (value.filename if isinstance(value, UploadFile) else value) 
                     for key, value in form.items()}
        logger.info(f"Form data received: {form_items}")
        
        # Extract fields from the form
        file_data = {}
        other_fields = {}
        
        for key, value in form.items():
            if isinstance(value, UploadFile):
                file_content = await value.read()
                file_data[key] = {
                    "filename": value.filename,
                    "content_type": value.content_type,
                    "size": len(file_content)
                }
            else:
                other_fields[key] = value
        
        return {
            "message": "Form data received",
            "request_path": str(request.url),
            "files": file_data,
            "fields": other_fields
        }
    except Exception as e:
        logger.error(f"Error in test upload: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Upload test failed: {str(e)}"}
        )

@app.post("/documents/upload")
async def upload_document(request: Request):
    """
    Handle document upload.
    
    This endpoint receives an XML file and saves it to the uploads directory.
    It then forwards the file to the backend API for processing.
    """
    logger.info("Document upload endpoint called")
    logger.info(f"Request path: {request.url.path}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Content type: {request.headers.get('content-type', 'unknown')}")
    
    try:
        # Parse the form data manually
        form = await request.form()
        logger.info(f"Form data received: {list(form.keys())}")
        
        # Log all form fields for debugging
        logger.info(f"All form fields: {list(form.keys())}")
        for key, value in form.items():
            logger.info(f"Field '{key}' type: {type(value)}, value: {value}")
        
        # Look for the title field
        title = None
        if 'title' in form:
            title = form.get('title')
        else:
            # Look for any field that might contain title information
            for key, value in form.items():
                if 'title' in key.lower() and isinstance(value, str):
                    title = value
                    break
        
        # If we still don't have a title, generate one
        if not title:
            title = f"Uploaded Document {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Look for the file field
        file = None
        if 'file' in form:
            file = form.get('file')
        else:
            # Look for any field that contains a file
            for key, value in form.items():
                if isinstance(value, UploadFile):
                    file = value
                    break
        
        # Double check the file
        if not file:
            logger.error("No file found in form data")
            return JSONResponse(
                status_code=422,
                content={"error": "No file found in the upload", "received_fields": list(form.keys())}
            )
        
        # Process the file object - we just need to get the content and filename
        try:
            # Log the file type we received
            logger.info(f"Received file object of type: {type(file)}, class: {file.__class__.__name__}")
            
            # Upload files have different interfaces depending on the web framework
            # Focus on getting the filename and content
            if hasattr(file, 'read') and callable(file.read):
                # Get content (might need to be awaited if it's an async method)
                try:
                    # Try async read first
                    file_content = await file.read()
                except (TypeError, AttributeError):
                    # Fall back to sync read
                    file_content = file.read()
                    
                # Get filename
                if hasattr(file, 'filename'):
                    filename = file.filename
                elif hasattr(file, 'name'):
                    filename = file.name
                else:
                    # Generate a filename if we can't find one
                    filename = f"uploaded_file_{uuid.uuid4().hex[:8]}.xml"
                
                # Get content type if available
                content_type = getattr(file, 'content_type', 'application/xml')
                
                # Try to seek back to the beginning if possible
                try:
                    if hasattr(file, 'seek') and callable(file.seek):
                        try:
                            await file.seek(0)
                        except (TypeError, AttributeError):
                            file.seek(0)
                except Exception as seek_error:
                    logger.warning(f"Could not seek file: {str(seek_error)}")
                
            elif isinstance(file, str) and os.path.exists(file):
                # It's a file path string, read directly
                with open(file, 'rb') as f:
                    file_content = f.read()
                filename = os.path.basename(file)
                content_type = "application/xml"
            else:
                # It's an unknown type, dump some debug info and reject
                logger.error(f"Unknown file type: {type(file)}")
                attributes = [attr for attr in dir(file) if not attr.startswith('_')]
                logger.error(f"Available attributes: {attributes}")
                return JSONResponse(
                    status_code=422,
                    content={
                        "error": "Unsupported file format", 
                        "details": f"Type: {type(file)}, available attrs: {attributes[:10]}"
                    }
                )
            
            # Log the file information
            logger.info(f"Processed file: {filename}, size: {len(file_content)} bytes, type: {content_type}")
            
        except Exception as e:
            logger.error(f"Error processing upload file: {str(e)}")
            return JSONResponse(
                status_code=422, 
                content={"error": f"Error processing upload: {str(e)}"}
            )
            
        logger.info(f"Upload received - Title: {title}, Filename: {filename}")
        
        # Check if the file is an XML file
        if not filename.lower().endswith('.xml'):
            logger.error(f"Invalid file type: {filename}")
            return JSONResponse(
                status_code=400,
                content={"error": "Only XML files are allowed"}
            )
        
        # Check if it's valid XML content
        try:
            from defusedxml import ElementTree
            root = ElementTree.fromstring(file_content)
            logger.info(f"Valid XML file detected with root element: {root.tag}")
        except Exception as xml_error:
            logger.error(f"Invalid XML content: {str(xml_error)}")
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid XML content: {str(xml_error)}"}
            )
            
        # Generate a unique ID for the document
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        logger.info(f"Generated document ID: {doc_id}")
        
        # Ensure uploads directory exists
        if not os.path.exists(UPLOAD_DIR):
            logger.info(f"Creating uploads directory: {UPLOAD_DIR}")
            os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Save the uploaded file temporarily
        file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.xml")
        logger.info(f"Saving file to: {file_path}")
        
        try:
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            logger.info(f"File saved successfully to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to save file: {str(e)}"}
            )
            
        # Get the content as text
        try:
            # Convert to string if it's bytes
            if isinstance(file_content, bytes):
                content = file_content.decode('utf-8')
            else:
                content = file_content
                
            logger.info(f"File content processed: {len(content)} characters")
        except Exception as e:
            logger.error(f"Failed to decode file content: {str(e)}")
            try:
                # Fallback - try to read the saved file
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                logger.info(f"File content read from disk successfully: {len(content)} characters")
            except Exception as read_error:
                logger.error(f"Failed to read file from disk: {str(read_error)}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Failed to process file content: {str(e)}, {str(read_error)}"}
                )
        
        # Prepare the payload for the backend API
        payload = {
            "doc_id": doc_id,
            "title": title,
            "content": content,
            "doc_type": "xml",
            "created_at": datetime.now().isoformat()
        }
        logger.info("Prepared payload for backend API")
        
        # Send the document to the backend API
        try:
            import httpx
            logger.info(f"Sending document to backend API at: {BACKEND_API_URL}/xml/upload")
            
            async with httpx.AsyncClient() as client:
                try:
                    # The backend API expects a different structure - xml_content and title
                    backend_payload = {
                        "xml_content": content,
                        "title": title
                    }
                    logger.info(f"Sending payload to backend: title={title}, content length={len(content)}")
                    
                    response = await client.post(
                        f"{BACKEND_API_URL}/xml/upload", 
                        json=backend_payload,
                        timeout=10.0
                    )
                    
                    logger.info(f"Backend API response status: {response.status_code}")
                    
                    if response.status_code != 200 and response.status_code != 201:
                        logger.error(f"Error from backend API: {response.status_code} {response.text}")
                        return JSONResponse(
                            status_code=500,
                            content={"error": f"Backend API error: {response.status_code}"}
                        )
                    
                    # Get the document ID from the response
                    try:
                        # Get response text first
                        response_text = await response.text()
                        logger.info(f"Response text: {response_text}")
                        
                        # Parse JSON from text
                        import json
                        backend_response = json.loads(response_text)
                        backend_doc_id = backend_response.get("doc_id", doc_id)
                        logger.info(f"Extracted doc_id: {backend_doc_id}")
                    except Exception as json_err:
                        logger.warning(f"Could not parse JSON response: {str(json_err)}")
                        backend_doc_id = doc_id
                    
                    # Return success response
                    logger.info(f"Document successfully uploaded to backend with ID: {backend_doc_id}")
                    return JSONResponse(
                        status_code=200,
                        content={
                            "id": backend_doc_id,
                            "title": title,
                            "success": True
                        }
                    )
                    
                except httpx.RequestError as e:
                    logger.error(f"HTTP request error: {str(e)}")
                    raise
                
        except Exception as e:
            logger.error(f"Error sending document to backend: {str(e)}")
            
            # Add more detailed error diagnostics
            try:
                import socket
                backend_host = BACKEND_API_URL.split("//")[1].split(":")[0]
                backend_port = int(BACKEND_API_URL.split(":")[-1])
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.0)
                conn_result = s.connect_ex((backend_host, backend_port))
                if conn_result != 0:
                    logger.error(f"Backend server at {backend_host}:{backend_port} is not reachable")
                    error_detail = f"Backend server not reachable at {backend_host}:{backend_port}"
                else:
                    logger.info(f"Backend server at {backend_host}:{backend_port} is reachable, but API call failed")
                    error_detail = f"Backend reachable but API call failed: {str(e)}"
                s.close()
            except Exception as socket_error:
                logger.error(f"Error checking backend connectivity: {str(socket_error)}")
                error_detail = f"Unknown backend error: {str(e)}"
                
            # Store the error message for later use
            error_detail_str = str(e)
            
            # Check if it's an XML parsing error
            if "no such file" in error_detail_str.lower() or "xml" in error_detail_str.lower():
                # XML parsing error
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Invalid XML content",
                        "details": error_detail_str,
                        "debug_info": error_detail
                    }
                )
            else:
                # Backend connectivity issue
                logger.error(f"Backend server unavailable: {error_detail}")
                
                # Since we already saved the file and verified it's valid XML,
                # we can store it locally for reference, but inform the user that
                # the backend is unavailable
                
                # Keep track of this document for potential later synchronization
                FALLBACK_DOCUMENT_STORE[doc_id] = {
                    "doc_id": doc_id,
                    "title": title,
                    "doc_type": "xml",
                    "created_at": datetime.now().isoformat(),
                    "local_only": True,  # Mark as local only
                    "pending_sync": True,  # Needs to be synced to backend when available
                    "local_path": file_path  # Store the path for future reference
                }
                
                # Return error response with information about local storage
                return JSONResponse(
                    status_code=503,  # Service Unavailable
                    content={
                        "error": "Backend Unavailable",
                        "message": "The backend processing server is currently unavailable. Your document has been saved locally but cannot be processed until the backend is available.",
                        "local_doc_id": doc_id,
                        "local_only": True
                    }
                )
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}", exc_info=True)
        # Return a more descriptive error
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Upload failed: {str(e)}",
                "details": "An error occurred while processing the upload. Please check the file format and try again."
            }
        )

@app.get("/static/js/{script_name}")
async def get_js(script_name: str):
    """Serve JavaScript files directly."""
    js_path = os.path.join(base_dir, "static", "js", script_name)
    
    logger.info(f"Serving JS file: {js_path}")
    
    if not os.path.exists(js_path):
        logger.error(f"JS file not found: {js_path}")
        return JSONResponse(
            status_code=404,
            content={"error": "File not found"}
        )
    
    return FileResponse(js_path, media_type='application/javascript')
    
@app.get("/tests/{script_name}")
async def get_test_script(script_name: str):
    """Serve test scripts directly."""
    script_path = os.path.join(base_dir, "tests", script_name)
    
    logger.info(f"Serving test script: {script_path}")
    
    if not os.path.exists(script_path):
        logger.error(f"Test script not found: {script_path}")
        return JSONResponse(
            status_code=404,
            content={"error": "File not found"}
        )
    
    return FileResponse(script_path, media_type='application/javascript')


def main() -> int:
    """Entry point for the frontend server."""
    parser = argparse.ArgumentParser(description="Agent Provocateur UI Server")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=3001, help="Port to bind the server to (default: 3001, changed from 3000 to avoid Grafana conflicts)"
    )
    parser.add_argument(
        "--backend-url", default="http://localhost:8111", help="Backend API URL"
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