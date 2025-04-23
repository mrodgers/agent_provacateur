import NodeCache from 'node-cache';
import config from '../config';
import logger from '../logger';

class Cache {
  private cache: NodeCache;
  private enabled: boolean;

  constructor() {
    this.cache = new NodeCache({
      stdTTL: config.cacheTtlSeconds,
      checkperiod: config.cacheTtlSeconds * 0.2,
    });
    this.enabled = config.enableCache;
    
    logger.info(`Cache ${this.enabled ? 'enabled' : 'disabled'} with TTL ${config.cacheTtlSeconds}s`);
  }

  /**
   * Get value from cache
   * @param key Cache key
   * @returns The cached value or undefined if not found
   */
  get<T>(key: string): T | undefined {
    if (!this.enabled) return undefined;
    
    const value = this.cache.get<T>(key);
    if (value) {
      logger.debug(`Cache hit for key: ${key}`);
    } else {
      logger.debug(`Cache miss for key: ${key}`);
    }
    return value;
  }

  /**
   * Set value in cache
   * @param key Cache key
   * @param value Value to cache
   * @param ttl Optional TTL in seconds (overrides default)
   */
  set<T>(key: string, value: T, ttl?: number): void {
    if (!this.enabled) return;
    
    this.cache.set(key, value, ttl || config.cacheTtlSeconds);
    logger.debug(`Cached value for key: ${key}`);
  }

  /**
   * Delete a value from cache
   * @param key Cache key
   */
  delete(key: string): void {
    if (!this.enabled) return;
    
    this.cache.del(key);
    logger.debug(`Deleted cache for key: ${key}`);
  }

  /**
   * Clear the entire cache
   */
  clear(): void {
    if (!this.enabled) return;
    
    this.cache.flushAll();
    logger.info('Cache cleared');
  }
}

// Singleton instance
export default new Cache();