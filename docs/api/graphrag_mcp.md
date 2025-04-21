# GraphRAG MCP Server Design

This document outlines the design for a GraphRAG MCP server wrapper that provides knowledge graph-based retrieval augmented generation capabilities.

## 1. Architecture Overview

The GraphRAG MCP server follows a similar architecture to the Web Search MCP server but focuses on knowledge graph operations and RAG functionality:

```
┌─────────────────────────────────────────────────────────────────┐
│                     GraphRAG MCP Server                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌────────────────┐    ┌──────────────────┐  │
│  │             │    │                │    │                  │  │
│  │  MCP API    │<-->│ GraphRAG Core  │<-->│ Vector Database  │  │
│  │  Interface  │    │ Implementation │    │  (e.g. Chroma)   │  │
│  │             │    │                │    │                  │  │
│  └─────────────┘    └────────────────┘    └──────────────────┘  │
│         ^                   ^                      ^            │
│         │                   │                      │            │
│         v                   v                      v            │
│  ┌─────────────┐    ┌────────────────┐    ┌──────────────────┐  │
│  │             │    │                │    │                  │  │
│  │ Tool        │    │ Knowledge Graph│    │  Document        │  │
│  │ Definitions │    │ Schema Manager │    │  Processors      │  │
│  │             │    │                │    │                  │  │
│  └─────────────┘    └────────────────┘    └──────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   Cache & Rate Limiter                      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                ^
                                │
                                v
                   ┌─────────────────────────┐
                   │                         │
                   │ Agent Provocateur Agents│
                   │                         │
                   └─────────────────────────┘
```

### Key Components:

- **MCP API Interface**: Implements the Model Context Protocol interface for communication with agents.
- **GraphRAG Core Implementation**: The main logic for graph-based RAG operations.
- **Vector Database**: Stores vector embeddings for documents and graph nodes.
- **Knowledge Graph Schema Manager**: Manages the structure and schema of the knowledge graph.
- **Document Processors**: Convert different document types into graph nodes and embeddings.
- **Tool Definitions**: MCP tool definitions exposed to agents.
- **Cache & Rate Limiter**: Provides caching of results and rate limiting of requests.

## 2. Key Endpoints/Tools

The GraphRAG MCP server exposes the following tools:

1. **graphrag_index_document**
   - Add a document to the knowledge graph and generate embeddings
   - Parameters: `document_content`, `metadata`, `document_type`

2. **graphrag_query**
   - Query the knowledge graph using natural language
   - Parameters: `query`, `max_results`, `min_similarity_score`

3. **graphrag_entity_lookup**
   - Look up specific entities in the knowledge graph
   - Parameters: `entity_name`, `entity_type`, `include_related`

4. **graphrag_relationship_query**
   - Query relationships between entities
   - Parameters: `source_entity`, `target_entity`, `relationship_type`

5. **graphrag_concept_map**
   - Generate a concept map around a particular entity or concept
   - Parameters: `central_concept`, `depth`, `max_nodes`

6. **graphrag_semantic_search**
   - Perform a semantic search across the knowledge base
   - Parameters: `query`, `max_results`, `filter`

7. **graphrag_extract_entities**
   - Extract entities from a text passage for potential inclusion in the graph
   - Parameters: `text`, `entity_types`

8. **graphrag_schema**
   - Get or update the knowledge graph schema
   - Parameters: `operation`, `schema_updates`

## 3. Sample Core MCP Server Implementation

