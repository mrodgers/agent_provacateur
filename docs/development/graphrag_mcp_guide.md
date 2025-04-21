# GraphRAG MCP Server Guide

This guide explains how to use the GraphRAG MCP server implementation for enhanced source attribution in Agent Provocateur.

## Overview

The GraphRAG MCP server is a standalone microservice that provides graph-based retrieval-augmented generation capabilities. It's built using Node.js/TypeScript and exposes a RESTful API for agent integration.

## Architecture

The GraphRAG MCP server follows a microservice architecture:

```
┌─────────────────────────────────────────┐
│            Agent Provocateur            │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────┐    ┌───────────────┐ │
│  │   XmlAgent    │    │ WebSearchAgent│ │
│  └───────┬───────┘    └───────┬───────┘ │
│          │                    │         │
│  ┌───────▼───────────────────▼───────┐  │
│  │         GraphRAG Client           │  │
│  └───────────────┬───────────────────┘  │
│                  │                      │
└──────────────────┼──────────────────────┘
                   │
         ┌─────────▼───────────┐
         │  HTTP / REST API    │
         └─────────┬───────────┘
                   │
┌──────────────────┼──────────────────────┐
│                  │                      │
│  ┌───────────────▼───────────────────┐  │
│  │         GraphRAG MCP Server       │  │
│  ├───────────────────────────────────┤  │
│  │ ┌─────────────┐  ┌─────────────┐  │  │
│  │ │  API Layer  │  │Cache & Rate │  │  │
│  │ │             │  │  Limiting   │  │  │
│  │ └─────┬───────┘  └─────────────┘  │  │
│  │       │                           │  │
│  │ ┌─────▼───────┐                   │  │
│  │ │ GraphRAG    │                   │  │
│  │ │ Service     │                   │  │
│  │ └─────┬───────┘                   │  │
│  │       │                           │  │
│  │ ┌─────▼───────┐  ┌─────────────┐  │  │
│  │ │Vector DB    │  │Knowledge    │  │  │
│  │ │Integration  │  │Graph Store  │  │  │
│  │ └─────────────┘  └─────────────┘  │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│               GraphRAG MCP               │
└───────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Node.js 16+ (for GraphRAG MCP server)
- Python 3.9+ (for Agent Provocateur)
- Agent Provocateur framework

### Setup

1. The GraphRAG MCP server is included in the Agent Provocateur repository:

```
/graphrag_mcp/           # GraphRAG MCP server
  ├── src/               # TypeScript source code
  ├── scripts/           # Server management scripts
  ├── package.json       # Node.js dependencies
  └── README.md          # Server documentation
```

2. Install server dependencies:

```bash
cd graphrag_mcp
npm install
```

3. Build the TypeScript code:

```bash
npm run build
```

## Running the Server

### Using the Run Script

The easiest way to start the GraphRAG MCP server is using the provided script:

```bash
./scripts/run_graphrag_mcp.sh
```

This script will:
1. Start the GraphRAG MCP server on port 8083 (default)
2. Configure necessary environment variables
3. Test that the server is running correctly
4. Print usage instructions for integrating with Agent Provocateur

### Manual Start

If you prefer to start the server manually:

```bash
# Navigate to the GraphRAG MCP directory
cd graphrag_mcp

# Build the TypeScript code (if needed)
npm run build

# Start the server
node dist/index.js
```

### Docker Deployment

The GraphRAG MCP server can also be deployed using Docker:

```bash
# Build the Docker image
cd graphrag_mcp
docker build -t graphrag-mcp-server .

# Run the container
docker run -p 8083:8083 graphrag-mcp-server
```

Or using docker-compose:

```bash
# Start the GraphRAG MCP server with vector database
cd graphrag_mcp
docker-compose up -d
```

## Integration with Agent Provocateur

### Environment Variables

To integrate the GraphRAG MCP server with Agent Provocateur, set the following environment variables:

```bash
export GRAPHRAG_MCP_URL=http://localhost:8083
export AGENT_TYPE=xml_graphrag
```

### Using the GraphRAG Client

The `GraphRAGClient` class provides a Python interface to the GraphRAG MCP server:

```python
from agent_provocateur.graphrag_client import GraphRAGClient

