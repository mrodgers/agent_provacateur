# Web Search Integration

This document explains the integration between Agent Provocateur and the Web Search MCP server for providing comprehensive web search capabilities with robust source attribution.

## Overview

The web search integration consists of:

1. A standalone **Web Search MCP Server** that interfaces with multiple search providers (Brave, Google, Bing)
2. The **WebSearchAgent** class in Agent Provocateur that communicates with the MCP server
3. Integration with the shared **service management infrastructure** for easy deployment

This integration enables agents to perform web searches with full source attribution, tracking confidence levels, citation information, and metadata for each search result.

## Architecture

```
┌────────────────────┐      ┌────────────────────┐      ┌────────────────────┐
│                    │      │                    │      │                    │
│  Agent Provocateur │      │   Web Search MCP   │      │   Search Provider  │
│  (WebSearchAgent)  │◄────►│      Server        │◄────►│    (Brave, etc.)   │
│                    │      │                    │      │                    │
└────────────────────┘      └────────────────────┘      └────────────────────┘
```

### Components

#### 1. Web Search MCP Server

The Web Search MCP server is a standalone service that:

- Provides a Model Context Protocol (MCP) interface for web search
- Supports multiple search providers (Brave, Google, Bing)
- Handles API rate limiting and result caching
- Formats search results in a standardized way
- Runs as a containerized service via podman or docker

The server is implemented in TypeScript/Node.js and follows the MCP specification.

#### 2. WebSearchAgent

The WebSearchAgent class in Agent Provocateur:

- Communicates with the Web Search MCP server
- Processes search results and creates Source objects
- Implements comprehensive source attribution
- Handles different search-related tasks (general search, entity research, content fetch)
- Provides confidence scoring for search results

#### 3. Service Management

The integration includes scripts for:

- Starting/stopping the Web Search MCP server
- Testing the web search functionality
- Managing dependencies and configuration

## Usage

### Starting the Web Search MCP Server

```bash
# Start as a standalone service
./scripts/start_ap.sh start web_search_mcp

# Start alongside other services
./scripts/start_ap.sh start mcp_server web_search_mcp frontend
```

### Testing Web Search

```bash
# Run a simple test search
./scripts/ap.sh web-search --query "climate change"

# Specify search provider
./scripts/ap.sh web-search --query "artificial intelligence" --provider google

# Limit number of results
./scripts/ap.sh web-search --query "latest research" --max-results 3
```

### Programmatic Usage

```python
from agent_provocateur.web_search_agent import WebSearchAgent
from agent_provocateur.a2a_models import TaskRequest

async def search_example():
    # Create agent instance
    agent = WebSearchAgent(agent_id="web-search-agent")
    
    # Initialize the agent
    await agent.start()
    
    try:
        # Create a search task request
        task_request = TaskRequest(
            task_id="search-task-1",
            intent="search",
            payload={
                "query": "climate change",
                "max_results": 5
            },
            source_agent="research-agent",
            target_agent="web-search-agent"
        )
        
        # Perform the search
        result = await agent.handle_task_request(task_request)
        
        # Process the results with sources
        print(f"Found {result['result_count']} results")
        for item in result['results']:
            print(f"- {item['title']}")
            print(f"  URL: {item['url']}")
            print(f"  Confidence: {item['confidence']}")
            
        # Access source information
        for source in result['sources']:
            print(f"Source: {source['title']}")
            print(f"Citation: {source['citation']}")
    
    finally:
        # Clean up
        await agent.stop()
```

## Configuration

### Environment Variables

The following environment variables can be used to configure the web search functionality:

| Variable | Description | Default |
| --- | --- | --- |
| `DEFAULT_SEARCH_PROVIDER` | Default search provider | `"brave"` |
| `BRAVE_API_KEY` | Brave Search API key | - |
| `GOOGLE_API_KEY` | Google Search API key | - |
| `GOOGLE_SEARCH_CX` | Google Custom Search ID | - |
| `BING_API_KEY` | Bing Search API key | - |

### Agent Configuration

The WebSearchAgent has the following configuration options:

```python
self.search_config = {
    "max_results": 5,           # Default max results per search
    "default_confidence": 0.7,  # Default confidence for sources
    "external_search_enabled": True,
    "search_providers": ["brave", "google", "bing"],
    "base_confidence": 0.85,    # Starting confidence score
    "confidence_decay": 0.05,   # Decay per result rank
    "min_confidence": 0.3,      # Minimum confidence score
    "preferred_provider": os.getenv("DEFAULT_SEARCH_PROVIDER", "brave")
}
```

## Source Attribution

Each search result includes comprehensive source attribution:

- Unique source ID
- Source type (WEB, DOCUMENT, etc.)
- Title and URL
- Retrieval timestamp
- Confidence score (based on result ranking)
- Properly formatted citation
- Additional metadata (provider, rank, etc.)

This information is stored in the `Source` objects returned with search results, enabling transparent attribution throughout the agent system.

## Available APIs

The WebSearchAgent supports the following intents:

| Intent | Description | Required Parameters |
| --- | --- | --- |
| `search` | Perform a web search | `query` |
| `fetch_content` | Fetch content from a URL | `url` |
| `research_entity` | Research an entity | `entity` |

Each API returns results with comprehensive source attribution.

## Advanced Usage

### Multiple Provider Support

The WebSearchAgent can be configured to use different search providers:

```python
# Set preferred provider
agent.search_config["preferred_provider"] = "google"

# Override preferred provider for a specific request
task_request.payload["provider"] = "bing"
```

### Confidence Scoring

Search results include confidence scores based on:

1. The rank of the result (higher ranks = higher confidence)
2. The search provider used
3. Configurable base confidence and decay values

## Related Documentation

- [Source Attribution Guide](../guides/source_attribution.md)
- [Brave Search API](./brave_web_search.md)
- [Web Search MCP Server Implementation](../../web_search_mcp/README.md)