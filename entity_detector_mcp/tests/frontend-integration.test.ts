import request from 'supertest';
import express from 'express';
import router from '../src/routes/tools';
import * as entityExtraction from '../src/tools/entity-extraction';

// Mock the entity extraction module
jest.mock('../src/tools/entity-extraction', () => ({
  extractEntities: jest.fn(),
  getDetectorInfo: jest.fn()
}));

/**
 * This test suite focuses on the integration with the frontend,
 * specifically testing the fallback mechanism we implemented
 * in document_viewer.js to handle API errors gracefully.
 */
describe('Frontend Integration', () => {
  let app: express.Application;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Create a test Express app
    app = express();
    app.use(express.json());
    app.use('/tools', router);
  });

  /**
   * Test direct endpoint access that the frontend would use
   * in the fallback mechanism when the MCP server fails
   */
  describe('Direct API Fallback', () => {
    it('should allow direct entity extraction access', async () => {
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
      
      // Test direct API access - simulating frontend fallback
      const response = await request(app)
        .post('/tools/extract_entities/run')
        .send({
          text: 'Contact us at example@test.com',
        });
      
      // Verify response
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockResult);
    });

    it('should handle entity extraction errors gracefully', async () => {
      // Mock extraction failure
      (entityExtraction.extractEntities as jest.Mock).mockRejectedValue(new Error('Service Unavailable'));
      
      // Test request - simulating frontend fallback
      const response = await request(app)
        .post('/tools/extract_entities/run')
        .send({
          text: 'Test text'
        });
      
      // Verify error response format is as expected by frontend
      expect(response.status).toBe(500);
      expect(response.body.error).toBe('Entity extraction failed');
      expect(response.body.message).toBe('Service Unavailable');
    });
  });

  /**
   * Test the statusCheck endpoint that the frontend would use
   * to determine if the entity detector service is running
   */
  describe('Service Status Check', () => {
    it('should return success for detector info request', async () => {
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
      
      // Test status check request
      const response = await request(app)
        .post('/tools/detector_info/run')
        .send({});
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockInfo);
    });
  });

  /**
   * Test the XML-specific entity extraction that would be used
   * by the frontend when processing XML documents
   */
  describe('XML Document Processing', () => {
    it('should extract entities from XML content', async () => {
      // Mock XML-specific extraction
      const mockResult = {
        entities: [
          {
            text: 'John Doe',
            type: 'PERSON',
            confidence: 0.95,
            metadata: {
              xmlElement: 'author'
            }
          },
          {
            text: 'Advanced Guide',
            type: 'WORK_OF_ART',
            confidence: 0.95,
            metadata: {
              xmlElement: 'title'
            }
          },
          {
            text: '$29.99',
            type: 'MONEY',
            confidence: 0.95,
            metadata: {
              xmlElement: 'price'
            }
          }
        ],
        processingTimeMs: 10,
        modelUsed: 'regex'
      };
      (entityExtraction.extractEntities as jest.Mock).mockResolvedValue(mockResult);
      
      // XML test content
      const xmlContent = `
        <document>
          <title>Advanced Guide</title>
          <author>John Doe</author>
          <price>$29.99</price>
          <content>This is a test document.</content>
        </document>
      `;
      
      // Test XML processing request
      const response = await request(app)
        .post('/tools/extract_entities/run')
        .send({
          text: xmlContent
        });
      
      // Verify response
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockResult);
      
      // Verify extraction was called with the XML content
      expect(entityExtraction.extractEntities).toHaveBeenCalledWith(
        xmlContent,
        expect.any(Object)
      );
    });
  });
});