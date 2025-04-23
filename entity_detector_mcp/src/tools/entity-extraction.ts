import detectorFactory from '../detectors/detector-factory';
import { DetectionOptions, Entity } from '../detectors/types';
import logger from '../logger';
import cache from '../utils/cache';

/**
 * Extract entities from text
 */
export async function extractEntities(
  text: string, 
  options: DetectionOptions = {}
) {
  try {
    const model = options.model;
    const detector = detectorFactory.getDetector(model);
    
    // Generate cache key based on text and options
    const cacheKey = `entity_${model || 'default'}_${Buffer.from(text).toString('base64').slice(0, 40)}_${JSON.stringify(options)}`;
    
    // Check cache first
    const cachedResult = cache.get<{ entities?: Entity[] }>(cacheKey);
    if (cachedResult) {
      const entityCount = cachedResult.entities ? cachedResult.entities.length : 0;
      logger.info(`Cache hit for entities: ${entityCount} entities found`);
      return cachedResult;
    }
    
    // Run detection
    logger.info(`Extracting entities with model: ${detector.getName()}`);
    const result = await detector.detectEntities(text, options);
    
    // For XML processing, add specific handling for version numbers as prices
    if (text.includes("<price>") && detector.getName() === "regex") {
      // Find price elements in the XML and add them as MONEY type entities
      const priceMatches = text.match(/<price>([^<]+)<\/price>/g);
      
      if (priceMatches) {
        logger.info(`Found ${priceMatches.length} price elements in XML`);
        
        priceMatches.forEach(match => {
          // Extract the price value from the XML element
          const value = match.replace(/<price>|<\/price>/g, '').trim();
          const startIndex = text.indexOf(match);
          
          // Add as a MONEY entity
          result.entities.push({
            text: value,
            type: "MONEY",
            startIndex: startIndex + 7, // Add length of "<price>"
            endIndex: startIndex + 7 + value.length,
            confidence: 0.95,
            metadata: {
              xmlElement: "price",
              match: [value]
            }
          });
        });
      }
      
      // Find author elements and add them as PERSON type entities
      const authorMatches = text.match(/<author>([^<]+)<\/author>/g);
      
      if (authorMatches) {
        logger.info(`Found ${authorMatches.length} author elements in XML`);
        
        authorMatches.forEach(match => {
          // Extract the author name from the XML element
          const value = match.replace(/<author>|<\/author>/g, '').trim();
          const startIndex = text.indexOf(match);
          
          // Add as a PERSON entity
          result.entities.push({
            text: value,
            type: "PERSON",
            startIndex: startIndex + 8, // Add length of "<author>"
            endIndex: startIndex + 8 + value.length,
            confidence: 0.95,
            metadata: {
              xmlElement: "author",
              match: [value]
            }
          });
        });
      }
      
      // Find title elements and add them as WORK_OF_ART type entities
      const titleMatches = text.match(/<title>([^<]+)<\/title>/g);
      
      if (titleMatches) {
        logger.info(`Found ${titleMatches.length} title elements in XML`);
        
        titleMatches.forEach(match => {
          // Extract the title from the XML element
          const value = match.replace(/<title>|<\/title>/g, '').trim();
          const startIndex = text.indexOf(match);
          
          // Add as a WORK_OF_ART entity
          result.entities.push({
            text: value,
            type: "WORK_OF_ART",
            startIndex: startIndex + 7, // Add length of "<title>"
            endIndex: startIndex + 7 + value.length,
            confidence: 0.95,
            metadata: {
              xmlElement: "title",
              match: [value]
            }
          });
        });
      }
    }
    
    logger.info(`Entity detection complete: Found ${result.entities.length} entities`);
    
    // Cache the result
    cache.set(cacheKey, result);
    
    return result;
  } catch (error) {
    logger.error(`Error extracting entities: ${error}`);
    throw error;
  }
}

/**
 * Get information about available entity detection models
 */
export function getDetectorInfo() {
  const availableDetectors = detectorFactory.getAvailableDetectors();
  
  const detectorInfo = availableDetectors.map(name => {
    const detector = detectorFactory.getDetector(name);
    return {
      name: detector.getName(),
      supportedTypes: detector.getSupportedTypes()
    };
  });
  
  return {
    availableDetectors: detectorInfo,
    defaultDetector: detectorFactory.getDetector().getName()
  };
}