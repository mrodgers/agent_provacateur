import NodeCache from 'node-cache';
import { config } from '../config';
import { logger } from './logger';

// Create cache instance
export const cache = new NodeCache({
  stdTTL: config.CACHE_TTL,  // default time to live in seconds
  checkperiod: 60,           // check for expired keys every 60 seconds
  maxKeys: config.MAX_CACHE_SIZE
});

/**
 * Get item from cache
 * @param key Cache key
 * @returns Cached value or undefined if not found
 */
export function getCacheItem<T>(key: string): T | undefined {
  if (!config.ENABLE_CACHE) return undefined;
  return cache.get<T>(key);
}

/**
 * Set item in cache
 * @param key Cache key
 * @param value Value to cache
 * @param ttl Time to live in seconds (optional, uses default if not specified)
 * @returns true if successful, false otherwise
 */
export function setCacheItem<T>(key: string, value: T, ttl?: number): boolean {
  if (!config.ENABLE_CACHE) return false;
  // Pass ttl as undefined if not provided, or as a number if provided
  return ttl === undefined ? cache.set(key, value) : cache.set(key, value, ttl);
}

/**
 * Delete item from cache
 * @param key Cache key
 * @returns Number of deleted entries (usually 0 or 1)
 */
export function deleteCacheItem(key: string): number {
  return cache.del(key);
}

/**
 * Clear entire cache
 * @returns void
 */
export function clearCache(): void {
  cache.flushAll();
  logger.info('Cache cleared');
}

/**
 * Get cache stats
 * @returns Cache statistics
 */
export function getCacheStats(): NodeCache.Stats {
  return cache.getStats();
}