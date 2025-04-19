from typing import List, Optional
from pydantic import BaseModel


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