import express from 'express';
import { extractEntities, getDetectorInfo } from '../tools/entity-extraction';
import logger from '../logger';

const router = express.Router();

// GET /tools - List all available tools
router.get('/', (req, res) => {
  res.json([
    {
      name: 'extract_entities',
      description: 'Extract entities from text',
      parameters: {
        text: { type: 'string', description: 'Text to extract entities from' },
        types: { type: 'array', description: 'Entity types to extract (optional)' },
        minConfidence: { type: 'number', description: 'Minimum confidence threshold (optional)' },
        includeMetadata: { type: 'boolean', description: 'Include additional metadata (optional)' },
        model: { type: 'string', description: 'Detection model to use (optional)' }
      }
    },
    {
      name: 'detector_info',
      description: 'Get information about available entity detection models',
      parameters: {}
    }
  ]);
});

// POST /tools/extract_entities/run - Extract entities from text
router.post('/extract_entities/run', async (req, res) => {
  try {
    const { text, types, minConfidence, includeMetadata, model } = req.body;
    
    if (!text || typeof text !== 'string') {
      return res.status(400).json({ error: 'Text parameter is required' });
    }
    
    logger.info(`Entity extraction request, text length: ${text.length} chars`);
    
    const result = await extractEntities(text, {
      types: types,
      minConfidence: minConfidence,
      includeMetadata: includeMetadata,
      model: model
    });
    
    res.json(result);
  } catch (error) {
    logger.error(`Error extracting entities: ${error}`);
    res.status(500).json({ error: 'Entity extraction failed', message: (error as Error).message });
  }
});

// POST /tools/detector_info/run - Get detector info
router.post('/detector_info/run', (req, res) => {
  try {
    const info = getDetectorInfo();
    res.json(info);
  } catch (error) {
    logger.error(`Error getting detector info: ${error}`);
    res.status(500).json({ error: 'Failed to get detector info', message: (error as Error).message });
  }
});

export default router;