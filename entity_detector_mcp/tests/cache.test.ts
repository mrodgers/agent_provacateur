import cache from '../src/utils/cache';
import NodeCache from 'node-cache';

// Mock the NodeCache
jest.mock('node-cache');

// Mock the config and logger
jest.mock('../src/config', () => ({
  cacheTtlSeconds: 600,
  enableCache: true
}));

describe('Cache Utility', () => {
  beforeEach(() => {
    // Clear mocks
    jest.clearAllMocks();
    
    // Clear the cache before each test
    cache.clear();
  });

  it('should store and retrieve values', () => {
    const key = 'test_key';
    const value = { data: 'test_value' };
    
    // Mock NodeCache get method
    (NodeCache.prototype.get as jest.Mock).mockReturnValue(value);
    
    // Store value
    cache.set(key, value);
    
    // Verify set was called
    expect(NodeCache.prototype.set).toHaveBeenCalledWith(key, value, expect.any(Number));
    
    // Retrieve value
    const retrievedValue = cache.get(key);
    
    // Verify get was called
    expect(NodeCache.prototype.get).toHaveBeenCalledWith(key);
    
    // Verify value
    expect(retrievedValue).toEqual(value);
  });

  it('should return undefined for non-existent keys', () => {
    const key = 'non_existent_key';
    
    // Mock cache miss
    (NodeCache.prototype.get as jest.Mock).mockReturnValue(undefined);
    
    // Retrieve non-existent value
    const retrievedValue = cache.get(key);
    
    // Verify
    expect(retrievedValue).toBeUndefined();
  });

  it('should respect TTL settings', () => {
    const key = 'ttl_test_key';
    const value = { data: 'ttl_test_value' };
    const customTtl = 100;
    
    // Store value with custom TTL
    cache.set(key, value, customTtl);
    
    // Verify set was called with custom TTL
    expect(NodeCache.prototype.set).toHaveBeenCalledWith(key, value, customTtl);
  });

  it('should delete keys', () => {
    const key = 'delete_test_key';
    
    // Delete key
    cache.delete(key);
    
    // Verify del was called
    expect(NodeCache.prototype.del).toHaveBeenCalledWith(key);
  });

  it('should clear all keys', () => {
    // Clear cache
    cache.clear();
    
    // Verify flushAll was called
    expect(NodeCache.prototype.flushAll).toHaveBeenCalled();
  });

  it('should not perform operations when cache is disabled', () => {
    // Reset mock calls first
    jest.clearAllMocks();
    
    // Testing with a temporary mock of the actual cache instance
    const originalEnabled = (cache as any).enabled;
    try {
      // Temporarily disable cache
      (cache as any).enabled = false;
      
      // Test operations
      cache.get('key');
      cache.set('key', 'value');
      cache.delete('key');
      cache.clear();
      
      // Verify no NodeCache methods were called
      expect(NodeCache.prototype.get).not.toHaveBeenCalled();
      expect(NodeCache.prototype.set).not.toHaveBeenCalled();
      expect(NodeCache.prototype.del).not.toHaveBeenCalled();
      expect(NodeCache.prototype.flushAll).not.toHaveBeenCalled();
    } finally {
      // Restore original state
      (cache as any).enabled = originalEnabled;
    }
  });
});