```typescript
// index.ts - GraphRAG MCP Server main file

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import { loadConfig } from './config.js';
import { GraphRAGManager } from './core/graphrag-manager.js';
import { DocumentProcessor } from './processors/document-processor.js';
import { KnowledgeGraphSchema } from './schema/knowledge-graph-schema.js';
import { ResultCache } from './utils/cache.js';
import { RateLimiter } from './utils/rate-limiter.js';
import { buildToolList } from './tools/graphrag-tools.js';

// Load configuration
const config = loadConfig();

// Initialize GraphRAG manager
const graphragManager = new GraphRAGManager(config.vectorDb);

// Initialize schema manager
const schemaManager = new KnowledgeGraphSchema(config.schema);

// Initialize document processor
const documentProcessor = new DocumentProcessor(schemaManager);

// Initialize cache and rate limiter
const cache = new ResultCache(config.cache);
const rateLimiter = new RateLimiter(config.rateLimit);

// Create server
const server = new Server(
  {
    name: "graphrag-mcp-server",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Helper functions for MCP responses
function createSuccessResponse(text: string) {
  return {
    content: [{ type: 'text', text }],
    isError: false,
  };
}

function createErrorResponse(message: string) {
  return {
    content: [{ type: 'text', text: `Error: ${message}` }],
    isError: true,
  };
}

// Register request handlers
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: buildToolList(),
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const { name, arguments: args } = request.params;
    
    if (!args) {
      return createErrorResponse('No arguments provided');
    }
    
    // Check rate limit
    if (!rateLimiter.allowRequest()) {
      return createErrorResponse('Rate limit exceeded. Please try again later.');
    }
    
    // Handle tool calls
    if (name === 'graphrag_index_document') {
      const { document_content, metadata, document_type } = args as { 
        document_content: string; 
        metadata?: any;
        document_type: string;
      };
      
      if (!document_content) {
        return createErrorResponse('Missing required parameter: document_content');
      }
      
      // Process and index the document
      const documentId = await graphragManager.indexDocument(
        document_content,
        document_type,
        metadata,
        documentProcessor
      );
      
      return createSuccessResponse(JSON.stringify({ document_id: documentId }));
    }
    
    if (name === 'graphrag_query') {
      const { query, max_results = 5, min_similarity_score = 0.7 } = args as {
        query: string;
        max_results?: number;
        min_similarity_score?: number;
      };
      
      if (!query) {
        return createErrorResponse('Missing required parameter: query');
      }
      
      // Check cache first
      const cacheKey = `query:${query}:${max_results}:${min_similarity_score}`;
      const cachedResult = cache.get<string>(cacheKey);
      
      if (cachedResult) {
        console.error(`Cache hit for: ${cacheKey}`);
        return createSuccessResponse(cachedResult);
      }
      
      // Perform the query
      const results = await graphragManager.query(query, max_results, min_similarity_score);
      const formattedResults = JSON.stringify(results);
      
      // Cache results
      cache.set(cacheKey, formattedResults);
      
      return createSuccessResponse(formattedResults);
    }
    
    // Additional tool handlers would be implemented here
    
    return createErrorResponse(`Unknown tool: ${name}`);
  } catch (error: any) {
    console.error('Unexpected error:', error);
    return createErrorResponse(`Unexpected error: ${error.message}`);
  }
});

// Start the server
async function runServer() {
  try {
    console.error(`Starting GraphRAG MCP server`);
    
    const transport = new StdioServerTransport();
    await server.connect(transport);
    
    console.error(`GraphRAG MCP Server running on stdio`);
  } catch (error) {
    console.error('Error starting server:', error);
    process.exit(1);
  }
}

// Handle process signals
process.on('SIGINT', () => {
  console.error('Received SIGINT, shutting down');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error('Received SIGTERM, shutting down');
  process.exit(0);
});

// Run the server
runServer().catch((error) => {
  console.error('Fatal error running server:', error);
  process.exit(1);
});
```

## 4. Agent Integration with GraphRAG MCP

Agents would connect to the GraphRAG MCP server using a pattern similar to the Web Search Agent:

