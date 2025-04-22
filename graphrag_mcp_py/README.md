# GraphRAG MCP Server (Python Implementation)

This is the Python implementation of the GraphRAG MCP (Microservice Communication Protocol) Server for Agent Provocateur. It provides graph-based retrieval-augmented generation capabilities with FAISS vector database integration.

## Features

- FAISS vector database integration for semantic search
- Advanced entity extraction and linking with external knowledge bases
- Entity disambiguation and relationship detection
- Knowledge graph operations with local persistence
- Source attribution for LLM responses
- RESTful API for microservice communication
- Caching and rate-limiting for performance optimization

## Architecture

The GraphRAG MCP Server follows a layered architecture:

1. **API Layer**: FastAPI RESTful endpoints for GraphRAG functionality
2. **Service Layer**: GraphRAG core logic and entity management
3. **Data Layer**: FAISS vector database and knowledge graph operations
4. **Utility Layer**: Caching, rate limiting, and logging

## Installation

### Prerequisites

- Python 3.9+
- pip

### Setup

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

```bash
# Start the server
./scripts/run.sh

# Stop the server
./scripts/stop.sh
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8083` |
| `VECTOR_DB_TYPE` | Vector database type | `faiss` |
| `VECTOR_DB_PATH` | Path to vector database files | `./data/vectors/faiss` |
| `MAX_RESULTS` | Default maximum results | `10` |
| `MIN_CONFIDENCE` | Default minimum confidence | `0.5` |
| `TRAVERSAL_DEPTH` | Default traversal depth | `2` |
| `ENABLE_CACHE` | Enable caching | `true` |
| `MAX_CACHE_SIZE` | Maximum cache size (items) | `1000` |
| `CACHE_TTL` | Cache TTL (seconds) | `3600` |
| `RATE_LIMIT_WINDOW` | Rate limit window (ms) | `60000` |
| `RATE_LIMIT_MAX` | Max requests per window | `100` |
| `LOG_LEVEL` | Logging level | `info` |
| `ENABLE_ENHANCED_ENTITY_LINKING` | Enable enhanced entity linking | `true` |
| `USE_WIKIDATA_KB` | Use Wikidata knowledge base | `true` | 
| `LOCAL_KB_PATH` | Path to local knowledge base | `./data/knowledge_base.json` |
| `WIKIDATA_CACHE_PATH` | Path to Wikidata cache | `./data/wikidata_cache.json` |
| `ENTITY_LINKING_CONFIDENCE_THRESHOLD` | Confidence threshold for entity linking | `0.7` |
| `MAX_ENTITY_RELATIONSHIPS` | Maximum number of entity relationships | `10` |
| `CONTEXTUAL_DISAMBIGUATION` | Enable contextual disambiguation | `true` |

### Docker

You can also run the server using Docker:

```bash
# Build the Docker image
docker build -t graphrag-mcp-py .

# Run the container
docker run -p 8083:8083 graphrag-mcp-py
```

Or with docker-compose:

```bash
docker-compose up -d
```

## API Reference

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/info` | GET | Get server information |
| `/api/tools/graphrag_index_source` | POST | Index a source in GraphRAG |
| `/api/tools/graphrag_extract_entities` | POST | Extract entities from text |
| `/api/tools/graphrag_query` | POST | Get sources for a query |
| `/api/tools/graphrag_entity_lookup` | POST | Look up entity information |
| `/api/tools/graphrag_concept_map` | POST | Generate a concept map |
| `/api/tools/graphrag_schema` | POST | Get or update the graph schema |
| `/api/process_attributed_response` | POST | Process a response with attribution markers |

For detailed API documentation, see [GraphRAG MCP API](../docs/api/graphrag_mcp_api.md). For a comparison with the TypeScript implementation, see [GraphRAG Implementation Comparison](../docs/development/graphrag_implementation_comparison.md).

## Integration with Agent Provocateur

To integrate the GraphRAG MCP Server with Agent Provocateur, set these environment variables:

```bash
export GRAPHRAG_MCP_URL=http://localhost:8083
export AGENT_TYPE=xml_graphrag
```

Then the GraphRAG client will automatically connect to this server.

## Differences from TypeScript Implementation

This Python implementation offers several advantages over the TypeScript version:

1. **Native FAISS Integration**: Direct integration with FAISS for high-performance vector search.
2. **Simplified Development**: Python's ecosystem makes NLP and vector operations more straightforward.
3. **Easier Integration**: Better compatibility with the Python-based Agent Provocateur framework.
4. **Enhanced Performance**: Optimized vector operations with NumPy and FAISS.
5. **Future ML Integration**: Easier to extend with scikit-learn, PyTorch, or other ML libraries.

## Testing

To test the GraphRAG MCP Server:

```bash
# Make sure the server is running
./scripts/run.sh

# Test the API
curl http://localhost:8083/api/info

# Test basic entity extraction
curl -X POST http://localhost:8083/api/tools/graphrag_extract_entities \
  -H "Content-Type: application/json" \
  -d '{"text":"Climate change is a global challenge that affects everyone."}'

# Test enhanced entity linking with Wikidata integration
curl -X POST http://localhost:8083/api/tools/graphrag_extract_entities \
  -H "Content-Type: application/json" \
  -d '{"text":"The Paris Agreement was signed by the United Nations to address climate change.", "use_enhanced_linking": true, "use_external_kb": true}'
```

## Enhanced Entity Linking

This implementation includes advanced entity linking capabilities with external knowledge base integration. For details, see [Entity Linking Enhancement](./ENTITY_LINKING_ENHANCEMENT.md).