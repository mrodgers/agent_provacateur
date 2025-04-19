from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field


class LlmMessage(BaseModel):
    """Model for a message in LLM conversation."""
    
    role: str = Field(..., description="Role of the message sender (system, user, assistant)")
    content: str = Field(..., description="Content of the message")


class LlmRequest(BaseModel):
    """Model for LLM request."""
    
    # Common fields across providers
    prompt: Optional[str] = Field(None, description="The prompt to send to the LLM")
    messages: Optional[List[LlmMessage]] = Field(None, description="Messages for chat-based LLMs")
    temperature: float = Field(0.7, description="Temperature for generation (0.0-1.0)")
    max_tokens: int = Field(1000, description="Maximum number of tokens to generate")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context data")
    
    # Provider selection
    provider: str = Field("mock", description="LLM provider to use (mock, ollama)")
    model: Optional[str] = Field(None, description="Model name to use (provider-specific)")
    stream: bool = Field(False, description="Whether to stream the response")


class LlmResponseUsage(BaseModel):
    """Model for token usage statistics."""
    
    prompt_tokens: int = Field(0, description="Number of tokens in the prompt")
    completion_tokens: int = Field(0, description="Number of tokens in the completion")
    total_tokens: int = Field(0, description="Total number of tokens used")


class LlmResponse(BaseModel):
    """Model for LLM response."""
    
    text: str = Field(..., description="The generated text")
    usage: LlmResponseUsage = Field(..., description="Token usage statistics")
    model: str = Field(..., description="Model used for generation")
    provider: str = Field(..., description="Provider used for generation")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")


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