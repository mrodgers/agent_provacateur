import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger';

// Types
export enum EntityType {
  PERSON = 'person',
  ORGANIZATION = 'organization',
  LOCATION = 'location',
  CONCEPT = 'concept',
  PRODUCT = 'product',
  EVENT = 'event',
  DATE = 'date',
  FACT = 'fact',
  CLAIM = 'claim',
  OTHER = 'other',
}

export enum RelationType {
  IS_A = 'is_a',
  PART_OF = 'part_of',
  LOCATED_IN = 'located_in',
  CREATED_BY = 'created_by',
  WORKS_FOR = 'works_for',
  HAS_PROPERTY = 'has_property',
  RELATED_TO = 'related_to',
  CONTRADICTS = 'contradicts',
  SUPPORTS = 'supports',
  TEMPORAL = 'temporal',
  CAUSAL = 'causal',
  OTHER = 'other',
}

export enum SourceType {
  WEB = 'web',
  DOCUMENT = 'document',
  DATABASE = 'database',
  API = 'api',
  KNOWLEDGE_BASE = 'knowledge_base',
  CALCULATION = 'calculation',
  USER_PROVIDED = 'user_provided',
  OTHER = 'other',
}

export interface Entity {
  entity_id: string;
  entity_type: EntityType;
  name: string;
  aliases?: string[];
  description?: string;
  metadata?: Record<string, any>;
}

export interface EntityMention {
  start: number;
  end: number;
  text: string;
}

export interface Relationship {
  relationship_id: string;
  source_entity_id: string;
  target_entity_id: string;
  relation_type: RelationType;
  confidence: number;
  metadata?: Record<string, any>;
}

export interface Source {
  source_id: string;
  source_type: SourceType;
  title: string;
  content: string;
  url?: string;
  authors?: string[];
  publication_date?: string;
  retrieval_date: string;
  confidence_score: number;
  reliability_score: number;
  metadata?: Record<string, any>;
}

// Configuration type
export interface GraphRAGServiceConfig {
  vectorDbUrl?: string;
  maxResults?: number;
  minConfidence?: number;
  traversalDepth?: number;
  cacheEnabled?: boolean;
}

// Mock vector database document
class MockVectorDocument {
  content: string;
  metadata: Record<string, any>;
  entities: Array<{
    entity_id: string;
    entity_type: string;
    positions: Array<[number, number]>;
  }>;
  relationships: Array<{
    source_entity_id: string;
    target_entity_id: string;
    relation_type: string;
  }>;

  constructor(content: string = '', metadata: Record<string, any> = {}) {
    this.content = content;
    this.metadata = metadata;
    this.entities = [];
    this.relationships = [];
  }

  addEntity(entity_id: string, entity_type: string, positions: Array<[number, number]>) {
    this.entities.push({
      entity_id,
      entity_type,
      positions
    });
  }

  addRelationship(source_entity_id: string, target_entity_id: string, relation_type: string) {
    this.relationships.push({
      source_entity_id,
      target_entity_id,
      relation_type
    });
  }
}

// Mock vector database indexer
class MockVectorIndexer {
  private documents: Record<string, MockVectorDocument> = {};

  addDocument(document: MockVectorDocument): string {
    const doc_id = `doc_${uuidv4().substring(0, 8)}`;
    this.documents[doc_id] = document;
    return doc_id;
  }

  getDocument(doc_id: string): MockVectorDocument | undefined {
    return this.documents[doc_id];
  }

  getAllDocuments(): Record<string, MockVectorDocument> {
    return this.documents;
  }
}

// Mock vector database retriever
class MockVectorRetriever {
  private indexer: MockVectorIndexer;

  constructor(indexer: MockVectorIndexer) {
    this.indexer = indexer;
  }

