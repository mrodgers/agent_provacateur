"""Web Search Agent for fetching and processing web content with robust source attribution via MCP."""

import os
import asyncio
import logging
import uuid
import datetime
from typing import Any, Dict, List, Optional, Tuple

from agent_provocateur.agent_base import BaseAgent
from agent_provocateur.a2a_models import TaskRequest, TaskStatus
from agent_provocateur.models import SearchResult, SearchResults, Source, SourceType
from agent_provocateur.mcp_client import McpClient

logger = logging.getLogger(__name__)

class WebSearchAgent(BaseAgent):
    """
    Agent for web search and content retrieval with comprehensive source attribution.
    Uses the Web Search MCP server for search capabilities.
    """
    
    async def on_startup(self) -> None:
        """Initialize the web search agent."""
        self.logger.info("Starting Web Search agent...")
        
        # Initialize search configuration
        self.search_config = {
            "max_results": 5,
            "default_confidence": 0.7,
            "external_search_enabled": True,
            "search_providers": ["brave", "google", "bing"],
            "base_confidence": 0.85,
            "confidence_decay": 0.05,
            "min_confidence": 0.3,
            "preferred_provider": os.getenv("DEFAULT_SEARCH_PROVIDER", "brave")
        }
        
        # Initialize MCP client for web search
        self.search_mcp_client = McpClient("web-search")
        self.logger.info(f"Web Search MCP client initialized with preferred provider: {self.search_config['preferred_provider']}")
        
        # Log available tools from MCP
        try:
            tools = await self.search_mcp_client.list_tools()
            self.logger.info(f"Available search tools: {[tool.name for tool in tools]}")
        except Exception as e:
            self.logger.warning(f"Failed to list search tools: {e}")
    
    async def handle_task_request(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Process a task request sent to this agent.
        
        Args:
            task_request: The task request to process
            
        Returns:
            Dict with task result
        """
        self.logger.info(f"Processing task request: {task_request.intent}")
        
        # Route to appropriate handler based on intent
        if task_request.intent == "search":
            return await self.handle_search(task_request)
        elif task_request.intent == "fetch_content":
            return await self.handle_fetch_content(task_request)
        elif task_request.intent == "research_entity":
            return await self.handle_research_entity(task_request)
        else:
            self.logger.warning(f"Unknown intent: {task_request.intent}")
            return {
                "error": f"Unknown intent: {task_request.intent}",
                "status": "failed"
            }
    
    async def handle_search(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Handle a search task with comprehensive source attribution.
        Uses the MCP web search tool.
        
        Args:
            task_request: Task request with search query
            
        Returns:
            Dict with search results and sources
        """
        query = task_request.payload.get("query")
        max_results = task_request.payload.get("max_results", self.search_config["max_results"])
        
        if not query:
            return {
                "error": "Missing required parameter: query",
                "status": "failed"
            }
        
        try:
            # Use the preferred provider for search
            provider = self.search_config["preferred_provider"]
            tool_name = f"{provider}_web_search"
            
            self.logger.info(f"Searching with {tool_name}: {query}")
            
            # Call MCP tool to perform the search
            search_result = await self.search_mcp_client.call_tool(
                tool_name, 
                {
                    "query": query,
                    "count": max_results
                }
            )
            
            # Parse the search result text and create Source objects
            results_with_sources, sources = self._parse_search_results(
                search_result.content[0].text, 
                query,
                provider
            )
            
            return {
                "query": query,
                "results": results_with_sources,
                "result_count": len(results_with_sources),
                "sources": [s.dict() for s in sources],
                "status": "completed"
            }
        
        except Exception as e:
            self.logger.error(f"Error searching for {query}: {e}")
            return {
                "error": f"Search failed: {str(e)}",
                "query": query,
                "status": "failed"
            }
    
    async def handle_fetch_content(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Fetch content from a URL with source attribution.
        
        Args:
            task_request: Task request with URL to fetch
            
        Returns:
            Dict with content and source information
        """
        url = task_request.payload.get("url")
        
        if not url:
            return {
                "error": "Missing required parameter: url",
                "status": "failed"
            }
        
        try:
            # In a real implementation, we would fetch content from the URL
            # For now, we'll simulate fetching content
            self.logger.info(f"Fetching content from: {url}")
            
            # Extract domain from URL for better title
            domain = url.split("//")[-1].split("/")[0] if "//" in url else url.split("/")[0]
            title = f"Content from {domain}"
            
            # Simulate content retrieval
            content = f"Simulated content from {url}"
            
            # Create a proper source object
            source = self._create_source(
                title=title,
                source_type=SourceType.WEB,
                url=url,
                confidence=0.90,  # Direct content fetching has high confidence
                context={
                    "fetch_type": "direct",
                    "content_length": len(content),
                    "query": task_request.payload.get("query", "Direct URL fetch")
                }
            )
            
            return {
                "url": url,
                "content": content,
                "source": source.dict(),
                "sources": [source.dict()],  # For consistency with other endpoints
                "status": "completed"
            }
        
        except Exception as e:
            self.logger.error(f"Error fetching content from {url}: {e}")
            return {
                "error": f"Fetch failed: {str(e)}",
                "url": url,
                "status": "failed"
            }
    
    async def handle_research_entity(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Research an entity using web search and other sources with 
        comprehensive source attribution.
        
        Args:
            task_request: Task request with entity to research
            
        Returns:
            Dict with research results and sources
        """
        entity = task_request.payload.get("entity")
        max_results = task_request.payload.get("max_results", self.search_config["max_results"])
        include_structured_data = task_request.payload.get("include_structured_data", True)
        
        if not entity:
            return {
                "error": "Missing required parameter: entity",
                "status": "failed"
            }
        
        try:
            # Use the preferred provider for entity research
            provider = self.search_config["preferred_provider"]
            tool_name = f"{provider}_web_search"
            
            self.logger.info(f"Researching entity with {tool_name}: {entity}")
            
            # Call MCP tool to search for the entity
            search_result = await self.search_mcp_client.call_tool(
                tool_name, 
                {
                    "query": entity,
                    "count": max_results
                }
            )
            
            # Parse the search result text and create Source objects
            results_with_sources, sources = self._parse_search_results(
                search_result.content[0].text, 
                entity,
                provider
            )
            
            # Extract key information from search results
            # In a real implementation, this would involve more sophisticated processing
            definition = f"Generated definition of '{entity}' based on search results"
            
            # In a real implementation, you might generate a structured representation
            # of the entity based on the search results
            structured_data = None
            if include_structured_data:
                structured_data = {
                    "entity": entity,
                    "type": "unknown",  # Would be inferred from results
                    "properties": {},   # Would be extracted from results
                    "related_entities": []  # Would be extracted from results
                }
            
            # Create a unified set of sources for the research output
            # with additional metadata for how they were used
            research_sources = []
            for i, source in enumerate(sources):
                # Create a copy with updated metadata
                source_dict = source.dict()
                source_dict["usage"] = "entity_research"
                source_dict["relevance_rank"] = i + 1
                
                research_sources.append(source_dict)
            
            return {
                "entity": entity,
                "definition": definition,
                "results": results_with_sources,
                "sources": research_sources,
                "structured_data": structured_data,
                "research_timestamp": datetime.datetime.now().isoformat(),
                "status": "completed"
            }
        
        except Exception as e:
            self.logger.error(f"Error researching entity {entity}: {e}")
            return {
                "error": f"Research failed: {str(e)}",
                "entity": entity,
                "status": "failed"
            }
    
    def _parse_search_results(self, text: str, query: str, provider: str) -> Tuple[List[Dict[str, Any]], List[Source]]:
        """
        Parse search results from the text response and create Source objects.
        
        Args:
            text: The search result text from the MCP tool
            query: The original search query
            provider: The provider used for the search
            
        Returns:
            Tuple containing:
              - List of result dictionaries with source references
              - List of Source objects
        """
        results_with_sources = []
        sources = []
        
        # Get confidence parameters from config
        base_confidence = self.search_config["base_confidence"]
        confidence_decay = self.search_config["confidence_decay"]
        min_confidence = self.search_config["min_confidence"]
        
        # Simple parsing logic that looks for result sections in the response
        # A more robust implementation would use regex or custom parsing logic
        # based on the known output format of the MCP server
        result_sections = text.split('\n\n')
        
        for i, section in enumerate(result_sections):
            # Skip empty sections
            if not section.strip():
                continue
                
            # Try to extract title, snippet and URL
            lines = section.split('\n')
            
            # Simple parsing - assumes format: [n] Title\nSnippet\nURL: url
            title = ""
            snippet = ""
            url = ""
            
            if lines and lines[0].strip():
                # Extract title, removing [n] prefix if present
                if ']' in lines[0]:
                    title = lines[0].split(']', 1)[1].strip()
                else:
                    title = lines[0].strip()
                    
            # The middle lines are the snippet
            if len(lines) > 1:
                snippet_lines = []
                for line in lines[1:]:
                    if line.startswith('URL:'):
                        break
                    snippet_lines.append(line)
                snippet = '\n'.join(snippet_lines).strip()
                
            # The last line might be the URL
            for line in lines:
                if line.startswith('URL:'):
                    url = line[4:].strip()
                    break
            
            # Calculate confidence - higher ranked results get higher confidence
            confidence = max(min_confidence, base_confidence - (i * confidence_decay))
            
            # Create a proper Source object for this result
            source = self._create_source(
                title=title,
                source_type=SourceType.WEB,
                url=url,
                confidence=confidence,
                context={
                    "query": query,
                    "provider": provider,
                    "rank": i + 1,
                    "snippet": snippet
                }
            )
            
            # Add to sources list
            sources.append(source)
            
            # Create result dict with source reference
            result_dict = {
                "title": title,
                "snippet": snippet,
                "url": url,
                "rank": i + 1,
                "confidence": confidence,
                "source_id": source.source_id,
                "source_type": source.source_type.value
            }
            
            results_with_sources.append(result_dict)
        
        return results_with_sources, sources
    
    def _create_source(
        self,
        title: str,
        source_type: SourceType,
        url: Optional[str] = None,
        confidence: float = 0.5,
        context: Optional[Dict[str, Any]] = None
    ) -> Source:
        """
        Create a Source object with consistent formatting.
        
        Args:
            title: Title or name of the source
            source_type: Type of source (from SourceType enum)
            url: URL to the source (if applicable)
            confidence: Confidence score (0.0-1.0)
            context: Additional context for the source
            
        Returns:
            Source object
        """
        # Create a unique ID for this source
        source_id = str(uuid.uuid4())
        
        # Get the current timestamp
        now = datetime.datetime.now()
        
        # Create metadata with any additional context
        metadata = {}
        if context:
            metadata.update(context)
        
        # Generate an appropriate citation based on type
        if source_type == SourceType.WEB and url:
            domain = url.split("//")[-1].split("/")[0] if "//" in url else url.split("/")[0]
            citation = f"\"{title}\" {domain}. Retrieved on {now.strftime('%Y-%m-%d')}."
        else:
            citation = f"\"{title}\". Retrieved on {now.strftime('%Y-%m-%d')}."
        
        # Create and return the Source object
        return Source(
            source_id=source_id,
            source_type=source_type,
            title=title,
            url=url,
            retrieved_at=now,
            confidence=confidence,
            metadata=metadata,
            citation=citation
        )