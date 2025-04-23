/**
 * Entity types that can be detected
 */
export enum EntityType {
  PERSON = 'PERSON',
  ORGANIZATION = 'ORGANIZATION',
  LOCATION = 'LOCATION',
  DATETIME = 'DATETIME',
  MONEY = 'MONEY',
  PERCENT = 'PERCENT',
  EMAIL = 'EMAIL',
  PHONE = 'PHONE',
  URL = 'URL',
  PRODUCT = 'PRODUCT',
  EVENT = 'EVENT',
  WORK_OF_ART = 'WORK_OF_ART',
  CONCEPT = 'CONCEPT',
  CUSTOM = 'CUSTOM',
  OTHER = 'OTHER'
}

/**
 * Represents a detected entity
 */
export interface Entity {
  text: string;
  type: EntityType | string;
  startIndex?: number;
  endIndex?: number;
  confidence: number;
  metadata?: Record<string, any>;
}

/**
 * Entity detection result
 */
export interface DetectionResult {
  entities: Entity[];
  processingTimeMs: number;
  modelUsed: string;
}

/**
 * Options for entity detection
 */
export interface DetectionOptions {
  types?: (EntityType | string)[];
  minConfidence?: number;
  includeMetadata?: boolean;
  model?: string;
  language?: string;
}

/**
 * Interface for entity detectors
 */
export interface EntityDetector {
  /**
   * Detect entities in text
   */
  detectEntities(text: string, options?: DetectionOptions): Promise<DetectionResult>;
  
  /**
   * Get the name of this detector
   */
  getName(): string;
  
  /**
   * Get supported entity types
   */
  getSupportedTypes(): (EntityType | string)[];
}