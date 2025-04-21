# GraphRAG MCP Server

The GraphRAG MCP (Microservice Communication Protocol) Server provides graph-based retrieval-augmented generation capabilities as a standalone service for the Agent Provocateur framework.

## Overview

The GraphRAG MCP Server exposes GraphRAG functionality through a RESTful API, allowing various agents to utilize knowledge graph-based source attribution and entity extraction without tight coupling to the implementation.

## Features

- Entity extraction from text
- Source indexing and retrieval
- Building attributed prompts
- Processing attributed responses
- Entity lookup and relationship querying
- Concept map generation
- Semantic search
- Schema management

## Architecture

The GraphRAG MCP Server follows a layered architecture:

1. **API Layer**: Exposes RESTful endpoints for GraphRAG functionality
2. **Service Layer**: Contains core GraphRAG logic
3. **Data Layer**: Manages connections to the vector database and knowledge graph storage
4. **Utility Layer**: Provides caching, rate limiting, and other cross-cutting concerns

## Installation

### Prerequisites

- Node.js 16+
- npm
- Vector database (optional for development)

### Setup

1. Clone the repository
2. Install dependencies

```bash
cd graphrag_mcp
npm install
```

3. Build the TypeScript code

```bash
npm run build
```

4. Configure environment variables (optional)

```bash
cp .env.example .env
# Edit .env file with your configuration
```

## Usage

### Starting the server

```bash
# Start with default configuration
npm start

# Or use the run script
./scripts/run.sh
```

### Stopping the server

```bash
# Use the stop script
./scripts/stop.sh
```

### Testing the server

```bash
# Run the test script
node scripts/test.js
```

## API Reference

For detailed API documentation, see [GraphRAG MCP API](../docs/api/graphrag_mcp_api.md).

## Integration

Agents can integrate with the GraphRAG MCP Server using the provided GraphRAG Client:

```python
from agent_provocateur.graphrag_client import GraphRAGClient

# Initialize the client
graphrag_client = GraphRAGClient(base_url="http://localhost:8083")

# Extract entities from text
entities = await graphrag_client.extract_entities("Climate change is a significant challenge.")

# Get sources for a query
sources = await graphrag_client.get_sources_for_query(
    "What are the effects of climate change?",
    focus_entities=["ent_a1b2c3"]
)
```

## Configuration

The GraphRAG MCP Server can be configured with the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8083` |
| `VECTOR_DB_URL` | URL of the vector database | `http://localhost:6333` |
| `MAX_CACHE_SIZE` | Maximum cache size (items) | `1000` |
| `CACHE_TTL` | Cache TTL (seconds) | `3600` |
| `MAX_RESULTS` | Default maximum results | `10` |
| `MIN_CONFIDENCE` | Default minimum confidence | `0.5` |
| `TRAVERSAL_DEPTH` | Default traversal depth | `2` |
| `RATE_LIMIT_WINDOW` | Rate limit window (ms) | `60000` |
| `RATE_LIMIT_MAX` | Max requests per window | `100` |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.