  retrieve(query: string, config: Record<string, any> = {}): Array<{
    content: string;
    metadata: Record<string, any>;
    relevance_score: number;
    explanation: string;
    entities: string[];
  }> {
    // Mock retrieval of documents
    const documents = this.indexer.getAllDocuments();
    const results = [];
    let i = 0;
    
    for (const [doc_id, doc] of Object.entries(documents)) {
      if (i >= (config.max_results || 2)) break;
      
      // Simple relevance scoring based on content overlap with query
      const queryWords = query.toLowerCase().split(/\s+/);
      const contentWords = doc.content.toLowerCase().split(/\s+/);
      const overlap = queryWords.filter(word => contentWords.includes(word)).length;
      const relevance = Math.min(0.5 + (overlap / queryWords.length) * 0.5, 0.95);
      
      if (relevance >= (config.min_relevance || 0.5)) {
        results.push({
          content: doc.content,
          metadata: doc.metadata,
          relevance_score: relevance - (i * 0.05),
          explanation: `Matched ${overlap} terms from the query`,
          entities: doc.entities.map(e => e.entity_id)
        });
        i++;
      }
    }
    
    return results;
  }

  retrieveForEntities(entity_ids: string[], config: Record<string, any> = {}): Array<{
    content: string;
    metadata: Record<string, any>;
    relevance_score: number;
    explanation: string;
    entities: string[];
  }> {
    // Mock retrieval of documents by entity
    const documents = this.indexer.getAllDocuments();
    const results = [];
    let i = 0;
    
    for (const [doc_id, doc] of Object.entries(documents)) {
      if (i >= (config.max_results || 2)) break;
      
      // Check if document contains any of the requested entities
      const docEntities = doc.entities.map(e => e.entity_id);
      const matchedEntities = entity_ids.filter(id => docEntities.includes(id));
      
      if (matchedEntities.length > 0) {
        const relevance = 0.7 + (matchedEntities.length / entity_ids.length) * 0.25;
        
        results.push({
          content: doc.content,
          metadata: doc.metadata,
          relevance_score: relevance - (i * 0.05),
          explanation: `Document contains ${matchedEntities.length} requested entities`,
          entities: docEntities
        });
        i++;
      }
    }
    
    return results;
  }
}

/**
 * GraphRAG Service implementation
 */
export class GraphRAGService {
  private config: Required<GraphRAGServiceConfig>;
  private indexer: MockVectorIndexer;
  private retriever: MockVectorRetriever;
  private entityStore: Record<string, Entity> = {};
  private relationshipStore: Record<string, Relationship> = {};

  constructor(config?: GraphRAGServiceConfig) {
    this.config = {
      vectorDbUrl: config?.vectorDbUrl || 'http://localhost:6333',
      maxResults: config?.maxResults || 10,
      minConfidence: config?.minConfidence || 0.5,
      traversalDepth: config?.traversalDepth || 2,
      cacheEnabled: config?.cacheEnabled !== false,
    };

    // Initialize vector database components
    this.indexer = new MockVectorIndexer();
    this.retriever = new MockVectorRetriever(this.indexer);

    logger.info(`Initialized GraphRAG service with config: ${JSON.stringify(this.config)}`);
  }

