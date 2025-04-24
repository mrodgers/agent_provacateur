# Enhanced Document Service API

This directory contains the implementation of the Enhanced Document Service API with improved API documentation and service integrations.

## Overview

The Document Service API (formerly known as MCP Server) extends the basic document service with:

1. Comprehensive API documentation
2. Proxy endpoints for Entity Detector and GraphRAG services
3. End-to-end workflow orchestration
4. Service health checking and status reporting
5. Automatic service discovery

## Key Components

- **enhanced_mcp_server.py** - Enhanced Document Service API implementation (to be renamed)
- **improved_docs.py** - API documentation models and metadata
- **document_service_api.py** - Base Document Service API implementation (renamed from mcp_server.py)
- **__main__.py** - Entry point for running the server as a module

## How to Run

### Using the Startup Script

The simplest way to run the Enhanced MCP Server is using the provided startup script:

```bash
./scripts/run_enhanced_mcp_server.sh
```

This script will:
1. Automatically detect services (Entity Detector and GraphRAG)
2. Find an available port if the default port is in use
3. Set up proper environment variables
4. Start the server with appropriate logging

You can customize the startup with options:

```bash
./scripts/run_enhanced_mcp_server.sh --port 8001 --entity-port 9585 --graphrag-port 9584 --host 0.0.0.0
```

### Using Python Module with UV

You can also run the server directly as a Python module with UV:

```bash
# From the project root directory
uv run -m agent_provocateur docservice --port 8001
```

Or using the Python API:

```python
from agent_provocateur.enhanced_mcp_server import create_enhanced_app
import uvicorn

app = create_enhanced_app()
uvicorn.run(app, host="127.0.0.1", port=8000)
```

Note: The module names will be updated in a future release to align with the new naming convention.

## API Documentation

The enhanced server provides comprehensive API documentation through FastAPI's OpenAPI integration.

Access the interactive documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Key Endpoints

### System Information
- `GET /api/info` - Comprehensive system status

### Document Management
- `POST /xml/upload` - Upload XML document
- `GET /documents/{doc_id}` - Get document by ID
- `GET /documents/{doc_id}/xml/nodes` - Get researchable nodes

### Proxy Services
- `POST /proxy/entity-extraction` - Entity extraction via Entity Detector
- `POST /proxy/graphrag-query` - Research via GraphRAG

### End-to-End Workflow
- `POST /workflow/process-document` - Process a document through the complete system

## Architecture

The Document Service API uses a layered architecture:

1. **Base Layer** - Core document service functionality (document_service_api.py)
2. **Documentation Layer** - API documentation models (improved_docs.py) 
3. **Enhancement Layer** - Extended functionality (enhanced_mcp_server.py - to be renamed)
4. **Integration Layer** - Service communication with Entity Detector and GraphRAG service

## Service Integration

The server integrates with:

- **Entity Detector MCP** (default port 8082/9585) - For entity extraction
- **GraphRAG MCP** (default port 8084/9584) - For knowledge graph research
- **Redis** (port 6379) - For caching and messaging

## Configuration

The server can be configured through:

1. **Command-line arguments** - For host, port, service URLs
2. **Environment variables** - ENTITY_DETECTOR_URL, GRAPHRAG_URL