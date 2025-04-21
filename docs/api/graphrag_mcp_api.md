# GraphRAG MCP Server API

This document describes the GraphRAG MCP (Microservice Communication Protocol) Server API, which provides graph-based retrieval-augmented generation capabilities as a standalone service.

## Overview

The GraphRAG MCP Server exposes GraphRAG functionality through a RESTful API, allowing various agents to utilize knowledge graph-based source attribution and entity extraction without tight coupling to the implementation.

## Architecture

The GraphRAG MCP Server follows a layered architecture:

1. **API Layer**: Exposes RESTful endpoints for GraphRAG functionality
2. **Service Layer**: Contains core GraphRAG logic
3. **Data Layer**: Manages connections to the vector database and knowledge graph storage
4. **Utility Layer**: Provides caching, rate limiting, and other cross-cutting concerns

```
┌─────────────────────────────────────────┐
│            GraphRAG MCP Server          │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐│
│  │           REST API Layer            ││
│  │    (Express Routes & Controllers)   ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │          Service Layer              ││
│  │    (GraphRAG Core Implementation)   ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │            Data Layer               ││
│  │ (Vector DB & Knowledge Graph Store) ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │          Utility Layer              ││
│  │  (Caching, Rate Limiting, Logging)  ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

## API Endpoints

The GraphRAG MCP Server exposes the following endpoints:

### GET /api/info

Returns information about the GraphRAG MCP Server.

**Response:**
```json
{
  "name": "GraphRAG MCP Server",
  "version": "1.0.0",
  "status": "running",
  "graphrag_version": "1.0.0",
  "tools": [
    "graphrag_index_source",
    "graphrag_extract_entities",
    "graphrag_query",
    "graphrag_relationship_query",
    "graphrag_entity_lookup",
    "graphrag_semantic_search",
    "graphrag_concept_map",
    "graphrag_schema"
  ]
}
```

### POST /api/tools/graphrag_index_source

Indexes a source in the GraphRAG knowledge graph.

**Request:**
```json
{
  "source": {
    "source_id": "src_123456",
    "source_type": "web",
    "title": "Example Source",
    "content": "This is the full text content of the source.",
    "url": "https://example.com/article",
    "confidence_score": 0.85,
    "metadata": {
      "authors": ["John Doe"],
      "publication_date": "2025-04-01T10:00:00Z"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "doc_id": "doc_a1b2c3d4",
  "entities_extracted": 5,
  "relationships_extracted": 3
}
```

### POST /api/tools/graphrag_extract_entities

Extracts entities from text using named entity recognition.

**Request:**
```json
{
  "text": "Climate change is a significant challenge facing our planet. Global temperatures have risen by approximately 1.1°C since pre-industrial times.",
  "options": {
    "min_confidence": 0.5,
    "include_relationships": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "entities": [
    {
      "entity_id": "ent_a1b2c3",
      "entity_type": "concept",
      "name": "Climate change",
      "confidence": 0.95,
      "mentions": [
        {
          "start": 0,
          "end": 13,
          "text": "Climate change"
        }
      ]
    },
    {
      "entity_id": "ent_d4e5f6",
      "entity_type": "measurement",
      "name": "1.1°C",
      "confidence": 0.9,
      "mentions": [
        {
          "start": 114,
          "end": 119,
          "text": "1.1°C"
        }
      ]
    }
  ],
  "relationships": [
    {
      "relationship_id": "rel_123",
      "source_entity_id": "ent_a1b2c3",
      "target_entity_id": "ent_d4e5f6",
      "relation_type": "has_property",
      "confidence": 0.85
    }
  ]
}
```

### POST /api/tools/graphrag_query

Retrieves relevant sources for a natural language query.

**Request:**
```json
{
  "query": "What are the effects of climate change?",
  "focus_entities": ["ent_a1b2c3"],
  "options": {
    "max_sources": 5,
    "min_relevance": 0.7,
    "traversal_depth": 2
  }
}
```

**Response:**
```json
{
  "success": true,
  "sources": [
    {
      "content": "Climate change has led to rising sea levels and more frequent extreme weather events.",
      "metadata": {
        "source_id": "src_123",
        "source_type": "web",
        "title": "Climate Effects Report",
        "confidence_score": 0.9,
        "url": "https://example.com/climate-effects"
      },
      "relevance_score": 0.95,
      "explanation": "This source directly addresses climate change effects",
      "entities": ["Climate change", "sea levels", "weather events"]
    }
  ],
  "attributed_prompt": "Answer the question based on these sources: [SOURCE_1: Climate Effects Report...]"
}
```

### POST /api/tools/graphrag_relationship_query

Queries relationships between entities in the knowledge graph.

**Request:**
```json
{
  "entity_id": "ent_a1b2c3",
  "relationship_types": ["supports", "contradicts"],
  "traversal_depth": 2
}
```

**Response:**
```json
{
  "success": true,
  "relationships": [
    {
      "relationship_id": "rel_456",
      "source_entity_id": "ent_a1b2c3",
      "source_entity_name": "Climate change",
      "target_entity_id": "ent_g7h8i9",
      "target_entity_name": "Rising sea levels",
      "relation_type": "causes",
      "confidence": 0.92,
      "sources": [
        {
          "source_id": "src_123",
          "title": "Climate Effects Report"
        }
      ]
    }
  ]
}
```

### POST /api/tools/graphrag_entity_lookup

Looks up entity information by ID or name.

**Request:**
```json
{
  "entity_id": "ent_a1b2c3"
}
```

**Response:**
```json
{
  "success": true,
  "entity": {
    "entity_id": "ent_a1b2c3",
    "entity_type": "concept",
    "name": "Climate change",
    "aliases": ["Global warming", "Climate crisis"],
    "description": "Long-term shifts in temperatures and weather patterns",
    "confidence": 0.95,
    "sources": [
      {
        "source_id": "src_123",
        "title": "Climate Effects Report"
      }
    ]
  }
}
```

### POST /api/tools/graphrag_semantic_search

Performs vector-based semantic search in the knowledge graph.

**Request:**
```json
{
  "query": "impact of rising temperatures on ecosystems",
  "options": {
    "limit": 5,
    "min_score": 0.7
  }
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "entity_id": "ent_j0k1l2",
      "entity_type": "concept",
      "name": "Ecosystem disruption",
      "score": 0.89,
      "sources": [
        {
          "source_id": "src_456",
          "title": "Biodiversity Report"
        }
      ]
    }
  ]
}
```

### POST /api/tools/graphrag_concept_map

Generates a concept map for visualization based on entities and relationships.

**Request:**
```json
{
  "focus_entities": ["ent_a1b2c3"],
  "traversal_depth": 2,
  "include_relationships": true
}
```

**Response:**
```json
{
  "success": true,
  "nodes": [
    {
      "id": "ent_a1b2c3",
      "label": "Climate change",
      "type": "concept",
      "properties": {
        "confidence": 0.95
      }
    }
  ],
  "edges": [
    {
      "id": "rel_456",
      "source": "ent_a1b2c3",
      "target": "ent_g7h8i9",
      "label": "causes",
      "properties": {
        "confidence": 0.92
      }
    }
  ]
}
```

### POST /api/tools/graphrag_schema

Retrieves or updates the GraphRAG knowledge graph schema.

**Request (GET):**
```json
{
  "operation": "get",
  "schema_type": "entity_types"
}
```

**Response:**
```json
{
  "success": true,
  "schema": {
    "entity_types": [
      {
        "id": "concept",
        "name": "Concept",
        "description": "Abstract idea or notion"
      },
      {
        "id": "person",
        "name": "Person",
        "description": "Human individual"
      }
    ]
  }
}
```

## Client Integration

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

## Security

The GraphRAG MCP Server implements the following security measures:

1. **Rate limiting**: Prevents abuse through request throttling
2. **Input validation**: Validates all inputs to prevent injection attacks
3. **Authentication**: Optional JWT authentication can be enabled
4. **HTTPS**: Supports HTTPS for secure communication

## Deployment

The GraphRAG MCP Server can be deployed using Docker:

```bash
docker build -t graphrag-mcp-server .
docker run -p 8083:8083 -e VECTOR_DB_URL=http://vector-db:6333 graphrag-mcp-server
```

Or using docker-compose:

```yaml
version: '3'
services:
  graphrag-mcp-server:
    build: ./graphrag-mcp-server
    ports:
      - "8083:8083"
    environment:
      - VECTOR_DB_URL=http://vector-db:6333
      - MAX_RESULTS=10
    depends_on:
      - vector-db
  
  vector-db:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - vector-db-data:/qdrant/storage
      
volumes:
  vector-db-data:
```