  /**
   * Index a source in GraphRAG
   */
  public indexSource(source: Source): string {
    logger.info(`Indexing source: ${source.source_id} - ${source.title}`);

    // Create vector document
    const doc = new MockVectorDocument(
      source.content,
      {
        source_id: source.source_id,
        source_type: source.source_type,
        title: source.title,
        url: source.url,
        confidence_score: source.confidence_score,
        reliability_score: source.reliability_score,
        retrieval_date: source.retrieval_date,
      }
    );

    // Extract entities from source content
    const entities = this.extractEntitiesFromText(source.content);
    
    // Add entities to document
    for (const entity of entities) {
      // Store entity
      this.entityStore[entity.entity_id] = entity;
      
      // Find mentions in text
      const entityName = entity.name.toLowerCase();
      const content = source.content.toLowerCase();
      let start = 0;
      
      while (true) {
        const pos = content.indexOf(entityName, start);
        if (pos === -1) break;
        
        doc.addEntity(
          entity.entity_id,
          entity.entity_type,
          [[pos, pos + entityName.length]]
        );
        
        start = pos + 1;
      }
    }
    
    // Create some relationships between entities
    if (entities.length >= 2) {
      for (let i = 0; i < entities.length - 1; i++) {
        const relationship: Relationship = {
          relationship_id: `rel_${uuidv4().substring(0, 8)}`,
          source_entity_id: entities[i].entity_id,
          target_entity_id: entities[i + 1].entity_id,
          relation_type: RelationType.RELATED_TO,
          confidence: 0.7,
        };
        
        this.relationshipStore[relationship.relationship_id] = relationship;
        
        doc.addRelationship(
          relationship.source_entity_id,
          relationship.target_entity_id,
          relationship.relation_type
        );
      }
    }

    // Index the document
    const doc_id = this.indexer.addDocument(doc);
    logger.info(`Indexed source ${source.source_id} as document ${doc_id}`);

    return doc_id;
  }

  /**
   * Get sources for a query
   */
  public getSourcesForQuery(query: string, focusEntities?: string[]): Array<{
    content: string;
    metadata: Record<string, any>;
    relevance_score: number;
    explanation: string;
    entities: string[];
  }> {
    logger.info(`Retrieving sources for query: ${query}`);

    // Configure retrieval options
    const retrievalConfig = {
      max_results: this.config.maxResults,
      min_relevance: this.config.minConfidence,
      include_explanations: true,
      traversal_depth: this.config.traversalDepth,
    };

    // Retrieve sources with different strategies based on context
    let results;
    if (focusEntities && focusEntities.length > 0) {
      logger.info(`Using entity-centric retrieval with entities: ${focusEntities}`);
      results = this.retriever.retrieveForEntities(
        focusEntities,
        retrievalConfig
      );
    } else {
      logger.info('Using query-based retrieval');
      results = this.retriever.retrieve(
        query,
        retrievalConfig
      );
    }

    logger.info(`Retrieved ${results.length} sources for query`);
    return results;
  }

  /**
   * Extract entities from text
   */
  public extractEntitiesFromText(text: string): Entity[] {
    try {
      const entities: Entity[] = [];
      
      // Simple keyword-based entity extraction
      const keywordMap: Record<string, EntityType> = {
        'climate change': EntityType.CONCEPT,
        'global warming': EntityType.CONCEPT,
        'artificial intelligence': EntityType.CONCEPT,
        'united states': EntityType.LOCATION,
        'european union': EntityType.ORGANIZATION,
        'covid-19': EntityType.CONCEPT,
        'paris agreement': EntityType.CONCEPT,
      };
      
      // Check for known entities
      const textLower = text.toLowerCase();
      for (const [keyword, entityType] of Object.entries(keywordMap)) {
        if (textLower.includes(keyword)) {
          entities.push({
            entity_id: `ent_${uuidv4().substring(0, 8)}`,
            entity_type: entityType,
            name: keyword.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
            description: `Entity extracted from text based on keyword match`,
          });
        }
      }
      
      // Extract potential entities based on capitalization patterns
      const capitalsRegex = /\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g;
      const capitalizedPhrases = text.match(capitalsRegex) || [];
      
      for (const phrase of capitalizedPhrases) {
        // Skip if already added as a known entity
        if (entities.some(e => e.name.toLowerCase() === phrase.toLowerCase())) {
          continue;
        }
        
        // Determine entity type based on content
        let entityType = EntityType.OTHER;
        if (phrase.match(/^\d{1,2}\/\d{1,2}\/\d{2,4}$/)) {
          entityType = EntityType.DATE;
        } else if (phrase.length > 2 && phrase.length < 15) {
          entityType = EntityType.CONCEPT;
        }
        
        entities.push({
          entity_id: `ent_${uuidv4().substring(0, 8)}`,
          entity_type: entityType,
          name: phrase,
          description: `Entity extracted from text based on capitalization pattern`,
        });
      }
      
      // If no entities found, add at least one general concept
      if (entities.length === 0) {
        // Extract most frequent non-stop word as a concept
        const words = text.toLowerCase().split(/\s+/);
        const wordFreq: Record<string, number> = {};
        
        for (const word of words) {
          if (word.length > 4) { // Skip short words
            wordFreq[word] = (wordFreq[word] || 0) + 1;
          }
        }
        
        let topWord = '';
        let topFreq = 0;
        
        for (const [word, freq] of Object.entries(wordFreq)) {
          if (freq > topFreq) {
            topWord = word;
            topFreq = freq;
          }
        }
        
        if (topWord) {
          entities.push({
            entity_id: `ent_${uuidv4().substring(0, 8)}`,
            entity_type: EntityType.CONCEPT,
            name: topWord.charAt(0).toUpperCase() + topWord.slice(1),
            description: `Main concept extracted from text`,
          });
        }
      }
      
      logger.info(`Extracted ${entities.length} entities from text`);
      return entities;
    } catch (error) {
      logger.error(`Error extracting entities: ${error}`);
      return [];
    }
  }

