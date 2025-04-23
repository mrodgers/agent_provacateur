import dotenv from 'dotenv';
import path from 'path';

// Load environment variables from .env file
dotenv.config();

interface Config {
  port: number;
  host: string;
  enableCache: boolean;
  cacheTtlSeconds: number;
  allowedOrigins: string[];
  logLevel: string;
  defaultModel: string;
  models: {
    [key: string]: {
      type: string;
      options?: any;
    };
  };
}

const config: Config = {
  port: parseInt(process.env.PORT || '8082', 10),
  host: process.env.HOST || '0.0.0.0',
  enableCache: process.env.ENABLE_CACHE !== 'false',
  cacheTtlSeconds: parseInt(process.env.CACHE_TTL_SECONDS || '3600', 10),
  allowedOrigins: (process.env.ALLOWED_ORIGINS || '*').split(','),
  logLevel: process.env.LOG_LEVEL || 'info',
  defaultModel: process.env.DEFAULT_MODEL || 'nlp',
  models: {
    nlp: {
      type: 'node-nlp',
      options: {
        language: process.env.NLP_LANGUAGE || 'en'
      }
    },
    regex: {
      type: 'regex',
      options: {
        patterns: {
          EMAIL: '\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b',
          PHONE: '\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b',
          URL: '\\b(https?://|www\\.)[^\\s]+\\b',
          DATE: '\\b\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4}\\b'
        }
      }
    }
  }
};

export default config;