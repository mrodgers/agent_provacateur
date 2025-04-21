import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { configureRoutes } from './routes';
import { GraphRAGService } from './services/graphrag-service';
import { config } from './config';
import { logger } from './utils/logger';
import path from 'path';

// Create Express application
const app = express();

// Apply middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Create logs directory if it doesn't exist
try {
  const fs = require('fs');
  if (!fs.existsSync('logs')) {
    fs.mkdirSync('logs');
    logger.info('Created logs directory');
  }
} catch (error) {
  logger.error(`Error creating logs directory: ${error}`);
}

// Create GraphRAG service
const graphragService = new GraphRAGService({
  vectorDbUrl: config.VECTOR_DB_URL,
  maxResults: config.MAX_RESULTS,
  minConfidence: config.MIN_CONFIDENCE,
  traversalDepth: config.TRAVERSAL_DEPTH,
  cacheEnabled: config.ENABLE_CACHE
});

// Configure routes
configureRoutes(app, graphragService);

// Static files (for documentation)
app.use('/docs', express.static(path.join(__dirname, '../docs')));

// Default route
app.get('/', (req, res) => {
  res.send('GraphRAG MCP Server is running. See /api/info for more details.');
});

// Start server
const PORT = config.PORT;
app.listen(PORT, () => {
  logger.info(`GraphRAG MCP Server running on port ${PORT}`);
  logger.info(`Server configuration: ${JSON.stringify(config)}`);
});