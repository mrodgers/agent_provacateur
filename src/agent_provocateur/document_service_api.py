import asyncio
import datetime
import logging
import random
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel

from agent_provocateur.llm_service import LlmService
from agent_provocateur.models import (
    Document,
    DocumentContent,
    JiraTicket,
    LlmRequest,
    LlmResponse,
    McpError,
    PdfDocument,
    PdfPage,
    SearchResult,
    SearchResults,
    ImageDocument,
    CodeDocument,
    StructuredDataDocument,
    XmlDocument,
    XmlNode,
)
from agent_provocateur.xml_parser import identify_researchable_nodes

# Sample data for mocking
SAMPLE_JIRA_TICKETS: Dict[str, JiraTicket] = {
    "AP-1": JiraTicket(
        id="AP-1",
        status="Open",
        assignee="jdoe",
        summary="Set up Document Service API for agent testing",
    ),
    "AP-2": JiraTicket(
        id="AP-2",
        status="In Progress",
        assignee="asmith",
        summary="Implement A2A messaging layer",
    ),
    "AP-3": JiraTicket(
        id="AP-3",
        status="Done",
        assignee="mjones",
        summary="Create project documentation",
    ),
}

# Current timestamp for document creation dates
NOW = datetime.datetime.now().isoformat()

# Sample text documents
SAMPLE_DOCS: Dict[str, DocumentContent] = {
    "doc1": DocumentContent(
        doc_id="doc1",
        doc_type="text",
        title="Agent System Design",
        created_at=NOW,
        updated_at=NOW,
        markdown="# Agent System Design\n\nThis document outlines...",
        html="<h1>Agent System Design</h1><p>This document outlines...</p>",
    ),
    "doc2": DocumentContent(
        doc_id="doc2",
        doc_type="text",
        title="Implementation Guide",
        created_at=NOW,
        updated_at=NOW,
        markdown="# Implementation Guide\n\nFollow these steps...",
        html="<h1>Implementation Guide</h1><p>Follow these steps...</p>",
    ),
}

# Sample PDF documents
SAMPLE_PDFS: Dict[str, PdfDocument] = {
    "pdf1": PdfDocument(
        doc_id="pdf1",
        doc_type="pdf",
        title="Agent System Architecture",
        created_at=NOW,
        updated_at=NOW,
        url="https://example.com/docs/agent_system.pdf",
        pages=[
            PdfPage(
                text="Introduction to agent systems and their applications...",
                page_number=1,
            ),
            PdfPage(
                text="Core components of the agent architecture include...",
                page_number=2,
            ),
        ],
    ),
}

# Sample image documents
SAMPLE_IMAGES: Dict[str, ImageDocument] = {
    "img1": ImageDocument(
        doc_id="img1",
        doc_type="image",
        title="Agent Communication Diagram",
        created_at=NOW,
        updated_at=NOW,
        url="https://example.com/images/agent_diagram.png",
        alt_text="Diagram showing agent communication flow",
        caption="Figure 1: Agent Communication Architecture",
        width=800,
        height=600,
        format="png",
    ),
}

# Sample code documents
SAMPLE_CODE: Dict[str, CodeDocument] = {
    "code1": CodeDocument(
        doc_id="code1",
        doc_type="code",
        title="Agent Base Class",
        created_at=NOW,
        updated_at=NOW,
        content="""
class BaseAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        
    async def handle_message(self, message):
        pass
        
    async def send_message(self, target_agent, content):
        pass
""",
        language="python",
        line_count=9,
    ),
}

# Sample structured data documents
SAMPLE_STRUCTURED_DATA: Dict[str, StructuredDataDocument] = {
    "data1": StructuredDataDocument(
        doc_id="data1",
        doc_type="structured_data",
        title="Agent Configuration",
        created_at=NOW,
        updated_at=NOW,
        data={
            "agent_types": [
                {"id": "doc_agent", "capabilities": ["fetch_documents", "search_content"]},
                {"id": "decision_agent", "capabilities": ["evaluate_options", "make_decisions"]},
            ],
            "default_timeout": 30,
            "max_retry_count": 3,
        },
        schema_def={
            "type": "object",
            "properties": {
                "agent_types": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "capabilities": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "default_timeout": {"type": "integer"},
                "max_retry_count": {"type": "integer"},
            },
        },
        format="json",
    ),
}

