import { extractEntities, getDetectorInfo } from '../src/tools/entity-extraction';
import { EntityType, DetectionResult } from '../src/detectors/types';
import * as detectorFactory from '../src/detectors/detector-factory';
import { RegexDetector } from '../src/detectors/regex-detector';
import { NlpDetector } from '../src/detectors/nlp-detector';

// Mock the detector factory
jest.mock('../src/detectors/detector-factory', () => {
  const originalModule = jest.requireActual('../src/detectors/detector-factory');
  return {
    __esModule: true,
    default: {
      getDetector: jest.fn(),
      getAvailableDetectors: jest.fn(),
    }
  };
});

// Mock cache for testing
jest.mock('../src/utils/cache', () => ({
  get: jest.fn(),
  set: jest.fn()
}));

// Import cache after mocking
import cache from '../src/utils/cache';

describe('Entity Extraction Tool', () => {
  let mockRegexDetector: RegexDetector;
  let mockNlpDetector: NlpDetector;

  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();
    
    // Mock regex detector
    mockRegexDetector = {
      getName: jest.fn().mockReturnValue('regex'),
      getSupportedTypes: jest.fn().mockReturnValue(['EMAIL', 'URL', 'PHONE', 'DATE', 'MONEY']),
      detectEntities: jest.fn().mockResolvedValue({
        entities: [
          {
            text: 'test@example.com',
            type: 'EMAIL',
            startIndex: 10,
            endIndex: 26,
            confidence: 0.9
          },
          {
            text: 'https://example.com',
            type: 'URL',
            startIndex: 40,
            endIndex: 59,
            confidence: 0.9
          }
        ],
        processingTimeMs: 5,
        modelUsed: 'regex'
      } as DetectionResult)
    } as unknown as RegexDetector;

    // Mock NLP detector
    mockNlpDetector = {
      getName: jest.fn().mockReturnValue('nlp'),
      getSupportedTypes: jest.fn().mockReturnValue([
        EntityType.PERSON, 
        EntityType.ORGANIZATION, 
        EntityType.LOCATION
      ]),
      detectEntities: jest.fn().mockResolvedValue({
        entities: [
          {
            text: 'John Smith',
            type: EntityType.PERSON,
            startIndex: 5,
            endIndex: 15,
            confidence: 0.85
          },
          {
            text: 'Google',
            type: EntityType.ORGANIZATION,
            startIndex: 30,
            endIndex: 36,
            confidence: 0.8
          }
        ],
        processingTimeMs: 15,
        modelUsed: 'nlp'
      } as DetectionResult)
    } as unknown as NlpDetector;

    // Setup detector factory mock
    (detectorFactory.default.getDetector as jest.Mock).mockImplementation((model) => {
      if (model === 'nlp') return mockNlpDetector;
      return mockRegexDetector;
    });

    (detectorFactory.default.getAvailableDetectors as jest.Mock).mockReturnValue(['regex', 'nlp']);

    // Setup cache mock
    (cache.get as jest.Mock).mockReturnValue(null);
  });

  describe('extractEntities', () => {
    it('should extract entities using the default detector', async () => {
      // Test input
      const text = 'Contact us at test@example.com or visit https://example.com';
      
      // Run extraction
      const result = await extractEntities(text);
      
      // Verify correct detector was used
      expect(detectorFactory.default.getDetector).toHaveBeenCalledWith(undefined);
      
      // Verify detection was performed
      expect(mockRegexDetector.detectEntities).toHaveBeenCalledWith(text, {});
      
      // Verify results
      expect(result.entities).toHaveLength(2);
      expect(result.entities[0].text).toBe('test@example.com');
      expect(result.entities[0].type).toBe('EMAIL');
      expect(result.entities[1].text).toBe('https://example.com');
      expect(result.entities[1].type).toBe('URL');
    });

    it('should extract entities using the specified model', async () => {
      // Test input
      const text = 'John Smith works at Google in New York.';
      const options = { model: 'nlp' };
      
      // Run extraction
      const result = await extractEntities(text, options);
      
      // Verify correct detector was used
      expect(detectorFactory.default.getDetector).toHaveBeenCalledWith('nlp');
      
      // Verify detection was performed
      expect(mockNlpDetector.detectEntities).toHaveBeenCalledWith(text, options);
      
      // Verify results
      expect(result.entities).toHaveLength(2);
      expect(result.entities[0].text).toBe('John Smith');
      expect(result.entities[0].type).toBe(EntityType.PERSON);
      expect(result.entities[1].text).toBe('Google');
      expect(result.entities[1].type).toBe(EntityType.ORGANIZATION);
    });

    it('should use cached results when available', async () => {
      // Setup cache hit
      const cachedResult = {
        entities: [
          {
            text: 'cached@example.com',
            type: 'EMAIL',
            startIndex: 10,
            endIndex: 26,
            confidence: 0.9
          }
        ]
      };
      (cache.get as jest.Mock).mockReturnValue(cachedResult);
      
      // Test input
      const text = 'Contact us at cached@example.com';
      
      // Run extraction
      const result = await extractEntities(text);
      
      // Verify cache was checked
      expect(cache.get).toHaveBeenCalled();
      
      // Verify detector was not called
      expect(mockRegexDetector.detectEntities).not.toHaveBeenCalled();
      
      // Verify cached results were returned
      expect(result).toBe(cachedResult);
    });

    it('should process XML specific elements', async () => {
      // Mock regex detector for XML processing
      mockRegexDetector.detectEntities = jest.fn().mockResolvedValue({
        entities: [],
        processingTimeMs: 5,
        modelUsed: 'regex'
      });
      
      // Test input with XML elements
      const xmlText = '<document><price>$199.99</price><author>Jane Doe</author><title>Test Document</title></document>';
      
      // Run extraction
      const result = await extractEntities(xmlText);
      
      // Verify results include XML entities
      expect(result.entities).toHaveLength(3);
      
      // Check price entity
      const priceEntity = result.entities.find(e => e.type === 'MONEY');
      expect(priceEntity).toBeDefined();
      expect(priceEntity?.text).toBe('$199.99');
      expect(priceEntity?.metadata?.xmlElement).toBe('price');
      
      // Check author entity
      const authorEntity = result.entities.find(e => e.type === 'PERSON');
      expect(authorEntity).toBeDefined();
      expect(authorEntity?.text).toBe('Jane Doe');
      expect(authorEntity?.metadata?.xmlElement).toBe('author');
      
      // Check title entity
      const titleEntity = result.entities.find(e => e.type === 'WORK_OF_ART');
      expect(titleEntity).toBeDefined();
      expect(titleEntity?.text).toBe('Test Document');
      expect(titleEntity?.metadata?.xmlElement).toBe('title');
    });

    it('should handle errors during entity detection', async () => {
      // Setup error case
      mockRegexDetector.detectEntities = jest.fn().mockRejectedValue(new Error('Test error'));
      
      // Test input
      const text = 'Test text';
      
      // Verify error is propagated
      await expect(extractEntities(text)).rejects.toThrow('Test error');
    });
  });

  describe('getDetectorInfo', () => {
    it('should return information about available detectors', () => {
      // Mock supported types for testing
      (mockRegexDetector.getSupportedTypes as jest.Mock).mockReturnValue(['EMAIL', 'URL', 'PHONE']);
      (mockNlpDetector.getSupportedTypes as jest.Mock).mockReturnValue([EntityType.PERSON, EntityType.ORGANIZATION]);
      
      // Get detector info
      const info = getDetectorInfo();
      
      // Verify correct information is returned
      expect(info.availableDetectors).toHaveLength(2);
      expect(info.availableDetectors[0].name).toBe('regex');
      expect(info.availableDetectors[0].supportedTypes).toEqual(['EMAIL', 'URL', 'PHONE']);
      expect(info.availableDetectors[1].name).toBe('nlp');
      expect(info.availableDetectors[1].supportedTypes).toEqual([EntityType.PERSON, EntityType.ORGANIZATION]);
      expect(info.defaultDetector).toBe('regex');
    });
  });
});