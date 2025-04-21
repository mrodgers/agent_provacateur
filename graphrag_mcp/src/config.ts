import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

interface Config {
  PORT: number;
  VECTOR_DB_URL: string;
  ENABLE_CACHE: boolean;
  MAX_CACHE_SIZE: number;
  CACHE_TTL: number;
  MAX_RESULTS: number;
  MIN_CONFIDENCE: number;
  TRAVERSAL_DEPTH: number;
  RATE_LIMIT_WINDOW: number;
  RATE_LIMIT_MAX: number;
  LOG_LEVEL: string;
}

export const config: Config = {
  PORT: parseInt(process.env.PORT || '8083', 10),
  VECTOR_DB_URL: process.env.VECTOR_DB_URL || 'http://localhost:6333',
  ENABLE_CACHE: process.env.ENABLE_CACHE !== 'false',
  MAX_CACHE_SIZE: parseInt(process.env.MAX_CACHE_SIZE || '1000', 10),
  CACHE_TTL: parseInt(process.env.CACHE_TTL || '3600', 10), // in seconds
  MAX_RESULTS: parseInt(process.env.MAX_RESULTS || '10', 10),
  MIN_CONFIDENCE: parseFloat(process.env.MIN_CONFIDENCE || '0.5'),
  TRAVERSAL_DEPTH: parseInt(process.env.TRAVERSAL_DEPTH || '2', 10),
  RATE_LIMIT_WINDOW: parseInt(process.env.RATE_LIMIT_WINDOW || '60000', 10), // in milliseconds
  RATE_LIMIT_MAX: parseInt(process.env.RATE_LIMIT_MAX || '100', 10),
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',
};