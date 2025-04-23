import config from '../config';
import logger from '../logger';
import { EntityDetector } from './types';
import { NlpDetector } from './nlp-detector';
import { RegexDetector } from './regex-detector';

class DetectorFactory {
  private detectors: Map<string, EntityDetector> = new Map();

  constructor() {
    this.initializeDetectors();
  }

  /**
   * Initialize all configured detectors
   */
  private initializeDetectors(): void {
    // Initialize all detectors from config
    for (const [name, modelConfig] of Object.entries(config.models)) {
      try {
        let detector: EntityDetector;
        
        switch (modelConfig.type) {
          case 'node-nlp':
            detector = new NlpDetector(modelConfig.options);
            break;
          case 'regex':
            detector = new RegexDetector(modelConfig.options);
            break;
          default:
            logger.warn(`Unknown detector type: ${modelConfig.type}`);
            continue;
        }
        
        this.detectors.set(name, detector);
        logger.info(`Initialized detector: ${name}`);
      } catch (error) {
        logger.error(`Failed to initialize detector ${name}: ${error}`);
      }
    }
    
    logger.info(`Initialized ${this.detectors.size} entity detectors`);
  }

  /**
   * Get a detector by name
   * @param name Detector name
   * @returns EntityDetector instance
   */
  getDetector(name?: string): EntityDetector {
    const detectorName = name || config.defaultModel;
    
    const detector = this.detectors.get(detectorName);
    if (!detector) {
      // Fall back to default detector if requested one is not found
      logger.warn(`Detector '${detectorName}' not found, using default: ${config.defaultModel}`);
      const defaultDetector = this.detectors.get(config.defaultModel);
      
      if (!defaultDetector) {
        throw new Error(`Neither requested detector '${detectorName}' nor default detector '${config.defaultModel}' found`);
      }
      
      return defaultDetector;
    }
    
    return detector;
  }

  /**
   * Get all available detector names
   * @returns Array of detector names
   */
  getAvailableDetectors(): string[] {
    return Array.from(this.detectors.keys());
  }
}

// Singleton instance
export default new DetectorFactory();