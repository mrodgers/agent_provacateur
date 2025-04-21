import dotenv from 'dotenv';
import { SearchProvidersConfig } from './providers/factory.js';
import { RateLimitConfig } from './utils/rate-limiter.js';
import { CacheOptions } from './utils/cache.js';

// Load environment variables
dotenv.config();

/**
 * Application configuration
 */
export interface AppConfig {
  serverName: string;
  serverVersion: string;
  providers: SearchProvidersConfig;
  rateLimit: RateLimitConfig;
  cache: CacheOptions;
}

/**
 * Helper to safely parse boolean values from environment
 */
function parseBoolean(value: string | undefined, defaultValue: boolean): boolean {
  if (value === undefined) return defaultValue;
  return value.toLowerCase() === 'true';
}

/**
 * Helper to safely parse number values from environment
 */
function parseNumber(value: string | undefined, defaultValue: number): number {
  if (value === undefined) return defaultValue;
  const parsed = parseInt(value, 10);
  return isNaN(parsed) ? defaultValue : parsed;
}

/**
 * Load configuration from environment variables
 */
export function loadConfig(): AppConfig {
  return {
    serverName: 'web-search-mcp',
    serverVersion: process.env.npm_package_version || '0.1.0',
    
    providers: {
      defaultProvider: process.env.DEFAULT_SEARCH_PROVIDER || 'brave',
      providers: {
        brave: {
          enabled: Boolean(process.env.BRAVE_API_KEY),
          apiKey: process.env.BRAVE_API_KEY || ''
        },
        google: {
          enabled: Boolean(process.env.GOOGLE_API_KEY && process.env.GOOGLE_SEARCH_CX),
          apiKey: process.env.GOOGLE_API_KEY || '',
          cx: process.env.GOOGLE_SEARCH_CX || ''
        },
        bing: {
          enabled: Boolean(process.env.BING_API_KEY),
          apiKey: process.env.BING_API_KEY || ''
        }
      }
    },
    
    rateLimit: {
      perSecond: parseNumber(process.env.RATE_LIMIT_PER_SECOND, 1),
      perDay: parseNumber(process.env.RATE_LIMIT_PER_DAY, 1000)
    },
    
    cache: {
      enabled: parseBoolean(process.env.ENABLE_CACHE, true),
      ttlSeconds: parseNumber(process.env.CACHE_TTL_SECONDS, 3600)
    }
  };
}