```python
# graphrag_agent.py - Agent for using GraphRAG services

import os
import logging
import uuid
import datetime
from typing import Any, Dict, List, Optional

from agent_provocateur.agent_base import BaseAgent
from agent_provocateur.a2a_models import TaskRequest
from agent_provocateur.mcp_client import McpClient

logger = logging.getLogger(__name__)

class GraphRAGAgent(BaseAgent):
    """Agent for knowledge graph-based retrieval augmented generation."""
    
    async def on_startup(self) -> None:
        """Initialize the GraphRAG agent."""
        self.logger.info("Starting GraphRAG agent...")
        
        # Initialize configuration
        self.graphrag_config = {
            "max_results": 5,
            "min_similarity_score": 0.7,
            "default_entity_types": ["person", "organization", "concept", "location", "event"],
            "max_depth": 3,
        }
        
        # Initialize MCP client for GraphRAG
        graphrag_mcp_url = os.getenv("GRAPHRAG_MCP_URL", "http://localhost:8081")
        self.graphrag_mcp_client = McpClient(graphrag_mcp_url)
        self.logger.info(f"GraphRAG MCP client initialized with URL: {graphrag_mcp_url}")
    
    async def handle_task_request(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Process a task request sent to this agent."""
        self.logger.info(f"Processing task request: {task_request.intent}")
        
        # Route to appropriate handler based on intent
        if task_request.intent == "index_document":
            return await self.handle_index_document(task_request)
        elif task_request.intent == "query_knowledge":
            return await self.handle_query_knowledge(task_request)
        elif task_request.intent == "entity_lookup":
            return await self.handle_entity_lookup(task_request)
        elif task_request.intent == "generate_concept_map":
            return await self.handle_generate_concept_map(task_request)
        else:
            self.logger.warning(f"Unknown intent: {task_request.intent}")
            return {
                "error": f"Unknown intent: {task_request.intent}",
                "status": "failed"
            }
    
    async def handle_index_document(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Handle a request to index a document in the knowledge graph."""
        document_content = task_request.payload.get("document_content")
        document_type = task_request.payload.get("document_type", "text")
        metadata = task_request.payload.get("metadata", {})
        
        if not document_content:
            return {
                "error": "Missing required parameter: document_content",
                "status": "failed"
            }
        
        try:
            # Call MCP tool to index the document
            result = await self.graphrag_mcp_client.call_tool(
                "graphrag_index_document",
                {
                    "document_content": document_content,
                    "document_type": document_type,
                    "metadata": metadata
                }
            )
            
            # Parse the result
            document_id = result.content[0].text
            
            return {
                "document_id": document_id,
                "document_type": document_type,
                "status": "completed"
            }
        
        except Exception as e:
            self.logger.error(f"Error indexing document: {e}")
            return {
                "error": f"Indexing failed: {str(e)}",
                "status": "failed"
            }
    
    async def handle_query_knowledge(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Handle a request to query the knowledge graph."""
        query = task_request.payload.get("query")
        max_results = task_request.payload.get("max_results", self.graphrag_config["max_results"])
        min_similarity_score = task_request.payload.get(
            "min_similarity_score", 
            self.graphrag_config["min_similarity_score"]
        )
        
        if not query:
            return {
                "error": "Missing required parameter: query",
                "status": "failed"
            }
        
        try:
            # Call MCP tool to query the knowledge graph
            result = await self.graphrag_mcp_client.call_tool(
                "graphrag_query",
                {
                    "query": query,
                    "max_results": max_results,
                    "min_similarity_score": min_similarity_score
                }
            )
            
            # Parse the result
            query_results = result.content[0].text
            
            return {
                "query": query,
                "results": query_results,
                "status": "completed"
            }
        
        except Exception as e:
            self.logger.error(f"Error querying knowledge graph: {e}")
            return {
                "error": f"Query failed: {str(e)}",
                "query": query,
                "status": "failed"
            }
    
    # Additional handlers for other intents would be implemented here
```

## 5. Advantages of GraphRAG as a Separate MCP Service

Making GraphRAG a separate MCP service provides several advantages:

1. **Decoupling and Modularity**
   - The GraphRAG functionality is separated from the core agent system, allowing independent development, testing, and deployment.
   - Agents can use GraphRAG capabilities without needing to implement complex graph-based RAG logic.

2. **Specialized Resource Management**
   - Vector databases and knowledge graph operations often have specific resource requirements.
   - A separate service allows for tailored infrastructure for these specialized needs.

3. **Independent Scaling**
   - The GraphRAG service can be scaled independently based on usage patterns without affecting other components.
   - During peak periods, more instances can be deployed to handle increased load.

4. **Technology Evolution**
   - The underlying vector database and graph technologies can be upgraded or changed without impacting the agent architecture.
   - New embedding models or retrieval methods can be implemented without modifying agent code.

5. **Centralized Knowledge Repository**
   - Acts as a central knowledge store that multiple agents can access.
   - Ensures consistent knowledge representation across different agent interactions.

6. **Optimized Caching**
   - Implements domain-specific caching strategies optimized for graph and vector searches.
   - Reduces redundant embedding generation and similar queries across agent instances.

7. **Simplified Agent Implementation**
   - Agents can focus on their core tasks while delegating knowledge management to the GraphRAG service.
   - Reduces complexity in agent code, making it more maintainable.

8. **Enhanced Security and Access Control**
   - Centralized management of knowledge enables better access controls and security policies.
   - Sensitive information can be managed with appropriate restrictions at the service level.

9. **Cross-Language Support**
   - The MCP interface allows agents written in different programming languages to use the GraphRAG capabilities.
   - Enables polyglot agent ecosystems to share the same knowledge graph infrastructure.

10. **Improved Testing and Monitoring**
    - Isolating GraphRAG functionality allows for targeted testing and performance monitoring.
    - Issues can be identified and resolved more easily when isolated to a specific service.