import asyncio
import random
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from agent_provocateur.models import (
    DocumentContent,
    JiraTicket,
    McpError,
    PdfDocument,
    PdfPage,
    SearchResult,
    SearchResults,
)

# Sample data for mocking
SAMPLE_JIRA_TICKETS: Dict[str, JiraTicket] = {
    "AP-1": JiraTicket(
        id="AP-1",
        status="Open",
        assignee="jdoe",
        summary="Set up MCP server for agent testing",
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

SAMPLE_DOCS: Dict[str, DocumentContent] = {
    "doc1": DocumentContent(
        doc_id="doc1",
        markdown="# Agent System Design\n\nThis document outlines...",
        html="<h1>Agent System Design</h1><p>This document outlines...</p>",
    ),
    "doc2": DocumentContent(
        doc_id="doc2",
        markdown="# Implementation Guide\n\nFollow these steps...",
        html="<h1>Implementation Guide</h1><p>Follow these steps...</p>",
    ),
}

SAMPLE_PDFS: Dict[str, PdfDocument] = {
    "pdf1": PdfDocument(
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

SAMPLE_SEARCH_RESULTS: Dict[str, List[SearchResult]] = {
    "agent protocol": [
        SearchResult(
            title="Agent Communication Protocols",
            snippet="Overview of standard protocols for agent communication...",
            url="https://example.com/agent-protocols",
        ),
        SearchResult(
            title="MCP: Model Context Protocol",
            snippet="Standardized protocol for LLM context management...",
            url="https://example.com/mcp-protocol",
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
    """Configuration for the MCP Server."""
    
    latency_min_ms: int = 0
    latency_max_ms: int = 500
    error_rate: float = 0.0  # Between 0.0 and 1.0


class McpServer:
    """Mock MCP server with configurable latency and error injection."""
    
    def __init__(self) -> None:
        self.app = FastAPI(title="Mock MCP Server")
        self.config = ServerConfig()
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
    server = McpServer()
    return server.app