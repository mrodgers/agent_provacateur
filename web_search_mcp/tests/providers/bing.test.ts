import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BingSearchProvider } from '../../src/providers/bing.js';
import { ProviderConfig } from '../../src/providers/base.js';

// Mock the fetch function
global.fetch = vi.fn();

describe('BingSearchProvider', () => {
  let provider: BingSearchProvider;
  let config: ProviderConfig;
  
  beforeEach(() => {
    // Reset mocks
    vi.resetAllMocks();
    
    // Set up config
    config = {
      enabled: true,
      apiKey: 'test-api-key'
    };
    
    // Create provider instance
    provider = new BingSearchProvider(config);
  });
  
  it('should create an instance with valid config', () => {
    expect(provider).toBeDefined();
    expect(provider.name).toBe('bing');
  });
  
  it('should throw if API key is missing', () => {
    expect(() => new BingSearchProvider({ ...config, apiKey: '' })).toThrow('Bing API key is required');
  });
  
  it('should support web search capability', () => {
    expect(provider.hasCapability('web')).toBe(true);
    expect(provider.hasCapability('local')).toBe(false);
  });
  
  it('should throw for local search capability', async () => {
    await expect(provider.searchLocal('local query')).rejects.toThrow('Local search is not implemented for Bing provider');
  });
  
  it('should perform web search with correct parameters', async () => {
    // Mock successful response
    const mockResponse = {
      ok: true,
      json: vi.fn().mockResolvedValue({
        webPages: {
          value: [
            {
              name: 'Test Result 1',
              snippet: 'This is a test result snippet',
              url: 'https://example.com/result1'
            },
            {
              name: 'Test Result 2',
              snippet: 'Another test result snippet',
              url: 'https://example.com/result2',
              language: 'en-US',
              datePublished: '2023-01-01'
            }
          ]
        }
      })
    };
    
    (global.fetch as any).mockResolvedValue(mockResponse);
    
    const results = await provider.searchWeb('test query', 2, 0);
    
    // Verify fetch was called with correct URL and parameters
    expect(global.fetch).toHaveBeenCalledTimes(1);
    const fetchUrl = (global.fetch as any).mock.calls[0][0];
    expect(fetchUrl).toContain('https://api.bing.microsoft.com/v7.0/search');
    expect(fetchUrl).toContain('q=test+query');
    expect(fetchUrl).toContain('count=2');
    expect(fetchUrl).toContain('offset=0');
    
    // Verify headers
    const fetchOptions = (global.fetch as any).mock.calls[0][1];
    expect(fetchOptions.headers['Ocp-Apim-Subscription-Key']).toBe('test-api-key');
    
    // Verify results
    expect(results).toHaveLength(2);
    expect(results[0].title).toBe('Test Result 1');
    expect(results[0].snippet).toBe('This is a test result snippet');
    expect(results[0].url).toBe('https://example.com/result1');
    
    expect(results[1].title).toBe('Test Result 2');
    expect(results[1].language).toBe('en-US');
    expect(results[1].published).toBe('2023-01-01');
  });
  
  it('should handle API errors gracefully', async () => {
    // Mock error response
    const mockResponse = {
      ok: false,
      status: 403,
      text: vi.fn().mockResolvedValue('Invalid API key')
    };
    
    (global.fetch as any).mockResolvedValue(mockResponse);
    
    await expect(provider.searchWeb('test query')).rejects.toThrow('Bing Search API error: 403 Invalid API key');
  });
  
  it('should handle empty results', async () => {
    // Mock empty response
    const mockResponse = {
      ok: true,
      json: vi.fn().mockResolvedValue({})
    };
    
    (global.fetch as any).mockResolvedValue(mockResponse);
    
    const results = await provider.searchWeb('no results query');
    
    expect(results).toHaveLength(0);
  });
});