import express from 'express';
import { rateLimit } from 'express-rate-limit';
import { GraphRAGService } from '../services/graphrag-service';
import { config } from '../config';
import { logger } from '../utils/logger';
import { getCacheItem, setCacheItem } from '../utils/cache';

// Rate limiter for API endpoints
const apiLimiter = rateLimit({
  windowMs: config.RATE_LIMIT_WINDOW,
  max: config.RATE_LIMIT_MAX,
  standardHeaders: true,
  legacyHeaders: false,
  message: 'Too many requests from this IP, please try again later.',
});

// Configure routes
export function configureRoutes(app: express.Application, graphragService: GraphRAGService): void {
  // Apply rate limiter to all /api routes
  app.use('/api', apiLimiter);

  // API info endpoint
  app.get('/api/info', (req, res) => {
    res.json({
      name: 'GraphRAG MCP Server',
      version: '1.0.0',
      status: 'running',
      graphrag_version: '1.0.0',
      tools: [
        'graphrag_index_source',
        'graphrag_extract_entities',
        'graphrag_query',
        'graphrag_relationship_query',
        'graphrag_entity_lookup',
        'graphrag_semantic_search',
        'graphrag_concept_map',
        'graphrag_schema'
      ]
    });
  });

  // GraphRAG tool: Index Source
  app.post('/api/tools/graphrag_index_source', (req, res) => {
    try {
      const { source } = req.body;
      
      if (!source || !source.source_id || !source.title || !source.content) {
        return res.status(400).json({
          success: false,
          error: 'Invalid source data. Required fields: source_id, title, content'
        });
      }
      
      const doc_id = graphragService.indexSource(source);
      
      res.json({
        success: true,
        doc_id,
        entities_extracted: source.entity_mentions?.length || 0,
        relationships_extracted: source.relationships?.length || 0
      });
    } catch (error: any) {
      logger.error(`Error in graphrag_index_source: ${error.message}`);
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  // GraphRAG tool: Extract Entities
  app.post('/api/tools/graphrag_extract_entities', (req, res) => {
    try {
      const { text, options } = req.body;
      
      if (!text || typeof text !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'Invalid request. Required field: text (string)'
        });
      }
      
      // Try cache first if enabled
      const cacheKey = `extract_entities:${Buffer.from(text).toString('base64').substring(0, 40)}`;
      const cachedResult = getCacheItem<any>(cacheKey);
      
      if (cachedResult) {
        logger.info(`Cache hit for entity extraction: ${cacheKey}`);
        return res.json(cachedResult);
      }
      
      // Extract entities
      const entities = graphragService.extractEntitiesFromText(text);
      
      // Create result with entities and mentions
      const result = {
        success: true,
        entities: entities.map(entity => ({
          entity_id: entity.entity_id,
          entity_type: entity.entity_type,
          name: entity.name,
          confidence: 0.9,  // Mock confidence
          mentions: [{
            start: text.toLowerCase().indexOf(entity.name.toLowerCase()),
            end: text.toLowerCase().indexOf(entity.name.toLowerCase()) + entity.name.length,
            text: entity.name
          }]
        })),
        relationships: []  // Mock relationships
      };
      
      // Cache result
      setCacheItem(cacheKey, result);
      
      res.json(result);
    } catch (error: any) {
      logger.error(`Error in graphrag_extract_entities: ${error.message}`);
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  // GraphRAG tool: Query
  app.post('/api/tools/graphrag_query', (req, res) => {
    try {
      const { query, focus_entities, options } = req.body;
      
      if (!query || typeof query !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'Invalid request. Required field: query (string)'
        });
      }
      
      // Try cache first if enabled
      const cacheKey = `query:${Buffer.from(query).toString('base64').substring(0, 40)}:${focus_entities?.join(',') || ''}`;
      const cachedResult = getCacheItem<any>(cacheKey);
      
      if (cachedResult) {
        logger.info(`Cache hit for query: ${cacheKey}`);
        return res.json(cachedResult);
      }
      
      // Get sources
      const sources = graphragService.getSourcesForQuery(query, focus_entities);
      
      // Build attributed prompt
      const attributedPrompt = graphragService.buildAttributedPrompt(query, sources);
      
      // Create result
      const result = {
        success: true,
        sources,
        attributed_prompt: attributedPrompt
      };
      
      // Cache result
      setCacheItem(cacheKey, result);
      
      res.json(result);
    } catch (error: any) {
      logger.error(`Error in graphrag_query: ${error.message}`);
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  // GraphRAG tool: Entity Lookup
  app.post('/api/tools/graphrag_entity_lookup', (req, res) => {
    try {
      const { entity_id, entity_name } = req.body;
      
      if (!entity_id && !entity_name) {
        return res.status(400).json({
          success: false,
          error: 'Invalid request. Required field: entity_id or entity_name'
        });
      }
      
      let entity = null;
      
      if (entity_id) {
        entity = graphragService.getEntity(entity_id);
      } else if (entity_name) {
        // Mock lookup by name (in a real implementation, we would query the entity store by name)
        entity = Object.values(graphragService).find(e => 
          e.name && e.name.toLowerCase() === entity_name.toLowerCase()
        );
      }
      
      if (!entity) {
        return res.status(404).json({
          success: false,
          error: 'Entity not found'
        });
      }
      
      res.json({
        success: true,
        entity: {
          ...entity,
          confidence: 0.95,
          sources: [{
            source_id: "src_123",
            title: "Sample Source"
          }]
        }
      });
    } catch (error: any) {
      logger.error(`Error in graphrag_entity_lookup: ${error.message}`);
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  // GraphRAG tool: Concept Map
  app.post('/api/tools/graphrag_concept_map', (req, res) => {
    try {
      const { focus_entities, traversal_depth } = req.body;
      
      if (!focus_entities || !Array.isArray(focus_entities) || focus_entities.length === 0) {
        return res.status(400).json({
          success: false,
          error: 'Invalid request. Required field: focus_entities (array of entity IDs)'
        });
      }
      
      const depth = traversal_depth || config.TRAVERSAL_DEPTH;
      
      // Generate concept map
      const conceptMap = graphragService.generateConceptMap(focus_entities, depth);
      
      res.json({
        success: true,
        ...conceptMap
      });
    } catch (error: any) {
      logger.error(`Error in graphrag_concept_map: ${error.message}`);
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  // Default route for unimplemented tools
  app.post('/api/tools/:tool', (req, res) => {
    const { tool } = req.params;
    logger.warn(`Request for unimplemented tool: ${tool}`);
    
    res.status(501).json({
      success: false,
      error: `Tool '${tool}' is not implemented yet`
    });
  });

  // Error handler
  app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
    logger.error(`Unhandled error: ${err.message}`);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  });
}