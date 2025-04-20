import logging
from typing import Any, Dict, List, Optional

import httpx

from agent_provocateur.models import (
    Document,
    DocumentContent,
    JiraTicket,
    LlmRequest,
    LlmMessage,
    LlmResponse,
    PdfDocument,
    SearchResults,
    ImageDocument,
    CodeDocument,
    StructuredDataDocument,
    XmlDocument,
    XmlNode,
)
from agent_provocateur.metrics import (
    instrument_mcp_client,
    instrument_llm_client
)


class McpClient:
    """Client for interacting with the MCP server."""
    
    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        """Initialize the MCP client.
        
        Args:
            base_url: The base URL of the MCP server
        """
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
    
    @instrument_mcp_client
    async def fetch_ticket(self, ticket_id: str) -> JiraTicket:
        """Fetch a JIRA ticket.
        
        Args:
            ticket_id: The ticket ID
            
        Returns:
            JiraTicket: The ticket data
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/jira/ticket/{ticket_id}")
            response.raise_for_status()
            return JiraTicket(**response.json())
    
    @instrument_mcp_client
    async def get_doc(self, doc_id: str) -> DocumentContent:
        """Get a document.
        
        Args:
            doc_id: The document ID
            
        Returns:
            DocumentContent: The document content
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/docs/{doc_id}")
            response.raise_for_status()
            return DocumentContent(**response.json())
    
    @instrument_mcp_client
    async def get_pdf(self, pdf_id: str) -> PdfDocument:
        """Get a PDF document.
        
        Args:
            pdf_id: The PDF ID
            
        Returns:
            PdfDocument: The PDF document
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/pdf/{pdf_id}")
            response.raise_for_status()
            return PdfDocument(**response.json())
    
    @instrument_mcp_client
    async def search_web(self, query: str) -> List[Dict[str, str]]:
        """Search the web.
        
        Args:
            query: The search query
            
        Returns:
            List[Dict[str, str]]: The search results
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search", params={"query": query}
            )
            response.raise_for_status()
            search_results = SearchResults(**response.json())
            return [result.dict() for result in search_results.results]
    
    @instrument_llm_client
    async def generate_text(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        provider: str = "mock",
        model: Optional[str] = None,
        stream: bool = False,
    ) -> LlmResponse:
        """Generate text using the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            messages: Messages for chat-based LLMs
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            system_prompt: Optional system prompt
            context: Optional context data
            provider: LLM provider to use (mock, ollama)
            model: Model name to use (provider-specific)
            stream: Whether to stream the response
            
        Returns:
            LlmResponse: The generated text
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        # Convert messages to LlmMessage objects if provided
        processed_messages = None
        if messages:
            processed_messages = [
                LlmMessage(role=msg["role"], content=msg["content"]) for msg in messages
            ]
        
        # Create request
        request = LlmRequest(
            prompt=prompt,
            messages=processed_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            context=context,
            provider=provider,
            model=model,
            stream=stream,
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/llm/generate", json=request.dict(exclude_none=True)
            )
            response.raise_for_status()
            result = LlmResponse(**response.json())
            return result
    
    @instrument_mcp_client
    async def list_documents(self, doc_type: Optional[str] = None) -> List[Document]:
        """List all available documents, optionally filtered by type.
        
        Args:
            doc_type: Optional document type filter
            
        Returns:
            List[Document]: List of documents
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        params = {}
        if doc_type:
            params["doc_type"] = doc_type
            
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/documents", params=params)
            response.raise_for_status()
            
            # Parse response based on document types
            documents = []
            for doc_data in response.json():
                documents.append(self._create_document_from_data(doc_data))
                
            return documents
    
    @instrument_mcp_client
    async def get_xml_document(self, doc_id: str) -> XmlDocument:
        """Get an XML document by ID.
        
        Args:
            doc_id: The document ID
            
        Returns:
            XmlDocument: The XML document
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/documents/{doc_id}/xml")
            response.raise_for_status()
            return XmlDocument(**response.json())
    
    @instrument_mcp_client
    async def get_xml_content(self, doc_id: str) -> str:
        """Get raw XML content for a document.
        
        Args:
            doc_id: The document ID
            
        Returns:
            str: The raw XML content
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/documents/{doc_id}/xml/content")
            response.raise_for_status()
            return response.text
    
    @instrument_mcp_client
    async def get_xml_researchable_nodes(self, doc_id: str) -> List[XmlNode]:
        """Get researchable nodes for an XML document.
        
        Args:
            doc_id: The document ID
            
        Returns:
            List[XmlNode]: The list of researchable nodes
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/documents/{doc_id}/xml/nodes")
            response.raise_for_status()
            return [XmlNode(**node) for node in response.json()]
    
    @instrument_mcp_client
    async def upload_xml(self, xml_content: str, title: str) -> XmlDocument:
        """Upload a new XML document.
        
        Args:
            xml_content: The raw XML content
            title: The document title
            
        Returns:
            XmlDocument: The created XML document
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/xml/upload",
                json={"xml_content": xml_content, "title": title}
            )
            response.raise_for_status()
            return XmlDocument(**response.json())
    
    @instrument_mcp_client
    async def get_document(self, doc_id: str) -> Document:
        """Get a document by ID.
        
        Args:
            doc_id: The document ID
            
        Returns:
            Document: The document (specific subclass based on doc_type)
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/documents/{doc_id}")
            response.raise_for_status()
            
            return self._create_document_from_data(response.json())
    
    def _create_document_from_data(self, data: Dict[str, Any]) -> Document:
        """Create the appropriate document subclass based on doc_type.
        
        Args:
            data: The document data
            
        Returns:
            Document: The appropriate document subclass
        """
        # Extract basic document fields that are common to all types
        doc_type = data.get("doc_type", "")
        basic_fields = {
            "doc_id": data.get("doc_id", ""),
            "doc_type": doc_type,
            "title": data.get("title", ""),
            "created_at": data.get("created_at", ""),
            "updated_at": data.get("updated_at"),
            "metadata": data.get("metadata", {})
        }
        
        try:
            if doc_type == "text":
                return DocumentContent(
                    **basic_fields,
                    markdown=data.get("markdown", ""),
                    html=data.get("html")
                )
            elif doc_type == "pdf":
                return PdfDocument(
                    **basic_fields,
                    url=data.get("url", ""),
                    pages=data.get("pages", [])
                )
            elif doc_type == "image":
                return ImageDocument(
                    **basic_fields,
                    url=data.get("url", ""),
                    alt_text=data.get("alt_text", ""),
                    caption=data.get("caption"),
                    width=data.get("width"),
                    height=data.get("height"),
                    format=data.get("format", "unknown")
                )
            elif doc_type == "code":
                return CodeDocument(
                    **basic_fields,
                    content=data.get("content", ""),
                    language=data.get("language", ""),
                    line_count=data.get("line_count", 0)
                )
            elif doc_type == "structured_data":
                return StructuredDataDocument(
                    **basic_fields,
                    data=data.get("data", {}),
                    schema=data.get("schema_def"),  # Using 'schema' instead of 'schema_def'
                    format=data.get("format", "")
                )
            elif doc_type == "xml":
                return XmlDocument(
                    **basic_fields,
                    content=data.get("content", ""),
                    schema_url=data.get("schema_url"),
                    root_element=data.get("root_element", ""),
                    namespaces=data.get("namespaces", {}),
                    researchable_nodes=data.get("researchable_nodes", [])
                )
            else:
                # Default to base Document class if type is unknown
                return Document(**basic_fields)
        except Exception as e:
            self.logger.error(f"Error creating document from data: {e}")
            # Fall back to base Document
            return Document(**basic_fields)