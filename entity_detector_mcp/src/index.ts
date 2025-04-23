import express from 'express';
import cors from 'cors';
import config from './config';
import logger from './logger';
import routes from './routes';

// Create Express application
const app = express();

// Configure CORS
const corsOptions = {
  origin: config.allowedOrigins.includes('*') ? '*' : config.allowedOrigins,
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization']
};
app.use(cors(corsOptions));

// Parse JSON request bodies
app.use(express.json({ limit: '10mb' }));

// Request logging middleware
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path}`);
  next();
});

// API routes
app.use('/', routes);

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  logger.error(`Error: ${err.message}`);
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error'
  });
});

// Start the server
app.listen(config.port, config.host, () => {
  logger.info(`Entity Detector MCP server started on ${config.host}:${config.port}`);
  logger.info(`Available entity detection models: ${Object.keys(config.models).join(', ')}`);
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down...');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down...');
  process.exit(0);
});

export default app;