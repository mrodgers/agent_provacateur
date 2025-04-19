import asyncio
import random
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from agent_provocateur.models import (
    DocumentContent,
    JiraTicket,
    LlmRequest,
    LlmResponse,
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
            
        @self.app.post(
            "/llm/generate",
            response_model=LlmResponse,
            responses={500: {"model": McpError}},
        )
        async def generate_text(request: LlmRequest) -> LlmResponse:
            """Generate text using a simulated LLM."""
            await self._simulate_conditions()
            
            # Mock LLM response generation
            prompt = request.prompt
            context = request.context or {}
            
            # Generate different responses based on prompt and context
            if "decision" in prompt.lower():
                response_text = self._generate_decision_response(prompt, context)
            elif "plan" in prompt.lower():
                response_text = self._generate_planning_response(prompt, context)
            elif "analyze" in prompt.lower() or "analysis" in prompt.lower():
                response_text = self._generate_analysis_response(prompt, context)
            else:
                response_text = self._generate_generic_response(prompt, context)
            
            # Mock token usage
            prompt_tokens = len(prompt.split())
            completion_tokens = len(response_text.split())
            
            return LlmResponse(
                text=response_text,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
                model="mock-llm-agent-v1",
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
    
    def _generate_decision_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate a decision-making response."""
        if "prioritize" in prompt.lower():
            return """Based on the provided information, I recommend prioritizing Task B (Data Pipeline Enhancement) for the following reasons:

1. Highest Impact: This task addresses critical data flow issues affecting multiple teams
2. Time Sensitivity: The current issues are causing daily operational problems
3. Prerequisites: Completing this will unblock several dependent tasks
4. Resource Availability: The required expertise is currently available

The second priority should be Task A (API Development), followed by Task C (Documentation Update)."""
        else:
            return """After analyzing the situation, I recommend proceeding with Option 2: Refactor the existing codebase.

This approach offers the best balance of immediate benefits and long-term sustainability:
- Addresses current performance bottlenecks
- Maintains compatibility with existing integrations
- Requires 40% less development time than a complete rewrite
- Enables incremental improvements while maintaining system availability

Key implementation steps should include modularizing the core components, introducing a comprehensive test suite, and establishing clear API boundaries."""
    
    def _generate_planning_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate a planning response."""
        return """## Implementation Plan

### Phase 1: Setup & Foundation (Week 1-2)
- Configure development environment with required dependencies
- Set up CI/CD pipeline with automated testing
- Establish code quality standards and linting rules
- Create basic project structure and architecture documentation

### Phase 2: Core Implementation (Week 3-5)
- Develop data models and schemas
- Implement API endpoints with OpenAPI documentation
- Create client SDK for easy integration
- Develop background processing service for async tasks

### Phase 3: Integration & Testing (Week 6-7)
- Integrate with external systems (auth, storage, analytics)
- Implement comprehensive test suite (unit, integration, load)
- Conduct security audit and performance testing
- Prepare deployment scripts and infrastructure templates

### Phase 4: Finalization & Deployment (Week 8)
- Conduct final QA and regression testing
- Prepare user documentation and examples
- Deploy to staging environment for stakeholder review
- Deploy to production with monitoring and rollback plan"""
    
    def _generate_analysis_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate an analysis response."""
        ticket_context = context.get("ticket", {})
        if ticket_context:
            return f"""## Analysis of Ticket {ticket_context.get('id', 'Unknown')}

The ticket "{ticket_context.get('summary', 'Unknown')}" requires attention to several aspects:

1. **Current Status**: {ticket_context.get('status', 'Unknown')}
2. **Primary Issues**:
   - The system is experiencing intermittent connection failures
   - Performance degradation during peak usage hours
   - Configuration inconsistencies between environments

3. **Root Cause Analysis**:
   - Connection failures appear to be related to connection pool exhaustion
   - Performance issues correlate with inefficient database queries
   - Configuration drift resulted from manual environment changes

4. **Recommended Actions**:
   - Implement connection pool monitoring and auto-scaling
   - Optimize the identified inefficient queries with proper indexing
   - Deploy configuration as code to prevent future drift
   - Add automated testing to catch these issues earlier

5. **Risk Assessment**:
   - Medium priority issue affecting specific user workflows
   - No data integrity concerns identified
   - Estimated effort: 2-3 developer days"""
        else:
            return """## Performance Analysis

The system analysis reveals several key metrics and bottlenecks:

1. **Response Time**:
   - 95th percentile: 870ms (exceeds target of 500ms)
   - Median: 320ms (within acceptable range)
   - Slowest endpoints: /api/reports and /api/search

2. **Resource Utilization**:
   - CPU: 78% average during peak hours
   - Memory: 85% utilization with occasional spikes to 92%
   - Database connections: Reaching pool limits (90-100%)

3. **Bottlenecks Identified**:
   - Database query optimization needed for reporting features
   - Connection pooling configuration requires adjustment
   - Caching strategy insufficient for repetitive queries
   - Background task scheduling causing CPU spikes

4. **Improvement Recommendations**:
   - Implement query optimization and indexing for reporting endpoints
   - Increase connection pool size by 25% and add monitoring
   - Add Redis cache layer for frequently accessed data
   - Reschedule background tasks to distribute load more evenly"""
    
    def _generate_generic_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate a generic response."""
        return """Thank you for your query. I've processed the information and have the following insights to share:

The system appears to be functioning within normal parameters, though there are opportunities for improvement in several areas. Based on the current configuration and usage patterns, I'd recommend reviewing the resource allocation and optimization settings.

Key points to consider:
1. Current utilization shows moderate efficiency with room for enhancement
2. The implementation follows standard patterns but could benefit from updates
3. Documentation is comprehensive but would benefit from examples

Let me know if you need more specific information about any aspect of the system, and I'd be happy to provide a more targeted analysis or recommendation."""


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        FastAPI: The configured FastAPI application
    """
    server = McpServer()
    return server.app