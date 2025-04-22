/**
 * GraphRAG MCP tools definition
 * Defines the tools that can be called by agents via the MCP interface
 */

/**
 * Tool definition interface
 */
export interface ToolDefinition {
  name: string;
  description: string;
  parameters: {
    type: string;
    properties: Record<string, any>;
    required: string[];
  };
}

/**
 * Build the list of tools exposed by the GraphRAG MCP server
 * @returns List of tool definitions
 */
export function buildToolList(): ToolDefinition[] {
  return [
    {
      name: 'graphrag_index_document',
      description: 'Index a document into the knowledge graph',
      parameters: {
        type: 'object',
        properties: {
          document_content: {
            type: 'string',
            description: 'Content of the document to index'
          },
          document_type: {
            type: 'string',
            description: 'Type of document (text, html, pdf, code, etc.)',
            default: 'text'
          },
          metadata: {
            type: 'object',
            description: 'Additional metadata for the document',
            additionalProperties: true
          }
        },
        required: ['document_content']
      }
    },
    {
      name: 'graphrag_index_text_document',
      description: 'Index a text or Markdown document into the knowledge graph',
      parameters: {
        type: 'object',
        properties: {
          document_content: {
            type: 'string',
            description: 'Content of the document to index'
          },
          document_type: {
            type: 'string',
            description: 'Type of text document (text, markdown)',
            default: 'markdown'
          },
          title: {
            type: 'string',
            description: 'Title of the document'
          },
          metadata: {
            type: 'object',
            description: 'Additional metadata for the document',
            additionalProperties: true
          }
        },
        required: ['document_content', 'title']
      }
    },
    {
      name: 'graphrag_query',
      description: 'Query the knowledge graph using natural language',
      parameters: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Natural language query'
          },
          max_results: {
            type: 'number',
            description: 'Maximum number of results to return',
            default: 5
          },
          min_similarity_score: {
            type: 'number',
            description: 'Minimum similarity score threshold (0.0-1.0)',
            default: 0.7
          }
        },
        required: ['query']
      }
    },
    {
      name: 'graphrag_entity_lookup',
      description: 'Look up specific entities in the knowledge graph',
      parameters: {
        type: 'object',
        properties: {
          entity_name: {
            type: 'string',
            description: 'Name of the entity to look up'
          },
          entity_type: {
            type: 'string',
            description: 'Type of entity (person, organization, concept, etc.)'
          },
          include_related: {
            type: 'boolean',
            description: 'Whether to include related entities',
            default: true
          }
        },
        required: ['entity_name']
      }
    },
    {
      name: 'graphrag_relationship_query',
      description: 'Query relationships between entities',
      parameters: {
        type: 'object',
        properties: {
          source_entity: {
            type: 'string',
            description: 'Source entity name or ID'
          },
          target_entity: {
            type: 'string',
            description: 'Target entity name or ID'
          },
          relationship_type: {
            type: 'string',
            description: 'Specific relationship type to query (optional)'
          }
        },
        required: ['source_entity', 'target_entity']
      }
    },
    {
      name: 'graphrag_concept_map',
      description: 'Generate a concept map around a central concept',
      parameters: {
        type: 'object',
        properties: {
          central_concept: {
            type: 'string',
            description: 'Central concept or entity for the map'
          },
          depth: {
            type: 'number',
            description: 'Number of relationship levels to include',
            default: 2
          },
          max_nodes: {
            type: 'number',
            description: 'Maximum number of nodes to include',
            default: 20
          }
        },
        required: ['central_concept']
      }
    },
    {
      name: 'graphrag_semantic_search',
      description: 'Perform semantic search across the knowledge base',
      parameters: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Search query string'
          },
          max_results: {
            type: 'number',
            description: 'Maximum number of results to return',
            default: 10
          },
          filter: {
            type: 'object',
            description: 'Filter criteria for search results',
            additionalProperties: true
          }
        },
        required: ['query']
      }
    },
    {
      name: 'graphrag_extract_entities',
      description: 'Extract entities from text for potential graph inclusion',
      parameters: {
        type: 'object',
        properties: {
          text: {
            type: 'string',
            description: 'Text to analyze for entities'
          },
          entity_types: {
            type: 'array',
            description: 'Types of entities to extract',
            items: {
              type: 'string'
            },
            default: ['person', 'organization', 'concept', 'location', 'event']
          }
        },
        required: ['text']
      }
    },
    {
      name: 'graphrag_schema',
      description: 'Get or update the knowledge graph schema',
      parameters: {
        type: 'object',
        properties: {
          operation: {
            type: 'string',
            description: 'Operation to perform (get, update)',
            enum: ['get', 'update'],
            default: 'get'
          },
          schema_updates: {
            type: 'object',
            description: 'Schema updates to apply (for update operation)',
            additionalProperties: true
          }
        },
        required: ['operation']
      }
    }
  ];
}