import { describe, it, expect, beforeEach, vi } from 'vitest';
import { ResultCache } from '../../src/utils/cache';

describe('ResultCache', () => {
  let cache: ResultCache;
  
  beforeEach(() => {
    // Create a new cache for each test
    cache = new ResultCache({
      enabled: true,
      ttlSeconds: 60
    });
    
    // Mock timers
    vi.useFakeTimers();
  });
  
  it('should store and retrieve items', () => {
    cache.set('test-key', 'test-value');
    expect(cache.get('test-key')).toBe('test-value');
  });
  
  it('should return null for non-existent keys', () => {
    expect(cache.get('non-existent')).toBeNull();
  });
  
  it('should respect the enabled flag', () => {
    // Create a disabled cache
    const disabledCache = new ResultCache({
      enabled: false,
      ttlSeconds: 60
    });
    
    // Should not store items
    disabledCache.set('test-key', 'test-value');
    expect(disabledCache.get('test-key')).toBeNull();
  });
  
  it('should expire items after TTL', () => {
    cache.set('test-key', 'test-value');
    
    // Check that the item exists initially
    expect(cache.get('test-key')).toBe('test-value');
    
    // Advance time past TTL
    vi.advanceTimersByTime(61 * 1000);
    
    // Item should be expired now
    expect(cache.get('test-key')).toBeNull();
  });
  
  it('should clean expired items', () => {
    // Add some items
    cache.set('key1', 'value1');
    cache.set('key2', 'value2');
    
    // Advance time past TTL
    vi.advanceTimersByTime(61 * 1000);
    
    // Add another item after expiry
    cache.set('key3', 'value3');
    
    // Clean expired items
    cache.cleanExpired();
    
    // Check cache state
    expect(cache.get('key1')).toBeNull();
    expect(cache.get('key2')).toBeNull();
    expect(cache.get('key3')).toBe('value3');
  });
  
  it('should report correct size', () => {
    expect(cache.size).toBe(0);
    
    cache.set('key1', 'value1');
    expect(cache.size).toBe(1);
    
    cache.set('key2', 'value2');
    expect(cache.size).toBe(2);
    
    // Advance time past TTL and clean
    vi.advanceTimersByTime(61 * 1000);
    cache.cleanExpired();
    
    expect(cache.size).toBe(0);
  });
  
  it('should clear all items', () => {
    cache.set('key1', 'value1');
    cache.set('key2', 'value2');
    
    expect(cache.size).toBe(2);
    
    cache.clear();
    
    expect(cache.size).toBe(0);
    expect(cache.get('key1')).toBeNull();
    expect(cache.get('key2')).toBeNull();
  });
});