# Sample XML documents
SAMPLE_XML_DOCUMENTS: Dict[str, XmlDocument] = {
    "xml1": XmlDocument(
        doc_id="xml1",
        doc_type="xml",
        title="Research Findings",
        created_at=NOW,
        updated_at=NOW,
        content="""<?xml version="1.0" encoding="UTF-8"?>
<research>
    <metadata>
        <title>Sample Research Paper</title>
        <author>John Doe</author>
        <date>2023-01-15</date>
    </metadata>
    <abstract>
        This is a sample abstract that contains statements requiring verification.
    </abstract>
    <findings>
        <finding id="f1">
            <statement>The global temperature has risen by 1.1°C since pre-industrial times.</statement>
            <confidence>high</confidence>
        </finding>
        <finding id="f2">
            <statement>Renewable energy adoption increased by 45% in the last decade.</statement>
            <confidence>medium</confidence>
        </finding>
    </findings>
    <references>
        <reference id="r1">IPCC Climate Report 2022</reference>
        <reference id="r2">Energy Statistics Quarterly, Vol 12</reference>
    </references>
</research>""",
        root_element="research",
        namespaces={},
        researchable_nodes=[
            XmlNode(
                xpath="//finding",
                element_name="finding",
                content=None,
                attributes={"id": "f1"},
                verification_status="pending"
            ),
            XmlNode(
                xpath="//finding",
                element_name="finding",
                content=None,
                attributes={"id": "f2"},
                verification_status="pending"
            ),
            XmlNode(
                xpath="//statement",
                element_name="statement",
                content="The global temperature has risen by 1.1°C since pre-industrial times.",
                verification_status="pending"
            ),
            XmlNode(
                xpath="//statement",
                element_name="statement",
                content="Renewable energy adoption increased by 45% in the last decade.",
                verification_status="pending"
            ),
        ]
    ),
    "xml2": XmlDocument(
        doc_id="xml2",
        doc_type="xml",
        title="Product Catalog",
        created_at=NOW,
        updated_at=NOW,
        content="""<?xml version="1.0" encoding="UTF-8"?>
<product-catalog xmlns:prod="http://example.com/product" xmlns:mfg="http://example.com/manufacturer">
    <prod:product id="p1">
        <prod:name>Eco-friendly Water Bottle</prod:name>
        <prod:description>Sustainable water bottle made from recycled materials.</prod:description>
        <prod:price currency="USD">24.99</prod:price>
        <prod:sustainability-score>9.5</prod:sustainability-score>
        <prod:claims>
            <prod:claim id="c1">Made from 100% recycled ocean plastic</prod:claim>
            <prod:claim id="c2">Carbon-neutral manufacturing process</prod:claim>
        </prod:claims>
        <mfg:details>
            <mfg:manufacturer>EcoGoods Inc.</mfg:manufacturer>
            <mfg:country>Canada</mfg:country>
            <mfg:certification>ISO 14001</mfg:certification>
        </mfg:details>
    </prod:product>
</product-catalog>""",
        root_element="product-catalog",
        namespaces={
            "prod": "http://example.com/product",
            "mfg": "http://example.com/manufacturer"
        },
        researchable_nodes=[
            XmlNode(
                xpath="//claim",
                element_name="claim",
                content="Made from 100% recycled ocean plastic",
                attributes={"id": "c1"},
                verification_status="pending"
            ),
            XmlNode(
                xpath="//claim",
                element_name="claim",
                content="Carbon-neutral manufacturing process",
                attributes={"id": "c2"},
                verification_status="pending"
            ),
        ]
    ),
}

# Consolidated document store for all document types
DOCUMENT_STORE: Dict[str, Document] = {
    **SAMPLE_DOCS,
    **SAMPLE_PDFS,
    **SAMPLE_IMAGES,
    **SAMPLE_CODE,
    **SAMPLE_STRUCTURED_DATA,
    **SAMPLE_XML_DOCUMENTS,
}

