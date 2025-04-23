import express from 'express';
import toolsRouter from './tools';

const router = express.Router();

// Health check endpoint
router.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Tools endpoints
router.use('/tools', toolsRouter);

export default router;