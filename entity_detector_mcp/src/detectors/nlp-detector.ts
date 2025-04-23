import { NlpManager } from 'node-nlp';
import logger from '../logger';
import { Entity, EntityType, DetectionResult, DetectionOptions, EntityDetector } from './types';

export class NlpDetector implements EntityDetector {
  private manager: NlpManager;
  private readonly supportedTypes: EntityType[];

  constructor(options: { language?: string } = {}) {
    const language = options.language || 'en';
    this.manager = new NlpManager({ languages: [language] });
    
    // Add built-in entity recognition
    this.supportedTypes = [
      EntityType.PERSON,
      EntityType.ORGANIZATION,
      EntityType.LOCATION,
      EntityType.DATETIME,
      EntityType.MONEY,
      EntityType.PERCENT,
      EntityType.EMAIL,
      EntityType.URL,
      EntityType.PHONE
    ];
    
    logger.info(`Initialized NLP Detector with language: ${language}`);
  }

  async detectEntities(text: string, options: DetectionOptions = {}): Promise<DetectionResult> {
    const startTime = Date.now();
    const minConfidence = options.minConfidence || 0.5;
    const requestedTypes = options.types || this.supportedTypes;
    
    try {
      // Ensure the NLP manager is trained
      if (!this.manager.isRunning()) {
        await this.manager.train();
      }
      
      // Process the text
      const result = await this.manager.process('en', text);
      const entities: Entity[] = [];
      
      // Extract entities from the result
      if (result.entities && result.entities.length > 0) {
        for (const entity of result.entities) {
          const type = this.mapEntityType(entity.entity);
          
          // Only include requested types
          if (
            requestedTypes.includes('ALL') || 
            requestedTypes.includes(type)
          ) {
            if (entity.accuracy >= minConfidence) {
              entities.push({
                text: entity.utteranceText,
                type: type,
                startIndex: entity.start,
                endIndex: entity.end,
                confidence: entity.accuracy,
                metadata: options.includeMetadata ? entity : undefined
              });
            }
          }
        }
      }
      
      const processingTimeMs = Date.now() - startTime;
      logger.debug(`Detected ${entities.length} entities in ${processingTimeMs}ms`);
      
      return {
        entities,
        processingTimeMs,
        modelUsed: this.getName()
      };
    } catch (error) {
      logger.error(`Error detecting entities: ${error}`);
      throw error;
    }
  }

  getName(): string {
    return 'nlp';
  }

  getSupportedTypes(): EntityType[] {
    return this.supportedTypes;
  }

  private mapEntityType(type: string): EntityType {
    switch (type.toLowerCase()) {
      case 'person':
        return EntityType.PERSON;
      case 'organization':
      case 'org':
        return EntityType.ORGANIZATION;
      case 'location':
      case 'place':
        return EntityType.LOCATION;
      case 'date':
      case 'time':
      case 'datetime':
        return EntityType.DATETIME;
      case 'money':
      case 'currency':
        return EntityType.MONEY;
      case 'percent':
      case 'percentage':
        return EntityType.PERCENT;
      case 'email':
        return EntityType.EMAIL;
      case 'url':
        return EntityType.URL;
      case 'phone':
      case 'phonenumber':
        return EntityType.PHONE;
      default:
        return EntityType.OTHER;
    }
  }
}