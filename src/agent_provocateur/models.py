from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class LlmRequest(BaseModel):
    """Model for LLM request."""
    
    prompt: str = Field(..., description="The prompt to send to the LLM")
    temperature: float = Field(0.7, description="Temperature for generation (0.0-1.0)")
    max_tokens: int = Field(1000, description="Maximum number of tokens to generate")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context data")


class LlmResponse(BaseModel):
    """Model for LLM response."""
    
    text: str = Field(..., description="The generated text")
    usage: Dict[str, int] = Field(..., description="Token usage statistics")
    model: str = Field(..., description="Model used for generation")


class JiraTicket(BaseModel):
    """Model for JIRA ticket data."""
    
    id: str
    status: str
    assignee: Optional[str] = None
    summary: str


class DocumentContent(BaseModel):
    """Model for document content."""
    
    doc_id: str
    markdown: str
    html: Optional[str] = None


class PdfPage(BaseModel):
    """Model for a page in a PDF document."""
    
    text: str
    page_number: int


class PdfDocument(BaseModel):
    """Model for PDF document content."""
    
    url: str
    pages: List[PdfPage]


class SearchResult(BaseModel):
    """Model for web search result."""
    
    title: str
    snippet: str
    url: str


class SearchResults(BaseModel):
    """Model for web search results."""
    
    results: List[SearchResult]


class McpError(BaseModel):
    """Model for MCP error response."""
    
    error: str
    status_code: int = 500
    detail: Optional[str] = None