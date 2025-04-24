"""
Enhanced MCP Server with improved API documentation.

This module extends the basic MCP server with comprehensive documentation
and proper integration with Entity Detector and GraphRAG services.
"""

import asyncio
import datetime
import logging
import os
import json
import socket
from typing import Dict, List, Optional, Any, Union

import httpx
from fastapi import FastAPI, HTTPException, Query, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent_provocateur.mcp_server import McpServer, ServerConfig
from agent_provocateur.improved_docs import (
    ApiInfo,
    XmlUploadRequest,
    XmlDocumentModel,
    SystemInfo,
    ServiceInfo,
    Entity,
    EntityExtractionRequest,
    EntityExtractionResponse,
    GraphQueryRequest,
    GraphQueryResponse,
    xml_upload_example,
    entity_extraction_example,
    graphrag_query_example,
    system_info_example,
)


class EnhancedMcpServer(McpServer):
    """Enhanced MCP server with improved documentation and service integration."""
    
    def __init__(self) -> None:
        """Initialize the enhanced MCP server."""
        # Initialize the base server first
        super().__init__()
        
        # Override app settings with improved documentation
        self.app.title = ApiInfo.title
        self.app.description = ApiInfo.description
        self.app.version = ApiInfo.version
        
        # Set contact and license info
        self.app.openapi_tags = ApiInfo.tags
        
        # Configuration for external services
        self.entity_detector_url = os.environ.get("ENTITY_DETECTOR_URL", "http://localhost:8082")
        self.graphrag_url = os.environ.get("GRAPHRAG_URL", "http://localhost:8084")
        
        # Build number tracking
        self.build_number = self._get_build_number()
        
        # Add the enhanced endpoints
        self._add_enhanced_endpoints()
    
    def _get_build_number(self) -> str:
        """Get the build number from file or environment."""
        build_number = os.environ.get("BUILD_NUMBER")
        if not build_number:
            # Try to read from file
            build_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "frontend",
                "build_number.txt"
            )
            try:
                if os.path.exists(build_file):
                    with open(build_file, "r") as f:
                        build_number = f.read().strip()
            except Exception as e:
                logging.warning(f"Could not read build number file: {e}")
        
        return build_number or "dev"
    
    def _add_enhanced_endpoints(self) -> None:
        """Add enhanced endpoints with better documentation."""
        
        # System information endpoint with comprehensive service status
        @self.app.get(
            "/api/info",
            response_model=SystemInfo,
            tags=["System"],
            summary=system_info_example["summary"],
            description=system_info_example["description"],
            responses=system_info_example["responses"],
        )
        async def get_system_info() -> SystemInfo:
            """Get comprehensive system information and service status."""
            services = {}
            
            # Check MCP server (this service)
            services["mcp_server"] = ServiceInfo(
                name="MCP Server",
                port=8000,
                status="running",
                version=self.app.version,
            )
            
            # Check Entity Detector service
            entity_detector_status = await self._check_service_status(
                self.entity_detector_url, "Entity Detector"
            )
            services["entity_detector"] = entity_detector_status
            
            # Check GraphRAG service
            graphrag_status = await self._check_service_status(
                self.graphrag_url, "GraphRAG"
            )
            services["graphrag"] = graphrag_status
            
            # Check Redis
            redis_port = 6379
            redis_status = "unknown"
            try:
                # Simple check if Redis port is open
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.2)
                result = sock.connect_ex(('127.0.0.1', redis_port))
                redis_status = "running" if result == 0 else "stopped"
                sock.close()
            except Exception:
                redis_status = "error"
            
            services["redis"] = ServiceInfo(
                name="Redis",
                port=redis_port,
                status=redis_status,
            )
            
            # Return complete system info
            return SystemInfo(
                version=self.app.version,
                build_number=self.build_number,
                services=services,
            )
        
        # Enhanced XML upload endpoint with detailed documentation
        @self.app.post(
            "/xml/upload",
            response_model=XmlDocumentModel,
            tags=["XML"],
            summary=xml_upload_example["summary"],
            description=xml_upload_example["description"],
            responses=xml_upload_example["responses"],
        )
        async def enhanced_upload_xml(
            request: XmlUploadRequest,
        ) -> XmlDocumentModel:
            """Enhanced XML upload with improved documentation."""
            # Simulate conditions for testing
            await self._simulate_conditions()
            
            # Use the same implementation from the base class
            try:
                # Reimplement the upload functionality directly
                from agent_provocateur.xml_parser import identify_researchable_nodes
                import datetime
                import uuid
                
                # Generate a new document ID
                doc_id = f"xml{uuid.uuid4().hex[:8]}"
                
                # Identify researchable nodes
                researchable_nodes = identify_researchable_nodes(request.xml_content)
                
                # Determine root element
                root_element = "unknown"
                namespaces = {}
                
                try:
                    from defusedxml import ElementTree
                    root = ElementTree.fromstring(request.xml_content)
                    
                    # Extract root element name
                    root_name = root.tag
                    if "}" in root_name:
                        root_name = root_name.split("}", 1)[1]
                    root_element = root_name
                    
                    # Extract namespaces
                    import re
                    xmlns_pattern = r'xmlns:([a-zA-Z0-9]+)="([^"]+)"'
                    matches = re.findall(xmlns_pattern, request.xml_content)
                    for prefix, uri in matches:
                        namespaces[prefix] = uri
                except Exception as e:
                    logging.warning(f"Error parsing XML: {e}")
                
                # Create the XML document
                now = datetime.datetime.utcnow().isoformat()
                doc = XmlDocumentModel(
                    doc_id=doc_id,
                    doc_type="xml",
                    title=request.title,
                    created_at=now,
                    updated_at=now,
                    content=request.xml_content,
                    root_element=root_element,
                    namespaces=namespaces,
                    researchable_nodes=researchable_nodes,
                )
                return doc
            except Exception as e:
                logging.error(f"Error uploading XML: {e}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to process XML content: {str(e)}"
                )
        
        # Entity extraction proxy
        @self.app.post(
            "/proxy/entity-extraction",
            response_model=EntityExtractionResponse,
            tags=["Entity Detection"],
            summary=entity_extraction_example["summary"],
            description=entity_extraction_example["description"],
            responses=entity_extraction_example["responses"],
        )
        async def proxy_entity_extraction(
            request: EntityExtractionRequest,
        ) -> EntityExtractionResponse:
            """Proxy request to Entity Detector service."""
            await self._simulate_conditions()
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.entity_detector_url}/tools/extract_entities/run",
                        json=request.dict(exclude_none=True),
                        timeout=10.0,
                    )
                    
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"Entity Detector error: {response.text}"
                        )
                    
                    return response.json()
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"Could not connect to Entity Detector service: {str(e)}"
                )
        
        # GraphRAG query proxy
        @self.app.post(
            "/proxy/graphrag-query",
            response_model=GraphQueryResponse,
            tags=["Research"],
            summary=graphrag_query_example["summary"],
            description=graphrag_query_example["description"],
            responses=graphrag_query_example["responses"],
        )
        async def proxy_graphrag_query(
            request: GraphQueryRequest,
        ) -> GraphQueryResponse:
            """Proxy request to GraphRAG service."""
            await self._simulate_conditions()
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.graphrag_url}/api/tools/graphrag_query",
                        json=request.dict(exclude_none=True),
                        timeout=20.0,  # Research can take longer
                    )
                    
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"GraphRAG error: {response.text}"
                        )
                    
                    return response.json()
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"Could not connect to GraphRAG service: {str(e)}"
                )
        
        # Integrated workflow for end-to-end processing
        @self.app.post(
            "/workflow/process-document",
            tags=["Workflow"],
            summary="End-to-End Document Processing",
            description="""
            Process a document through the complete workflow:
            1. Upload XML document
            2. Extract entities from the document
            3. Research entities using GraphRAG
            4. Return the complete results
            
            This endpoint orchestrates the end-to-end process across all services.
            """,
        )
        async def process_document_workflow(
            xml_content: str = Body(..., description="Raw XML content"),
            title: str = Body(..., description="Document title"),
            research_query: Optional[str] = Body(None, description="Optional research query"),
        ):
            """Complete end-to-end document processing workflow."""
            await self._simulate_conditions()
            
            # Step 1: Upload XML document
            try:
                # Reimplement the upload functionality directly
                from agent_provocateur.xml_parser import identify_researchable_nodes
                import datetime
                import uuid
                
                # Generate a new document ID
                doc_id = f"xml{uuid.uuid4().hex[:8]}"
                
                # Identify researchable nodes
                researchable_nodes = identify_researchable_nodes(xml_content)
                
                # Determine root element
                root_element = "unknown"
                namespaces = {}
                
                try:
                    from defusedxml import ElementTree
                    root = ElementTree.fromstring(xml_content)
                    
                    # Extract root element name
                    root_name = root.tag
                    if "}" in root_name:
                        root_name = root_name.split("}", 1)[1]
                    root_element = root_name
                    
                    # Extract namespaces
                    import re
                    xmlns_pattern = r'xmlns:([a-zA-Z0-9]+)="([^"]+)"'
                    matches = re.findall(xmlns_pattern, xml_content)
                    for prefix, uri in matches:
                        namespaces[prefix] = uri
                except Exception as e:
                    logging.warning(f"Error parsing XML: {e}")
                
                # Create the XML document
                now = datetime.datetime.utcnow().isoformat()
                doc = XmlDocumentModel(
                    doc_id=doc_id,
                    doc_type="xml",
                    title=title,
                    created_at=now,
                    updated_at=now,
                    content=xml_content,
                    root_element=root_element,
                    namespaces=namespaces,
                    researchable_nodes=researchable_nodes,
                )
                doc_id = doc.doc_id
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to upload document: {str(e)}"
                )
            
            # Step 2: Extract entities
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.entity_detector_url}/tools/extract_entities/run",
                        json={"text": xml_content},
                        timeout=10.0,
                    )
                    
                    if response.status_code != 200:
                        return JSONResponse(
                            status_code=200,
                            content={
                                "doc_id": doc_id,
                                "entities": [],
                                "research": None,
                                "status": "partial_success",
                                "errors": [f"Entity extraction failed: {response.text}"]
                            }
                        )
                    
                    entities_response = response.json()
                    entities = entities_response.get("entities", [])
            except Exception as e:
                return JSONResponse(
                    status_code=200,
                    content={
                        "doc_id": doc_id,
                        "entities": [],
                        "research": None,
                        "status": "partial_success",
                        "errors": [f"Entity extraction service error: {str(e)}"]
                    }
                )
            
            # Step 3: Research (if entities found and query provided)
            research_results = None
            errors = []
            
            if entities and research_query:
                try:
                    # Extract entity text for focus
                    focus_entities = [e["entity"] for e in entities[:3]]
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{self.graphrag_url}/api/tools/graphrag_query",
                            json={
                                "query": research_query,
                                "focus_entities": focus_entities,
                                "options": {"max_results": 5}
                            },
                            timeout=20.0,
                        )
                        
                        if response.status_code == 200:
                            research_results = response.json()
                        else:
                            errors.append(f"Research failed: {response.text}")
                except Exception as e:
                    errors.append(f"Research service error: {str(e)}")
            
            # Return complete workflow results
            return {
                "doc_id": doc_id,
                "entities": entities,
                "research": research_results,
                "status": "success" if not errors else "partial_success",
                "errors": errors if errors else None
            }
    
    async def _check_service_status(self, base_url: str, service_name: str) -> ServiceInfo:
        """Check the status of a service."""
        port = int(base_url.split(":")[-1]) if ":" in base_url else 0
        status = "unknown"
        version = None
        details = None
        
        try:
            async with httpx.AsyncClient() as client:
                try:
                    # First try health endpoint
                    response = await client.get(
                        f"{base_url}/health",
                        timeout=2.0,
                    )
                    if response.status_code == 200:
                        status = "running"
                        details = response.json()
                except Exception:
                    # Then try api/info endpoint
                    try:
                        response = await client.get(
                            f"{base_url}/api/info",
                            timeout=2.0,
                        )
                        if response.status_code == 200:
                            status = "running"
                            info = response.json()
                            version = info.get("version")
                            details = info
                    except Exception:
                        # Try tools endpoint (for entity detector)
                        try:
                            response = await client.get(
                                f"{base_url}/tools",
                                timeout=2.0,
                            )
                            if response.status_code == 200:
                                status = "running"
                                details = {"tools": response.json()}
                        except Exception:
                            status = "stopped"
        except Exception:
            status = "error"
        
        return ServiceInfo(
            name=f"{service_name} MCP",
            port=port,
            status=status,
            version=version,
            details=details,
        )
    
    async def _upload_xml(self, xml_content: str, title: str):
        """Upload XML document implementation from base class."""
        # This is a duplicate of the implementation in the base class
        # to make it accessible to the enhanced version of the endpoint
        pass


def create_enhanced_app() -> FastAPI:
    """Create and configure the enhanced FastAPI application.
    
    Returns:
        FastAPI: The configured FastAPI application with enhanced documentation
    """
    server = EnhancedMcpServer()
    
    # Add CORS middleware for frontend integration
    from fastapi.middleware.cors import CORSMiddleware
    server.app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return server.app


# Entry point for running the enhanced server
if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the enhanced MCP server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--entity-detector", default="http://localhost:8082", help="Entity Detector URL")
    parser.add_argument("--graphrag", default="http://localhost:8084", help="GraphRAG URL")
    
    args = parser.parse_args()
    
    # Set environment variables for service URLs
    os.environ["ENTITY_DETECTOR_URL"] = args.entity_detector
    os.environ["GRAPHRAG_URL"] = args.graphrag
    
    # Create and run the app
    app = create_enhanced_app()
    uvicorn.run(app, host=args.host, port=args.port)