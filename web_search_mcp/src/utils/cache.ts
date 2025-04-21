/**
 * Result cache for storing search results
 */
export interface CacheOptions {
  enabled: boolean;
  ttlSeconds: number;
}

/**
 * Cache item with expiration
 */
interface CacheItem<T> {
  value: T;
  expiry: number;
}

/**
 * In-memory cache implementation with TTL
 */
export class ResultCache {
  private cache: Map<string, CacheItem<any>> = new Map();
  private enabled: boolean;
  private ttlSeconds: number;
  
  constructor(options: CacheOptions) {
    this.enabled = options.enabled;
    this.ttlSeconds = options.ttlSeconds;
    
    // Clean expired items periodically
    setInterval(() => this.cleanExpired(), 60000); // Run every minute
  }
  
  /**
   * Get a value from the cache
   * @param key Cache key
   * @returns Cached value or null if not found or expired
   */
  get<T>(key: string): T | null {
    if (!this.enabled) return null;
    
    const item = this.cache.get(key);
    if (!item) return null;
    
    // Return null if item has expired
    if (item.expiry < Date.now()) {
      this.cache.delete(key);
      return null;
    }
    
    return item.value;
  }
  
  /**
   * Store a value in the cache
   * @param key Cache key
   * @param value Value to cache
   */
  set<T>(key: string, value: T): void {
    if (!this.enabled) return;
    
    const expiry = Date.now() + (this.ttlSeconds * 1000);
    this.cache.set(key, { value, expiry });
  }
  
  /**
   * Remove all expired items from the cache
   */
  cleanExpired(): void {
    if (!this.enabled) return;
    
    const now = Date.now();
    for (const [key, item] of this.cache.entries()) {
      if (item.expiry < now) {
        this.cache.delete(key);
      }
    }
  }
  
  /**
   * Get the number of items in the cache
   */
  get size(): number {
    return this.cache.size;
  }
  
  /**
   * Clear all items from the cache
   */
  clear(): void {
    this.cache.clear();
  }
}