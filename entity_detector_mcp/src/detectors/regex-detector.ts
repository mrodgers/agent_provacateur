import logger from '../logger';
import { Entity, EntityType, DetectionResult, DetectionOptions, EntityDetector } from './types';

interface PatternDefinition {
  [key: string]: string | RegExp;
}

export class RegexDetector implements EntityDetector {
  private patterns: { [key: string]: RegExp };
  private supportedTypes: string[];

  constructor(options: { patterns?: PatternDefinition } = {}) {
    this.patterns = {};
    
    // Default patterns
    const defaultPatterns: PatternDefinition = {
      EMAIL: '\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b',
      PHONE: '\\b(?:\\+?\\d{1,3}[-. ]?)?(?:\\(\\d{1,4}\\)[-. ]?)?\\d{1,4}[-. ]?\\d{1,4}[-. ]?\\d{1,9}\\b',
      URL: '\\b(?:https?://|www\\.)[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&//=]*)',
      DATE: '\\b(?:\\d{1,2}[-/]\\d{1,2}[-/]\\d{2,4}|\\d{4}[-/]\\d{1,2}[-/]\\d{1,2})\\b',
      MONEY: '\\b[$€£¥]\\s?\\d+(?:[.,]\\d+)*\\b|\\b\\d+(?:[.,]\\d+)*\\s?[$€£¥]\\b',
      PERCENT: '\\b\\d+(?:[.,]\\d+)*\\s?%\\b',
      VERSION: '\\bv?\\d+(?:\\.\\d+){1,3}\\b',
      ISBN: '\\b(?:ISBN(?:-1[03])?:?\\s?)?(?=[0-9X]{10}$|(?=(?:[0-9]+[-\\s]){3})[-\\s0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[-\\s]){4})[-\\s0-9]{17}$)(?:97[89][-\\s]?)?[0-9]{1,5}[-\\s]?[0-9]+[-\\s]?[0-9]+[-\\s]?[0-9X]\\b'
    };
    
    // Merge with provided patterns
    const allPatterns = { ...defaultPatterns, ...(options.patterns || {}) };
    
    // Compile patterns to RegExp objects
    Object.entries(allPatterns).forEach(([key, pattern]) => {
      try {
        this.patterns[key] = pattern instanceof RegExp ? 
          pattern : 
          new RegExp(pattern, 'gi');
      } catch (error) {
        logger.error(`Invalid regex pattern for ${key}: ${error}`);
      }
    });
    
    this.supportedTypes = Object.keys(this.patterns);
    logger.info(`Initialized Regex Detector with ${this.supportedTypes.length} patterns`);
  }

  async detectEntities(text: string, options: DetectionOptions = {}): Promise<DetectionResult> {
    const startTime = Date.now();
    const minConfidence = options.minConfidence || 0.5;
    const requestedTypes = options.types || this.supportedTypes;
    
    const entities: Entity[] = [];
    
    try {
      // Only process requested types
      const typesToProcess = requestedTypes.includes('ALL') ? 
        this.supportedTypes : 
        this.supportedTypes.filter(type => requestedTypes.includes(type));
      
      // Apply each pattern
      for (const type of typesToProcess) {
        const pattern = this.patterns[type];
        if (!pattern) continue;
        
        // Reset regex lastIndex to start from beginning
        pattern.lastIndex = 0;
        
        let match;
        while ((match = pattern.exec(text)) !== null) {
          const matchText = match[0];
          entities.push({
            text: matchText,
            type: type,
            startIndex: match.index,
            endIndex: match.index + matchText.length,
            confidence: 0.9, // Regex matches have high confidence
            metadata: options.includeMetadata ? { match } : undefined
          });
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
    return 'regex';
  }

  getSupportedTypes(): string[] {
    return this.supportedTypes;
  }
}