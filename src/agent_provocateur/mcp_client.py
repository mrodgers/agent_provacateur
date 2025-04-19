import asyncio
from typing import Any, Dict, List, Optional

import httpx

from agent_provocateur.models import (
    DocumentContent,
    JiraTicket,
    LlmRequest,
    LlmResponse,
    PdfDocument,
    SearchResult,
    SearchResults,
)


class McpClient:
    """Client SDK for interacting with the MCP server."""
    
    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        """Initialize the MCP client.
        
        Args:
            base_url: The base URL of the MCP server
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=10.0)
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def fetch_ticket(self, ticket_id: str) -> JiraTicket:
        """Fetch a JIRA ticket by ID.
        
        Args:
            ticket_id: The ID of the ticket to fetch
            
        Returns:
            JiraTicket: The ticket data
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.get(f"/jira/ticket/{ticket_id}")
        response.raise_for_status()
        return JiraTicket(**response.json())
    
    async def get_doc(self, doc_id: str) -> DocumentContent:
        """Fetch a document by ID.
        
        Args:
            doc_id: The ID of the document to fetch
            
        Returns:
            DocumentContent: The document content
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.get(f"/docs/{doc_id}")
        response.raise_for_status()
        return DocumentContent(**response.json())
    
    async def get_pdf(self, pdf_id: str) -> PdfDocument:
        """Fetch a PDF document by ID.
        
        Args:
            pdf_id: The ID of the PDF to fetch
            
        Returns:
            PdfDocument: The PDF document
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.get(f"/pdf/{pdf_id}")
        response.raise_for_status()
        return PdfDocument(**response.json())
    
    async def search_web(self, query: str) -> List[SearchResult]:
        """Search the web with the given query.
        
        Args:
            query: The search query
            
        Returns:
            List[SearchResult]: List of search results
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.get("/search", params={"query": query})
        response.raise_for_status()
        results = SearchResults(**response.json())
        return results.results
        
    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> LlmResponse:
        """Generate text using the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            system_prompt: Optional system prompt
            context: Optional context data
            
        Returns:
            LlmResponse: The generated text response
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        request = LlmRequest(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            context=context,
        )
        response = await self.client.post("/llm/generate", json=request.dict())
        response.raise_for_status()
        return LlmResponse(**response.json())
    
    async def update_server_config(
        self,
        latency_min_ms: Optional[int] = None,
        latency_max_ms: Optional[int] = None,
        error_rate: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Update the server configuration.
        
        Args:
            latency_min_ms: Minimum latency in milliseconds
            latency_max_ms: Maximum latency in milliseconds
            error_rate: Rate of simulated errors (0.0 to 1.0)
            
        Returns:
            Dict: Updated server configuration
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        # Get current config
        response = await self.client.get("/config")
        response.raise_for_status()
        config = response.json()
        
        # Update with provided values
        if latency_min_ms is not None:
            config["latency_min_ms"] = latency_min_ms
        if latency_max_ms is not None:
            config["latency_max_ms"] = latency_max_ms
        if error_rate is not None:
            config["error_rate"] = error_rate
        
        # Send updated config
        response = await self.client.post("/config", json=config)
        response.raise_for_status()
        result: Dict[str, Any] = response.json()
        return result


# Synchronous interface for simpler usage
class SyncMcpClient:
    """Synchronous wrapper for the MCP client."""
    
    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        """Initialize the synchronous MCP client.
        
        Args:
            base_url: The base URL of the MCP server
        """
        self.async_client = McpClient(base_url)
    
    def __enter__(self) -> "SyncMcpClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with client cleanup."""
        asyncio.run(self.async_client.close())
    
    def fetch_ticket(self, ticket_id: str) -> JiraTicket:
        """Fetch a JIRA ticket synchronously."""
        return asyncio.run(self.async_client.fetch_ticket(ticket_id))
    
    def get_doc(self, doc_id: str) -> DocumentContent:
        """Fetch a document synchronously."""
        return asyncio.run(self.async_client.get_doc(doc_id))
    
    def get_pdf(self, pdf_id: str) -> PdfDocument:
        """Fetch a PDF document synchronously."""
        return asyncio.run(self.async_client.get_pdf(pdf_id))
    
    def search_web(self, query: str) -> List[SearchResult]:
        """Search the web synchronously."""
        return asyncio.run(self.async_client.search_web(query))
        
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> LlmResponse:
        """Generate text using the LLM synchronously."""
        return asyncio.run(
            self.async_client.generate_text(
                prompt, temperature, max_tokens, system_prompt, context
            )
        )
    
    def update_server_config(
        self,
        latency_min_ms: Optional[int] = None,
        latency_max_ms: Optional[int] = None,
        error_rate: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Update the server configuration synchronously."""
        return asyncio.run(
            self.async_client.update_server_config(
                latency_min_ms, latency_max_ms, error_rate
            )
        )