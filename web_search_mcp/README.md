# Web Search MCP Server

A Model Context Protocol (MCP) server for integrating web search capabilities into Agent Provocateur, with support for multiple search providers.

## Features

- **Multiple Provider Support**: Currently implements Brave Search, Google Search, and Bing Search
- **Web Search**: General queries with pagination and content filtering
- **Local Search**: Business and location searches with detailed information (Brave provider only)
- **Caching**: In-memory caching to reduce API calls
- **Rate Limiting**: Configurable rate limits to control API usage

## Prerequisites

- Node.js 18+ (for development)
- Podman or Docker (for containerized deployment)
- Search provider API keys:
  - [Brave Search API](https://brave.com/search/api/) (required for default setup)
  - Google Custom Search (optional)
  - Bing Search API (optional)

## Quick Start

### Development Setup

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd web_search_mcp
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   # Edit .env to add your API keys
   ```

4. Build the TypeScript code:
   ```bash
   npm run build
   ```

5. Run the tests:
   ```bash
   npm test
   ```

6. Start the server in development mode:
   ```bash
   npm run dev
   ```

### Containerized Deployment

1. Quick start (one command):
   ```bash
   # Set up and start the server in one command
   ./scripts/start.sh
   ```

2. Build the container image:
   ```bash
   # Using the build script
   ./scripts/build.sh
   ```

3. Run the container:
   ```bash
   # Using the run script (requires .env file)
   ./scripts/run.sh
   ```

4. Run tests:
   ```bash
   # Run all unit tests and check integration test availability
   ./scripts/run_tests.sh
   ```

5. Manual operation:
   ```bash
   # Build manually
   podman build -t agent-provocateur/web-search-mcp:latest .
   
   # Run manually
   podman run --rm -i \
     -e BRAVE_API_KEY=your_brave_api_key \
     agent-provocateur/web-search-mcp:latest
   ```

## Configuration

The server is configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_SEARCH_PROVIDER` | Default search provider to use | `brave` |
| `ENABLE_CACHE` | Enable result caching | `true` |
| `CACHE_TTL_SECONDS` | Seconds to cache results | `3600` |
| `RATE_LIMIT_PER_SECOND` | Maximum requests per second | `1` |
| `RATE_LIMIT_PER_DAY` | Maximum requests per day | `1000` |
| `BRAVE_API_KEY` | Brave Search API key | (required) |
| `GOOGLE_API_KEY` | Google API key (optional) | |
| `GOOGLE_SEARCH_CX` | Google Custom Search ID (optional) | |
| `BING_API_KEY` | Bing Search API key (optional) | |

## Integration with Agent Provocateur

To integrate this MCP server with Agent Provocateur, follow these steps:

1. Build and prepare the MCP server container.

2. Configure Agent Provocateur to use the MCP server:
   ```python
   # In your Agent Provocateur code
   async def on_startup(self):
       """Initialize the web search agent."""
       self.logger.info("Starting Web Search agent...")
       
       # Initialize MCP client for web search
       self.search_mcp_client = await self.get_mcp_client("web-search")
   ```

3. Update your agent's handlers to use the MCP client:
   ```python
   async def handle_search(self, task_request: TaskRequest):
       query = task_request.payload.get("query")
       if not query:
           return {"error": "Missing query parameter"}
       
       # Call the MCP tool
       tool_result = await self.search_mcp_client.call_tool(
           "brave_web_search",
           {"query": query, "count": 5}
       )
       
       # Process and return the results
       return {
           "query": query,
           "results": tool_result,
           "status": "completed"
       }
   ```

## Available Tools

### Web Search

- **Tool name**: `{provider}_web_search` (e.g., `brave_web_search`)
- **Parameters**:
  - `query` (string, required): Search query
  - `count` (number, optional): Number of results (default: 10, max: 20)
  - `offset` (number, optional): Pagination offset (default: 0)

### Local Search

- **Tool name**: `{provider}_local_search` (e.g., `brave_local_search`)
- **Parameters**:
  - `query` (string, required): Local search query (e.g., "pizza near Central Park")
  - `count` (number, optional): Number of results (default: 5, max: 20)

## Extending with Additional Providers

To add a new search provider:

1. Create a new file in `src/providers/` implementing the `SearchProvider` interface.
2. Update the `SearchProviderFactory` to initialize the new provider.
3. Add environment variable handling in `config.ts`.
4. Update documentation and tests.

## Testing

Run the test suite:

```bash
# Run tests once
npm test

# Run tests in watch mode
npm run test:watch
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure they pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.