"""
Improved API documentation for Agent Provocateur MCP Server.

This module contains Pydantic models and documentation metadata that can be used
to enhance the OpenAPI documentation of the MCP Server.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class ApiInfo:
    """API information for documentation."""
    
    title = "Agent Provocateur MCP API"
    version = "1.0.0"
    description = """
    # Agent Provocateur MCP API
    
    This API serves as the central entry point for the Agent Provocateur system. It provides access
    to document management, entity extraction, research capabilities, and agent interactions.
    
    ## Key Components
    
    - **MCP Server**: Main API server (port 8000)
    - **Entity Detector**: Entity extraction service (port 8082/9585)
    - **GraphRAG**: Graph-based research service (port 8084/9584)
    
    ## Workflow Integration
    
    A typical workflow involves:
    
    1. Upload a document (XML, text, etc.)
    2. Extract entities from the document
    3. Research the entities using GraphRAG
    4. Generate attribution or verification results
    """
    
    contact = {
        "name": "Agent Provocateur Team",
        "url": "https://github.com/agent-provocateur/docs",
        "email": "support@agent-provocateur.example.com",
    }
    
    license_info = {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }
    
    tags = [
        {
            "name": "Documents",
            "description": "Document management endpoints",
        },
        {
            "name": "XML",
            "description": "XML document handling and processing",
        },
        {
            "name": "Entity Detection",
            "description": "Entity extraction and analysis",
        },
        {
            "name": "Research",
            "description": "Research and knowledge graph capabilities",
        },
        {
            "name": "LLM",
            "description": "Language model integration",
        },
        {
            "name": "System",
            "description": "System status and configuration",
        },
    ]


class EntityType(str, Enum):
    """Entity types recognized by the system."""
    
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    DATE = "DATE"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    TIME = "TIME"
    FACILITY = "FACILITY"
    PRODUCT = "PRODUCT"
    EVENT = "EVENT"
    WORK_OF_ART = "WORK_OF_ART"
    LAW = "LAW"
    LANGUAGE = "LANGUAGE"
    TECHNOLOGY = "TECHNOLOGY"
    CONCEPT = "CONCEPT"
    CLAIM = "CLAIM"


class RelationType(str, Enum):
    """Relationship types between entities."""
    
    RELATED_TO = "RELATED_TO"
    PART_OF = "PART_OF"
    LOCATED_IN = "LOCATED_IN"
    WORKS_FOR = "WORKS_FOR"
    CREATED_BY = "CREATED_BY"
    HAS_PROPERTY = "HAS_PROPERTY"
    CONTRADICTS = "CONTRADICTS"
    SUPPORTS = "SUPPORTS"


class Entity(BaseModel):
    """Entity extracted from text."""
    
    entity: str = Field(..., description="Entity text")
    type: Union[EntityType, str] = Field(..., description="Entity type")
    confidence: float = Field(..., description="Detection confidence score (0-1)")
    start: Optional[int] = Field(None, description="Start position in text")
    end: Optional[int] = Field(None, description="End position in text")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional entity metadata")


class EntityExtractionRequest(BaseModel):
    """Request for entity extraction."""
    
    text: str = Field(..., description="Text to extract entities from")
    types: Optional[List[str]] = Field(None, description="Entity types to extract (optional)")
    minConfidence: Optional[float] = Field(0.5, description="Minimum confidence threshold (0-1)")
    includeMetadata: Optional[bool] = Field(False, description="Include additional metadata")
    model: Optional[str] = Field("default", description="Detection model to use")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Apple Inc. was founded by Steve Jobs and Steve Wozniak in Cupertino, California in 1976.",
                "types": ["PERSON", "ORGANIZATION", "LOCATION", "DATE"],
                "minConfidence": 0.7,
                "includeMetadata": True,
                "model": "nlp"
            }
        }


class EntityExtractionResponse(BaseModel):
    """Response from entity extraction."""
    
    entities: List[Entity] = Field(..., description="Extracted entities")
    status: str = Field("success", description="Status of the extraction")
    model: Optional[str] = Field(None, description="Model used for extraction")
    
    class Config:
        schema_extra = {
            "example": {
                "entities": [
                    {
                        "entity": "Apple Inc.",
                        "type": "ORGANIZATION",
                        "confidence": 0.98,
                        "start": 0,
                        "end": 10
                    },
                    {
                        "entity": "Steve Jobs",
                        "type": "PERSON",
                        "confidence": 0.97,
                        "start": 25,
                        "end": 35
                    },
                    {
                        "entity": "Steve Wozniak",
                        "type": "PERSON",
                        "confidence": 0.95,
                        "start": 40,
                        "end": 53
                    },
                    {
                        "entity": "Cupertino",
                        "type": "LOCATION",
                        "confidence": 0.93,
                        "start": 57,
                        "end": 66
                    },
                    {
                        "entity": "California",
                        "type": "LOCATION",
                        "confidence": 0.96,
                        "start": 68,
                        "end": 78
                    },
                    {
                        "entity": "1976",
                        "type": "DATE",
                        "confidence": 0.99,
                        "start": 82,
                        "end": 86
                    }
                ],
                "status": "success",
                "model": "nlp"
            }
        }


class Relationship(BaseModel):
    """Relationship between entities."""
    
    relationship_id: str = Field(..., description="Unique relationship ID")
    source_entity_id: str = Field(..., description="ID of the source entity")
    target_entity_id: str = Field(..., description="ID of the target entity")
    relation_type: RelationType = Field(..., description="Type of relationship")
    confidence: float = Field(..., description="Confidence score (0-1)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional relationship metadata")


class GraphQueryRequest(BaseModel):
    """Request for graph research query."""
    
    query: str = Field(..., description="Natural language query for research")
    focus_entities: Optional[List[str]] = Field(None, description="Entities to focus on")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Tell me about the health benefits of apples",
                "focus_entities": ["apple", "health", "nutrition"],
                "options": {
                    "max_results": 5,
                    "include_sources": True
                }
            }
        }


class GraphQueryResponse(BaseModel):
    """Response from graph research query."""
    
    success: bool = Field(..., description="Query success status")
    sources: List[Dict[str, Any]] = Field(..., description="Sources used for the response")
    attributed_prompt: Optional[str] = Field(None, description="Research output with attribution")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "sources": [
                    {
                        "title": "Health Benefits of Apples",
                        "relevance": 0.95,
                        "content": "Apples are high in fiber and vitamin C..."
                    },
                    {
                        "title": "Nutritional Analysis of Common Fruits",
                        "relevance": 0.87,
                        "content": "Per 100g, apples contain approximately..."
                    }
                ],
                "attributed_prompt": "According to research, apples provide several health benefits [SOURCE_1]. They are high in fiber and vitamin C, which contribute to heart health and immune function. Nutritional analysis shows that per 100g, apples contain significant amounts of antioxidants [SOURCE_2]."
            }
        }


class XmlUploadRequest(BaseModel):
    """Request for uploading XML documents."""
    
    xml_content: str = Field(..., description="Raw XML content")
    title: str = Field(..., description="Document title")
    
    class Config:
        schema_extra = {
            "example": {
                "xml_content": "<?xml version=\"1.0\"?>\n<research>\n  <finding id=\"f1\">\n    <statement>Regular exercise reduces the risk of cardiovascular disease.</statement>\n    <confidence>high</confidence>\n  </finding>\n</research>",
                "title": "Health Research Findings"
            }
        }


class XmlNodeModel(BaseModel):
    """XML node for verification."""
    
    xpath: str = Field(..., description="XPath to the node")
    element_name: str = Field(..., description="Element name")
    content: Optional[str] = Field(None, description="Text content")
    attributes: Optional[Dict[str, str]] = Field(None, description="Element attributes")
    verification_status: Optional[str] = Field("pending", description="Verification status")


class XmlDocumentModel(BaseModel):
    """XML document model."""
    
    doc_id: str = Field(..., description="Document ID")
    doc_type: str = Field("xml", description="Document type")
    title: str = Field(..., description="Document title")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    content: str = Field(..., description="Raw XML content")
    root_element: str = Field(..., description="XML root element name")
    namespaces: Dict[str, str] = Field({}, description="XML namespaces")
    researchable_nodes: List[XmlNodeModel] = Field([], description="Nodes that can be researched")
    
    class Config:
        schema_extra = {
            "example": {
                "doc_id": "xml123",
                "doc_type": "xml",
                "title": "Climate Research Claims",
                "created_at": "2025-04-23T10:20:30.123Z",
                "updated_at": "2025-04-23T10:25:15.456Z",
                "content": "<?xml version=\"1.0\"?>\n<research>\n  <finding id=\"f1\">\n    <statement>Global temperatures have risen by 1.1°C since pre-industrial times.</statement>\n    <confidence>high</confidence>\n  </finding>\n</research>",
                "root_element": "research",
                "namespaces": {},
                "researchable_nodes": [
                    {
                        "xpath": "//finding",
                        "element_name": "finding",
                        "content": None,
                        "attributes": {"id": "f1"},
                        "verification_status": "pending"
                    },
                    {
                        "xpath": "//statement",
                        "element_name": "statement",
                        "content": "Global temperatures have risen by 1.1°C since pre-industrial times.",
                        "verification_status": "pending"
                    }
                ]
            }
        }


class ServiceInfo(BaseModel):
    """Service information for system status."""
    
    name: str = Field(..., description="Service name")
    port: int = Field(..., description="Service port")
    status: str = Field(..., description="Service status")
    version: Optional[str] = Field(None, description="Service version")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional service details")


class SystemInfo(BaseModel):
    """System status information."""
    
    version: str = Field(..., description="API version")
    build_number: Optional[str] = Field(None, description="Build number")
    services: Dict[str, ServiceInfo] = Field(..., description="Status of system services")
    
    class Config:
        schema_extra = {
            "example": {
                "version": "1.0.0",
                "build_number": "20250423.5",
                "services": {
                    "mcp_server": {
                        "name": "MCP Server",
                        "port": 8000,
                        "status": "running",
                        "version": "1.0.0"
                    },
                    "entity_detector": {
                        "name": "Entity Detector MCP",
                        "port": 8082,
                        "status": "running",
                        "version": "1.0.0"
                    },
                    "graphrag": {
                        "name": "GraphRAG MCP",
                        "port": 8084,
                        "status": "running",
                        "version": "1.0.0"
                    }
                }
            }
        }


# Example endpoint docs for API documentation improvement

xml_upload_example = {
    "summary": "Upload XML Document",
    "description": """
    Upload a new XML document for processing and analysis.
    
    This endpoint accepts raw XML content and processes it to identify researchable nodes
    such as claims, statements, and facts that can be verified through research.
    
    ## Usage
    
    1. Prepare your XML content with properly structured claims or statements
    2. Provide a descriptive title for the document
    3. Submit the content and receive a document ID for further operations
    
    ## Next Steps
    
    After uploading, you can:
    - Extract entities using the Entity Detector MCP
    - Research the extracted entities using GraphRAG MCP
    - Get researchable nodes using the `/documents/{doc_id}/xml/nodes` endpoint
    
    ## Example
    
    ```python
    import requests
    import json
    
    # Load XML content from file
    with open('research.xml', 'r') as f:
        xml_content = f.read()
    
    # Prepare request payload
    payload = {
        "xml_content": xml_content,
        "title": "Research Findings"
    }
    
    # Upload the XML document
    response = requests.post(
        "http://localhost:8000/xml/upload",
        json=payload
    )
    
    # Get the document ID for further processing
    document = response.json()
    doc_id = document['doc_id']
    print(f"Uploaded document with ID: {doc_id}")
    ```
    """,
    "responses": {
        "200": {
            "description": "XML document uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "doc_id": "xml123",
                        "doc_type": "xml",
                        "title": "Research Findings",
                        "created_at": "2025-04-23T10:20:30.123Z",
                        "root_element": "research",
                        "researchable_nodes": [
                            {
                                "xpath": "//statement",
                                "element_name": "statement",
                                "content": "Global temperatures have risen by 1.1°C since pre-industrial times.",
                                "verification_status": "pending"
                            }
                        ]
                    }
                }
            }
        },
        "400": {
            "description": "Invalid XML content",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to process XML content: XML syntax error on line 5"
                    }
                }
            }
        },
        "500": {
            "description": "Server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error occurred while processing XML"
                    }
                }
            }
        }
    }
}

entity_extraction_example = {
    "summary": "Extract Entities",
    "description": """
    Extract named entities from text using the Entity Detector MCP.
    
    This endpoint processes text to identify entities such as people, organizations,
    locations, dates, and concepts. It uses natural language processing to recognize
    entities and assign confidence scores.
    
    ## Integration with GraphRAG
    
    After extracting entities, you can use the GraphRAG MCP to research these entities
    and generate attributed content through the `/api/tools/graphrag_query` endpoint.
    
    ## Entity Types
    
    The system recognizes many entity types, including:
    - PERSON: People and characters
    - ORGANIZATION: Companies, agencies, institutions
    - LOCATION: Countries, cities, geographical features
    - DATE: Calendar dates, time periods
    - TECHNOLOGY: Technical systems, products, languages
    - CONCEPT: Abstract ideas, theories, fields of study
    
    ## Example Usage
    
    ```python
    import requests
    
    # Get document content
    doc_id = "xml123"
    response = requests.get(f"http://localhost:8000/documents/{doc_id}/xml/content")
    xml_content = response.text
    
    # Extract entities
    entity_response = requests.post(
        "http://localhost:8082/tools/extract_entities/run",
        json={
            "text": xml_content,
            "minConfidence": 0.7
        }
    )
    
    entities = entity_response.json()["entities"]
    print(f"Found {len(entities)} entities")
    ```
    """,
    "responses": {
        "200": {
            "description": "Entities extracted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "entities": [
                            {
                                "entity": "global temperatures",
                                "type": "CONCEPT",
                                "confidence": 0.92
                            },
                            {
                                "entity": "1.1°C",
                                "type": "MEASURE",
                                "confidence": 0.95
                            },
                            {
                                "entity": "pre-industrial times",
                                "type": "DATE",
                                "confidence": 0.88
                            }
                        ],
                        "status": "success",
                        "model": "nlp"
                    }
                }
            }
        },
        "400": {
            "description": "Invalid request",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Text parameter is required"
                    }
                }
            }
        },
        "500": {
            "description": "Server error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Entity extraction failed",
                        "message": "NLP processing error"
                    }
                }
            }
        }
    }
}

graphrag_query_example = {
    "summary": "Research Query",
    "description": """
    Query the knowledge graph for information about specific entities or topics.
    
    This endpoint leverages the GraphRAG (Graph Retrieval Augmented Generation) system
    to research entities and generate attributed responses that cite sources.
    
    ## Integration with Entity Extraction
    
    This endpoint works well with entities extracted from documents:
    1. Extract entities from a document using the Entity Detector MCP
    2. Research those entities using this GraphRAG query endpoint
    3. Generate attribution or verification content with source references
    
    ## Query Options
    
    - `focus_entities`: List of entities to center the research around
    - `max_results`: Maximum number of sources to return (default: 5)
    - `include_sources`: Whether to include source details (default: true)
    
    ## Example Usage
    
    ```python
    import requests
    
    # Research a specific entity
    response = requests.post(
        "http://localhost:8084/api/tools/graphrag_query",
        json={
            "query": "Tell me about global temperature rise since pre-industrial times",
            "focus_entities": ["global temperature", "climate change"],
            "options": {
                "max_results": 3,
                "include_sources": true
            }
        }
    )
    
    result = response.json()
    attributed_text = result["attributed_prompt"]
    sources = result["sources"]
    
    print(f"Found {len(sources)} sources")
    print(attributed_text)
    ```
    """,
    "responses": {
        "200": {
            "description": "Research query successful",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "sources": [
                            {
                                "title": "IPCC Sixth Assessment Report",
                                "relevance": 0.95,
                                "content": "According to multiple lines of evidence, global surface temperature has increased by 1.1°C compared to pre-industrial times (1850-1900)."
                            },
                            {
                                "title": "Climate Change: Evidence and Causes",
                                "relevance": 0.88,
                                "content": "The global average surface temperature has increased by about 1.1°C since the pre-industrial era due to human activities, primarily the burning of fossil fuels."
                            }
                        ],
                        "attributed_prompt": "According to the research, global temperatures have risen by approximately 1.1°C since pre-industrial times (1850-1900) [SOURCE_1]. This warming has been attributed to human activities, primarily the burning of fossil fuels, which has increased the concentration of greenhouse gases in the atmosphere [SOURCE_2]."
                    }
                }
            }
        },
        "400": {
            "description": "Invalid request",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": "Query parameter is required"
                    }
                }
            }
        },
        "500": {
            "description": "Server error",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": "Research query failed due to internal server error"
                    }
                }
            }
        }
    }
}

system_info_example = {
    "summary": "System Information",
    "description": """
    Get comprehensive information about the system status and components.
    
    This endpoint provides details about all service components, their status,
    version information, and port configurations. It's useful for monitoring and
    troubleshooting the system.
    
    ## Included Services
    
    - MCP Server: Main API server
    - Entity Detector MCP: Entity extraction service
    - GraphRAG MCP: Research and knowledge graph service
    - Redis: Caching and messaging service
    
    ## Usage
    
    ```python
    import requests
    
    # Get system status
    response = requests.get("http://localhost:8000/api/info")
    info = response.json()
    
    # Check if all required services are running
    all_running = all(
        service["status"] == "running"
        for service in info["services"].values()
    )
    
    if all_running:
        print("All services are operational")
    else:
        print("Some services are not running")
        for name, service in info["services"].items():
            if service["status"] != "running":
                print(f"- {name} is {service['status']}")
    ```
    """,
    "responses": {
        "200": {
            "description": "System information retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "version": "1.0.0",
                        "build_number": "20250423.5",
                        "services": {
                            "mcp_server": {
                                "name": "MCP Server",
                                "port": 8000,
                                "status": "running",
                                "version": "1.0.0",
                                "uptime": "1d 2h 34m"
                            },
                            "entity_detector": {
                                "name": "Entity Detector MCP",
                                "port": 8082,
                                "status": "running",
                                "version": "1.0.0",
                                "uptime": "1d 2h 30m"
                            },
                            "graphrag": {
                                "name": "GraphRAG MCP",
                                "port": 8084,
                                "status": "running",
                                "version": "1.0.0",
                                "uptime": "1d 2h 25m"
                            },
                            "redis": {
                                "name": "Redis",
                                "port": 6379,
                                "status": "running",
                                "uptime": "1d 3h 10m"
                            }
                        }
                    }
                }
            }
        },
        "500": {
            "description": "Server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to retrieve system information"
                    }
                }
            }
        }
    }
}


def generate_api_docs():
    """Generate improved API documentation configuration."""
    
    return {
        "title": ApiInfo.title,
        "version": ApiInfo.version,
        "description": ApiInfo.description,
        "contact": ApiInfo.contact,
        "license_info": ApiInfo.license_info,
        "tags": ApiInfo.tags,
        "endpoints": {
            "/xml/upload": xml_upload_example,
            "/api/tools/extract_entities/run": entity_extraction_example,
            "/api/tools/graphrag_query": graphrag_query_example,
            "/api/info": system_info_example,
        }
    }


# Example of how to apply these improvements to a FastAPI app
def update_fastapi_docs(app):
    """Update FastAPI app with improved documentation."""
    
    # Update API metadata
    app.title = ApiInfo.title
    app.description = ApiInfo.description
    app.version = ApiInfo.version
    
    # You would need to modify the actual route handlers to add the detailed documentation
    # This is just a demonstration of how you would do it
    
    # Example:
    # @app.post(
    #     "/xml/upload",
    #     response_model=XmlDocumentModel,
    #     responses={
    #         200: {"model": XmlDocumentModel},
    #         400: {"model": ErrorModel},
    #         500: {"model": ErrorModel},
    #     },
    #     tags=["XML"],
    #     summary=xml_upload_example["summary"],
    #     description=xml_upload_example["description"],
    # )
    # async def upload_xml(
    #     xml_content: str = Body(..., description="Raw XML content"),
    #     title: str = Body(..., description="Document title")
    # ) -> XmlDocumentModel:
    #     ...
    
    return app