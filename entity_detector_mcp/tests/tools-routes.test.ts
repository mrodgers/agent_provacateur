import express from 'express';
import request from 'supertest';
import router from '../src/routes/tools';
import * as entityExtraction from '../src/tools/entity-extraction';

// Mock the entity extraction module
jest.mock('../src/tools/entity-extraction', () => ({
  extractEntities: jest.fn(),
  getDetectorInfo: jest.fn()
}));

describe('Tools API Routes', () => {
  let app: express.Application;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Create a test Express app
    app = express();
    app.use(express.json());
    app.use('/tools', router);
  });

  describe('GET /tools', () => {
    it('should return a list of available tools', async () => {
      const response = await request(app).get('/tools');
      
      expect(response.status).toBe(200);
      expect(response.body).toBeInstanceOf(Array);
      expect(response.body.length).toBe(2);
      expect(response.body[0].name).toBe('extract_entities');
      expect(response.body[1].name).toBe('detector_info');
    });
  });

  describe('POST /tools/extract_entities/run', () => {
    it('should extract entities from text', async () => {
      // Mock successful extraction
      const mockResult = {
        entities: [
          {
            text: 'example@test.com',
            type: 'EMAIL',
            confidence: 0.9
          }
        ],
        processingTimeMs: 5,
        modelUsed: 'regex'
      };
      (entityExtraction.extractEntities as jest.Mock).mockResolvedValue(mockResult);
      
      // Test request
      const response = await request(app)
        .post('/tools/extract_entities/run')
        .send({
          text: 'Contact us at example@test.com',
          minConfidence: 0.7
        });
      
      // Verify response
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockResult);
      
      // Verify extraction call
      expect(entityExtraction.extractEntities).toHaveBeenCalledWith(
        'Contact us at example@test.com',
        expect.objectContaining({ minConfidence: 0.7 })
      );
    });

    it('should return 400 if text is missing', async () => {
      const response = await request(app)
        .post('/tools/extract_entities/run')
        .send({
          minConfidence: 0.7
        });
      
      expect(response.status).toBe(400);
      expect(response.body.error).toBeDefined();
    });

    it('should return 500 if extraction fails', async () => {
      // Mock extraction failure
      (entityExtraction.extractEntities as jest.Mock).mockRejectedValue(new Error('Test error'));
      
      const response = await request(app)
        .post('/tools/extract_entities/run')
        .send({
          text: 'Test text'
        });
      
      expect(response.status).toBe(500);
      expect(response.body.error).toBeDefined();
      expect(response.body.message).toBe('Test error');
    });
  });

  describe('POST /tools/detector_info/run', () => {
    it('should return detector info', async () => {
      // Mock detector info
      const mockInfo = {
        availableDetectors: [
          {
            name: 'regex',
            supportedTypes: ['EMAIL', 'URL']
          }
        ],
        defaultDetector: 'regex'
      };
      (entityExtraction.getDetectorInfo as jest.Mock).mockReturnValue(mockInfo);
      
      const response = await request(app)
        .post('/tools/detector_info/run')
        .send({});
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockInfo);
    });

    it('should return 500 if getting info fails', async () => {
      // Mock failure
      (entityExtraction.getDetectorInfo as jest.Mock).mockImplementation(() => {
        throw new Error('Test error');
      });
      
      const response = await request(app)
        .post('/tools/detector_info/run')
        .send({});
      
      expect(response.status).toBe(500);
      expect(response.body.error).toBeDefined();
      expect(response.body.message).toBe('Test error');
    });
  });
});