# Sample search results
SAMPLE_SEARCH_RESULTS: Dict[str, List[SearchResult]] = {
    "agent protocol": [
        SearchResult(
            title="Agent Communication Protocols",
            snippet="Overview of standard protocols for agent communication...",
            url="https://example.com/agent-protocols",
        ),
        SearchResult(
            title="Document Service API: Model Context Protocol",
            snippet="Standardized protocol for LLM context management...",
            url="https://example.com/protocol",
        ),
    ],
    "a2a messaging": [
        SearchResult(
            title="Agent-to-Agent (A2A) Messaging",
            snippet="Framework for enabling efficient agent collaboration...",
            url="https://example.com/a2a-messaging",
        ),
    ],
}


class ServerConfig(BaseModel):
    """Configuration for the Document Service API."""
    
    latency_min_ms: int = 0
    latency_max_ms: int = 500
    error_rate: float = 0.0  # Between 0.0 and 1.0


# Dependencies
def get_llm_service():
    """Get the LLM service."""
    return LlmService()


class DocumentServiceAPI:
    """Document Service API with configurable latency and error injection."""
    
    def __init__(self) -> None:
        self.app = FastAPI(title="Document Service API")
        self.config = ServerConfig()
        self.llm_service = LlmService()
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Set up API routes."""
        
        @self.app.get("/config", response_model=ServerConfig)
        async def get_config() -> ServerConfig:
            return self.config
        
        @self.app.post("/config", response_model=ServerConfig)
        async def update_config(config: ServerConfig) -> ServerConfig:
            self.config = config
            return self.config
            
        @self.app.get("/api/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "ok"}
            
        @self.app.post(
            "/llm/generate",
            response_model=LlmResponse,
            responses={500: {"model": McpError}},
        )
        async def generate_text(request: LlmRequest) -> LlmResponse:
            """Generate text using the configured LLM provider."""
            await self._simulate_conditions()
            
            try:
                # Use the appropriate LLM service based on the request
                response = await self.llm_service.generate(request)
                return response
            except Exception as e:
                logging.error(f"Error generating text with LLM: {e}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"LLM generation failed: {str(e)}"
                )
        
        @self.app.get(
            "/jira/ticket/{ticket_id}",
            response_model=JiraTicket,
            responses={500: {"model": McpError}},
        )
        async def fetch_ticket(ticket_id: str) -> JiraTicket:
            await self._simulate_conditions()
            
            if ticket_id not in SAMPLE_JIRA_TICKETS:
                raise HTTPException(
                    status_code=404, detail=f"Ticket {ticket_id} not found"
                )
            
            return SAMPLE_JIRA_TICKETS[ticket_id]
        
        @self.app.get(
            "/documents",
            response_model=List[Document],
            responses={500: {"model": McpError}},
        )
        async def list_documents(doc_type: Optional[str] = None) -> List[Document]:
            """Get a list of all available documents, optionally filtered by type."""
            await self._simulate_conditions()
            
            # Filter by document type if provided
            if doc_type:
                documents = [doc for doc in DOCUMENT_STORE.values() if doc.doc_type == doc_type]
            else:
                documents = list(DOCUMENT_STORE.values())
            
            # Return document metadata only, not full content
            return documents
        
        @self.app.get(
            "/documents/{doc_id}",
            response_model=Document,
            responses={500: {"model": McpError}},
        )
        async def get_document(doc_id: str) -> Document:
            """Get a document by ID, returns the appropriate document type."""
            await self._simulate_conditions()
            
            if doc_id not in DOCUMENT_STORE:
                raise HTTPException(
                    status_code=404, detail=f"Document {doc_id} not found"
                )
            
            return DOCUMENT_STORE[doc_id]
        
        # Legacy endpoint for backward compatibility
        @self.app.get(
            "/docs/{doc_id}",
            response_model=DocumentContent,
            responses={500: {"model": McpError}},
        )
        async def get_doc(doc_id: str) -> DocumentContent:
            await self._simulate_conditions()
            
            if doc_id not in SAMPLE_DOCS:
                raise HTTPException(
                    status_code=404, detail=f"Document {doc_id} not found"
                )
            
            return SAMPLE_DOCS[doc_id]
        
        # Legacy endpoint for backward compatibility
        @self.app.get(
            "/pdf/{pdf_id}",
            response_model=PdfDocument,
            responses={500: {"model": McpError}},
        )
        async def get_pdf(pdf_id: str) -> PdfDocument:
            await self._simulate_conditions()
            
            if pdf_id not in SAMPLE_PDFS:
                raise HTTPException(
                    status_code=404, detail=f"PDF {pdf_id} not found"
                )
            
            return SAMPLE_PDFS[pdf_id]
        
        @self.app.get(
            "/search",
            response_model=SearchResults,
            responses={500: {"model": McpError}},
        )
        async def search_web(query: str = Query(...)) -> SearchResults:
            await self._simulate_conditions()
            
            # Very simple search - just match query against keys in sample data
            results: List[SearchResult] = []
            for key, search_results in SAMPLE_SEARCH_RESULTS.items():
                if query.lower() in key.lower():
                    results.extend(search_results)
            
            return SearchResults(results=results)
        
        @self.app.get(
            "/documents/{doc_id}/xml",
            response_model=XmlDocument,
            responses={500: {"model": McpError}},
        )
        async def get_xml_document(doc_id: str) -> XmlDocument:
            """Get an XML document by ID."""
            await self._simulate_conditions()
            
            if doc_id not in SAMPLE_XML_DOCUMENTS:
                raise HTTPException(
                    status_code=404, detail=f"XML document {doc_id} not found"
                )
            
            return SAMPLE_XML_DOCUMENTS[doc_id]
        
        @self.app.get(
            "/documents/{doc_id}/xml/content",
            response_model=str,
            responses={500: {"model": McpError}},
        )
        async def get_xml_content(doc_id: str) -> str:
            """Get raw XML content for a document."""
            await self._simulate_conditions()
            
            if doc_id not in SAMPLE_XML_DOCUMENTS:
                raise HTTPException(
                    status_code=404, detail=f"XML document {doc_id} not found"
                )
            
            return SAMPLE_XML_DOCUMENTS[doc_id].content
        
        @self.app.get(
            "/documents/{doc_id}/xml/nodes",
            response_model=List[XmlNode],
            responses={500: {"model": McpError}},
        )
        async def get_xml_researchable_nodes(doc_id: str) -> List[XmlNode]:
            """Get researchable nodes for an XML document."""
            await self._simulate_conditions()
            
            if doc_id not in SAMPLE_XML_DOCUMENTS:
                raise HTTPException(
                    status_code=404, detail=f"XML document {doc_id} not found"
                )
            
            return SAMPLE_XML_DOCUMENTS[doc_id].researchable_nodes
        
        @self.app.post(
            "/xml/upload",
            response_model=XmlDocument,
            responses={500: {"model": McpError}},
        )
        async def upload_xml(
            xml_content: str = Body(..., description="Raw XML content"),
            title: str = Body(..., description="Document title")
        ) -> XmlDocument:
            """Upload a new XML document."""
            await self._simulate_conditions()
            
            try:
                # Process the XML content
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
                    logging.error(f"Error parsing XML: {e}")
                
                # Generate a new document ID
                doc_id = f"xml{len(SAMPLE_XML_DOCUMENTS) + 1}"
                
                # Identify researchable nodes
                researchable_nodes = identify_researchable_nodes(xml_content)
                
                # Create the XML document
                now = datetime.datetime.utcnow().isoformat()
                new_doc = XmlDocument(
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
                
                # Add to the document store (in a real system, this would persist to a database)
                SAMPLE_XML_DOCUMENTS[doc_id] = new_doc
                DOCUMENT_STORE[doc_id] = new_doc
                
                return new_doc
            except Exception as e:
                logging.error(f"Error uploading XML: {e}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to process XML content: {str(e)}"
                )
    
    async def _simulate_conditions(self) -> None:
        """Simulate latency and random errors based on configuration."""
        # Simulate latency
        if self.config.latency_max_ms > 0:
            delay_ms = random.randint(
                self.config.latency_min_ms, self.config.latency_max_ms
            )
            await asyncio.sleep(delay_ms / 1000.0)
        
        # Simulate errors
        if self.config.error_rate > 0 and random.random() < self.config.error_rate:
            raise HTTPException(
                status_code=500, detail="Simulated server error"
            )
    


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        FastAPI: The configured FastAPI application
    """
    server = DocumentServiceAPI()
    
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