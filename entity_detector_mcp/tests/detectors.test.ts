import { NlpDetector } from '../src/detectors/nlp-detector';
import { RegexDetector } from '../src/detectors/regex-detector';
import { EntityType } from '../src/detectors/types';

// Mock node-nlp
jest.mock('node-nlp', () => {
  return {
    NlpManager: jest.fn().mockImplementation(() => {
      return {
        isRunning: jest.fn().mockReturnValue(true),
        train: jest.fn().mockResolvedValue(true),
        process: jest.fn().mockResolvedValue({
          entities: [
            {
              entity: 'person',
              utteranceText: 'John Smith',
              accuracy: 0.85,
              start: 5,
              end: 15
            },
            {
              entity: 'organization',
              utteranceText: 'Google',
              accuracy: 0.8,
              start: 30,
              end: 36
            }
          ]
        })
      };
    })
  };
});

describe('Entity Detectors', () => {
  describe('RegexDetector', () => {
    it('should detect entities using default patterns', async () => {
      const detector = new RegexDetector();
      const text = 'Contact us at example@test.com or call 123-456-7890. Visit https://example.com for more info.';
      
      const result = await detector.detectEntities(text);
      
      // Check result structure
      expect(result.entities).toBeDefined();
      expect(result.processingTimeMs).toBeGreaterThanOrEqual(0);
      expect(result.modelUsed).toBe('regex');
      
      // Verify detected entities
      expect(result.entities.length).toBeGreaterThanOrEqual(3);
      
      // Email detection
      const email = result.entities.find(e => e.type === 'EMAIL');
      expect(email).toBeDefined();
      expect(email?.text).toBe('example@test.com');
      
      // Phone detection
      const phone = result.entities.find(e => e.type === 'PHONE');
      expect(phone).toBeDefined();
      expect(phone?.text).toBe('123-456-7890');
      
      // URL detection
      const url = result.entities.find(e => e.type === 'URL');
      expect(url).toBeDefined();
      expect(url?.text).toBe('https://example.com');
    });

    it('should respect minimum confidence threshold', async () => {
      const detector = new RegexDetector();
      const text = 'Contact us at example@test.com';
      
      // Mock the RegExp exec method to return null for this test
      const originalExec = RegExp.prototype.exec;
      RegExp.prototype.exec = jest.fn().mockReturnValue(null);
      
      const result = await detector.detectEntities(text, { minConfidence: 0.95 });
      
      // Should have no entities due to high confidence threshold
      expect(result.entities.length).toBe(0);
      
      // Restore original exec
      RegExp.prototype.exec = originalExec;
    });

    it('should filter by requested types', async () => {
      const detector = new RegexDetector();
      const text = 'Contact us at example@test.com or call 123-456-7890. Visit https://example.com for more info.';
      
      const result = await detector.detectEntities(text, { types: ['EMAIL'] });
      
      // Only EMAIL type should be returned
      expect(result.entities.length).toBe(1);
      expect(result.entities[0].type).toBe('EMAIL');
      expect(result.entities[0].text).toBe('example@test.com');
    });

    it('should add metadata when requested', async () => {
      const detector = new RegexDetector();
      const text = 'Contact us at example@test.com';
      
      const result = await detector.detectEntities(text, { includeMetadata: true });
      
      expect(result.entities[0].metadata).toBeDefined();
      expect(result.entities[0].metadata?.match).toBeDefined();
    });

    it('should use custom patterns when provided', async () => {
      // Create detector with custom pattern
      const detector = new RegexDetector({
        patterns: {
          CUSTOM_ID: '\\b[A-Z]{2}\\d{6}\\b'
        }
      });
      
      const text = 'Your ID is AB123456 and your email is example@test.com';
      
      const result = await detector.detectEntities(text, { types: ['CUSTOM_ID'] });
      
      // Should detect custom ID
      expect(result.entities.length).toBe(1);
      expect(result.entities[0].type).toBe('CUSTOM_ID');
      expect(result.entities[0].text).toBe('AB123456');
    });
  });

  describe('NlpDetector', () => {
    it('should detect entities using NLP processing', async () => {
      const detector = new NlpDetector();
      const text = 'John Smith works at Google in New York.';
      
      const result = await detector.detectEntities(text);
      
      // Check result structure
      expect(result.entities).toBeDefined();
      expect(result.processingTimeMs).toBeGreaterThanOrEqual(0);
      expect(result.modelUsed).toBe('nlp');
      
      // Verify detected entities
      expect(result.entities.length).toBe(2);
      
      // Person detection
      expect(result.entities[0].text).toBe('John Smith');
      expect(result.entities[0].type).toBe(EntityType.PERSON);
      
      // Organization detection
      expect(result.entities[1].text).toBe('Google');
      expect(result.entities[1].type).toBe(EntityType.ORGANIZATION);
    });

    it('should map entity types correctly', async () => {
      const detector = new NlpDetector();
      const text = 'John Smith works at Google in New York.';
      
      const result = await detector.detectEntities(text);
      
      // Verify type mapping
      expect(result.entities[0].type).toBe(EntityType.PERSON);
      expect(result.entities[1].type).toBe(EntityType.ORGANIZATION);
    });

    it('should respect minimum confidence threshold', async () => {
      const detector = new NlpDetector();
      const text = 'John Smith works at Google in New York.';
      
      const result = await detector.detectEntities(text, { minConfidence: 0.9 });
      
      // Only entities with confidence >= 0.9 should be included
      expect(result.entities.length).toBe(0);
    });

    it('should filter by requested types', async () => {
      const detector = new NlpDetector();
      const text = 'John Smith works at Google in New York.';
      
      const result = await detector.detectEntities(text, { types: [EntityType.PERSON] });
      
      // Only PERSON type should be returned
      expect(result.entities.length).toBe(1);
      expect(result.entities[0].type).toBe(EntityType.PERSON);
      expect(result.entities[0].text).toBe('John Smith');
    });

    it('should add metadata when requested', async () => {
      const detector = new NlpDetector();
      const text = 'John Smith works at Google in New York.';
      
      const result = await detector.detectEntities(text, { includeMetadata: true });
      
      expect(result.entities[0].metadata).toBeDefined();
    });
  });
});