  /**
   * Build a prompt with attribution markers
   */
  public buildAttributedPrompt(query: string, sources: Array<{
    content: string;
    metadata: Record<string, any>;
    relevance_score: number;
    explanation?: string;
    entities?: string[];
  }>): string {
    const promptParts = [
      'Answer the question based on these sources:\n\n'
    ];

    // Add each source with clear attribution markers
    for (let i = 0; i < sources.length; i++) {
      const source = sources[i];
      const sourceId = `SOURCE_${i + 1}`;
      const sourceMetadata = source.metadata;

      promptParts.push(
        `[${sourceId}: ${sourceMetadata.title} ` +
        `(${sourceMetadata.source_type}, ` +
        `confidence: ${sourceMetadata.confidence_score.toFixed(2)})]\n`
      );
      promptParts.push(source.content + '\n');
      promptParts.push(`[END ${sourceId}]\n\n`);
    }

    // Add instructions for attribution in the response
    promptParts.push(
      '\nQuestion: ' + query + '\n\n' +
      'Answer the question based on the sources provided. ' +
      'For each piece of information in your answer, indicate which ' +
      'source(s) it came from using source numbers [SOURCE_X].'
    );

    return promptParts.join('');
  }

  /**
   * Process a response with attribution markers
   */
  public processAttributedResponse(
    response: string,
    sources: Array<{
      content: string;
      metadata: Record<string, any>;
      relevance_score: number;
      explanation?: string;
      entities?: string[];
    }>
  ): {
    text: string;
    sources: Array<{
      source_id: string;
      title: string;
      reference_count: number;
      relevance_score: number;
      metadata: Record<string, any>;
    }>;
    confidence: number;
    explanation: string;
  } {
    // Extract attribution counts
    const sourceRefs = response.match(/\[SOURCE_(\d+)\]/g) || [];
    const attributionCounts: Record<number, number> = {};
    
    for (const ref of sourceRefs) {
      const match = ref.match(/\[SOURCE_(\d+)\]/);
      if (match) {
        const sourceNum = parseInt(match[1], 10);
        attributionCounts[sourceNum] = (attributionCounts[sourceNum] || 0) + 1;
      }
    }

    // Map sources
    const attributedSources = [];
    for (const [sourceNumStr, count] of Object.entries(attributionCounts)) {
      const sourceNum = parseInt(sourceNumStr, 10);
      if (sourceNum <= sources.length) {
        const sourceIdx = sourceNum - 1; // Convert from 1-indexed to 0-indexed
        const source = sources[sourceIdx];
        attributedSources.push({
          source_id: source.metadata.source_id || `unknown_${sourceIdx}`,
          title: source.metadata.title || 'Unknown Source',
          reference_count: count,
          relevance_score: source.relevance_score || 0.0,
          metadata: source.metadata
        });
      }
    }

    // Calculate overall confidence based on source confidence and relevance
    let confidence = 0.75; // Reasonable default
    if (attributedSources.length > 0) {
      let totalWeight = 0;
      let weightedSum = 0;
      
      for (const source of attributedSources) {
        const refCount = source.reference_count;
        const relevance = source.relevance_score || 0.8;
        const conf = source.metadata.confidence_score || 0.75;
        
        // Weight = reference count * relevance
        const weight = refCount * relevance;
        weightedSum += weight * conf;
        totalWeight += weight;
      }
      
      if (totalWeight > 0) {
        confidence = weightedSum / totalWeight;
      }
      
      // Ensure minimum confidence
      if (confidence < 0.75) {
        confidence = 0.75;
      }
    }

    return {
      text: response,
      sources: attributedSources,
      confidence,
      explanation: 'Attribution based on source references in the response'
    };
  }

