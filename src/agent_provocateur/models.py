from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
import datetime


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


# Base document type
class Document(BaseModel):
    """Base model for all document types."""
    
    doc_id: str = Field(..., description="Unique identifier for the document")
    doc_type: str = Field(..., description="Type of document")
    title: str = Field(..., description="Document title")
    created_at: str = Field(..., description="Document creation timestamp")
    updated_at: Optional[str] = Field(None, description="Document last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class JiraTicket(BaseModel):
    """Model for JIRA ticket data."""
    
    id: str
    status: str
    assignee: Optional[str] = None
    summary: str


class DocumentContent(Document):
    """Model for text document content."""
    
    markdown: str = Field(..., description="Markdown content of the document")
    html: Optional[str] = Field(None, description="HTML content of the document")
    doc_type: str = Field("text", const=True, description="Document type identifier")


class PdfPage(BaseModel):
    """Model for a page in a PDF document."""
    
    text: str
    page_number: int


class PdfDocument(Document):
    """Model for PDF document content."""
    
    url: str = Field(..., description="URL to the original PDF file")
    pages: List[PdfPage] = Field(..., description="List of PDF pages with extracted text")
    doc_type: str = Field("pdf", const=True, description="Document type identifier")


class ImageDocument(Document):
    """Model for image document content."""
    
    url: str = Field(..., description="URL to the image file")
    alt_text: str = Field("", description="Alternative text for the image")
    caption: Optional[str] = Field(None, description="Caption for the image")
    width: Optional[int] = Field(None, description="Width of the image in pixels")
    height: Optional[int] = Field(None, description="Height of the image in pixels")
    format: str = Field(..., description="Image format (png, jpg, etc.)")
    doc_type: str = Field("image", const=True, description="Document type identifier")


class CodeDocument(Document):
    """Model for code document content."""
    
    content: str = Field(..., description="Code content")
    language: str = Field(..., description="Programming language")
    line_count: int = Field(..., description="Number of lines in the code")
    doc_type: str = Field("code", const=True, description="Document type identifier")


class StructuredDataDocument(Document):
    """Model for structured data document content."""
    
    data: Dict[str, Any] = Field(..., description="Structured data content")
    schema_def: Optional[Dict[str, Any]] = Field(None, description="Schema definition for the data", alias="schema")
    format: str = Field(..., description="Data format (json, csv, etc.)")
    doc_type: str = Field("structured_data", const=True, description="Document type identifier")


class XmlNode(BaseModel):
    """Model for an XML node that needs verification."""
    
    xpath: str = Field(..., description="XPath to the node")
    element_name: str = Field(..., description="Name of the element")
    content: Optional[str] = Field(None, description="Text content of the node")
    attributes: Dict[str, str] = Field(default_factory=dict, description="Node attributes")
    verification_status: str = Field("pending", description="Verification status")
    verification_data: Dict[str, Any] = Field(default_factory=dict, description="Verification results")


class XmlDocument(Document):
    """Model for XML document content."""
    
    content: str = Field(..., description="Raw XML content")
    schema_url: Optional[str] = Field(None, description="URL to XML schema definition")
    root_element: str = Field(..., description="Name of the root element")
    namespaces: Dict[str, str] = Field(default_factory=dict, description="XML namespaces")
    researchable_nodes: List[XmlNode] = Field(default_factory=list, description="Nodes requiring verification")
    doc_type: str = Field("xml", const=True, description="Document type identifier")
    
    @validator('content')
    def validate_xml_content(cls, v):
        """Validate that the content is valid XML."""
        try:
            # Import here to avoid circular imports
            from defusedxml import ElementTree
            ElementTree.fromstring(v)
            return v
        except Exception as e:
            raise ValueError(f"Invalid XML content: {str(e)}")


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