# Initialize the client
client = GraphRAGClient(base_url="http://localhost:8083")

# Extract entities
entities = await client.extract_entities("Climate change is a significant challenge.")

# Get sources for a query
sources, prompt = await client.get_sources_for_query(
    "What are the effects of climate change?"
)

# Process an attributed response
result = await client.process_attributed_response(
    "Climate change is causing [SOURCE_1] sea levels to rise.",
    sources
)
```

### Using the XML GraphRAG Agent

The `XmlGraphRAGAgent` extends the standard `XmlAgent` with GraphRAG capabilities:

```python
from agent_provocateur.xml_graphrag_agent import XmlGraphRAGAgent

# Create an XML GraphRAG agent
agent = XmlGraphRAGAgent(
    agent_id="xml_graphrag_agent",
    agent_type="xml_graphrag",
    capabilities=["xml_verification"]
)
```

This agent will automatically use the GraphRAG MCP server for:
- Entity extraction from XML content
- Source attribution for XML nodes
- Processing attributed responses

## API Reference

The GraphRAG MCP server exposes the following API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/info` | GET | Get server information |
| `/api/tools/graphrag_index_source` | POST | Index a source in GraphRAG |
| `/api/tools/graphrag_extract_entities` | POST | Extract entities from text |
| `/api/tools/graphrag_query` | POST | Get sources for a query |
| `/api/tools/graphrag_entity_lookup` | POST | Look up entity information |
| `/api/tools/graphrag_concept_map` | POST | Generate a concept map |

For detailed API documentation, see [GraphRAG MCP API](../api/graphrag_mcp_api.md).

## Testing

### Unit Tests

To run the GraphRAG client unit tests:

```bash
python -m pytest tests/test_graphrag_client.py -v
```

### Integration Tests

To run the GraphRAG MCP integration tests (requires server to be running):

```bash
# Start the GraphRAG MCP server if not already running
./scripts/run_graphrag_mcp.sh

# Run integration tests
GRAPHRAG_MCP_TESTS=1 python -m pytest tests/test_graphrag_mcp_integration.py -v
```

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check Node.js version (should be 16+)
   - Verify TypeScript is built: `npm run build`
   - Check for port conflicts: `lsof -i :8083`

2. **Connection refused error**
   - Verify server is running: `curl http://localhost:8083/api/info`
   - Check server logs: `cat logs/graphrag_mcp.log`

3. **Client can't connect**
   - Verify GRAPHRAG_MCP_URL environment variable
   - Check network connectivity
   - Try restarting the server

### Logs

Server logs are available at:
- Standard output: `logs/graphrag_mcp.log`
- Error log: `logs/graphrag_mcp.err.log`

## Advanced Configuration

The GraphRAG MCP server can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8083` |
| `VECTOR_DB_URL` | Vector database URL | `http://localhost:6333` |
| `MAX_CACHE_SIZE` | Cache size (items) | `1000` |
| `CACHE_TTL` | Cache TTL (seconds) | `3600` |
| `MAX_RESULTS` | Max query results | `10` |
| `MIN_CONFIDENCE` | Min confidence threshold | `0.5` |
| `TRAVERSAL_DEPTH` | Graph traversal depth | `2` |
| `RATE_LIMIT_WINDOW` | Rate limit window (ms) | `60000` |
| `RATE_LIMIT_MAX` | Max requests per window | `100` |

## Future Enhancements

Planned improvements to the GraphRAG MCP server:

1. **Real GraphRAG Integration**: Replace mock implementation with actual Microsoft GraphRAG
2. **Vector Database Support**: Add support for Qdrant, Pinecone, or other vector databases
3. **Knowledge Graph Visualization**: Add endpoints for graph visualization
4. **Entity Linking**: Improve entity recognition and linking to knowledge bases
5. **Distributed Deployment**: Support for clustering and load balancing