  /**
   * Get entity by ID or create a new one if not found
   */
  public getEntity(entityId: string): Entity | null {
    return this.entityStore[entityId] || null;
  }

  /**
   * Get relationship by ID or create a new one if not found
   */
  public getRelationship(relationshipId: string): Relationship | null {
    return this.relationshipStore[relationshipId] || null;
  }

  /**
   * Generate a concept map for visualization
   */
  public generateConceptMap(focusEntities: string[], traversalDepth: number = 2): {
    nodes: Array<{
      id: string;
      label: string;
      type: string;
      properties: Record<string, any>;
    }>;
    edges: Array<{
      id: string;
      source: string;
      target: string;
      label: string;
      properties: Record<string, any>;
    }>;
  } {
    const nodes: Array<{
      id: string;
      label: string;
      type: string;
      properties: Record<string, any>;
    }> = [];
    
    const edges: Array<{
      id: string;
      source: string;
      target: string;
      label: string;
      properties: Record<string, any>;
    }> = [];
    
    // Process each focus entity
    const processedEntities = new Set<string>();
    const entitiesToProcess = [...focusEntities];
    
    // Process entities up to the specified traversal depth
    for (let depth = 0; depth <= traversalDepth; depth++) {
      if (entitiesToProcess.length === 0) break;
      
      const currentBatch = [...entitiesToProcess];
      entitiesToProcess.length = 0;
      
      for (const entityId of currentBatch) {
        if (processedEntities.has(entityId)) continue;
        processedEntities.add(entityId);
        
        // Add entity to nodes
        const entity = this.getEntity(entityId);
        if (entity) {
          nodes.push({
            id: entity.entity_id,
            label: entity.name,
            type: entity.entity_type,
            properties: {
              description: entity.description || '',
              aliases: entity.aliases || [],
              ...entity.metadata
            }
          });
          
          // Find relationships where this entity is source or target
          for (const rel of Object.values(this.relationshipStore)) {
            if (rel.source_entity_id === entityId || rel.target_entity_id === entityId) {
              // Add the relationship
              edges.push({
                id: rel.relationship_id,
                source: rel.source_entity_id,
                target: rel.target_entity_id,
                label: rel.relation_type,
                properties: {
                  confidence: rel.confidence,
                  ...rel.metadata
                }
              });
              
              // Add the other entity to be processed in the next depth
              const otherEntityId = rel.source_entity_id === entityId ? rel.target_entity_id : rel.source_entity_id;
              if (!processedEntities.has(otherEntityId) && depth < traversalDepth) {
                entitiesToProcess.push(otherEntityId);
              }
            }
          }
        }
      }
    }
    
    return { nodes, edges };
  }
}