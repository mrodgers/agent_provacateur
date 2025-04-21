import { describe, it, expect, vi, beforeEach } from 'vitest';
import { GoogleSearchProvider } from '../../src/providers/google.js';
import { ProviderConfig } from '../../src/providers/base.js';

// Mock the fetch function
global.fetch = vi.fn();

describe('GoogleSearchProvider', () => {
  let provider: GoogleSearchProvider;
  let config: ProviderConfig & { cx: string };
  
  beforeEach(() => {
    // Reset mocks
    vi.resetAllMocks();
    
    // Set up config
    config = {
      enabled: true,
      apiKey: 'test-api-key',
      cx: 'test-cx-id'
    };
    
    // Create provider instance
    provider = new GoogleSearchProvider(config);
  });
  
  it('should create an instance with valid config', () => {
    expect(provider).toBeDefined();
    expect(provider.name).toBe('google');
  });
  
  it('should throw if API key is missing', () => {
    expect(() => new GoogleSearchProvider({ ...config, apiKey: '' })).toThrow('Google API key is required');
  });
  
  it('should throw if CX is missing', () => {
    expect(() => new GoogleSearchProvider({ ...config, cx: '' })).toThrow('Google Custom Search Engine ID (cx) is required');
  });
  
  it('should support web search capability', () => {
    expect(provider.hasCapability('web')).toBe(true);
    expect(provider.hasCapability('local')).toBe(false);
  });
  
  it('should perform web search with correct parameters', async () => {
    // Mock successful response
    const mockResponse = {
      ok: true,
      json: vi.fn().mockResolvedValue({
        items: [
          {
            title: 'Test Result 1',
            snippet: 'This is a test result snippet',
            link: 'https://example.com/result1'
          },
          {
            title: 'Test Result 2',
            snippet: 'Another test result snippet',
            link: 'https://example.com/result2',
            pagemap: {
              metatags: [{ 'og:locale': 'en_US' }],
              article: [{ datePublished: '2023-01-01' }]
            }
          }
        ]
      })
    };
    
    (global.fetch as any).mockResolvedValue(mockResponse);
    
    const results = await provider.searchWeb('test query', 2, 0);
    
    // Verify fetch was called with correct URL and parameters
    expect(global.fetch).toHaveBeenCalledTimes(1);
    const fetchUrl = (global.fetch as any).mock.calls[0][0];
    expect(fetchUrl).toContain('https://www.googleapis.com/customsearch/v1');
    expect(fetchUrl).toContain('key=test-api-key');
    expect(fetchUrl).toContain('cx=test-cx-id');
    expect(fetchUrl).toContain('q=test+query');
    expect(fetchUrl).toContain('num=2');
    expect(fetchUrl).toContain('start=1');
    
    // Verify results
    expect(results).toHaveLength(2);
    expect(results[0].title).toBe('Test Result 1');
    expect(results[0].snippet).toBe('This is a test result snippet');
    expect(results[0].url).toBe('https://example.com/result1');
    
    expect(results[1].title).toBe('Test Result 2');
    expect(results[1].language).toBe('en_US');
    expect(results[1].published).toBe('2023-01-01');
  });
  
  it('should handle API errors gracefully', async () => {
    // Mock error response
    const mockResponse = {
      ok: false,
      status: 403,
      text: vi.fn().mockResolvedValue('API quota exceeded')
    };
    
    (global.fetch as any).mockResolvedValue(mockResponse);
    
    await expect(provider.searchWeb('test query')).rejects.toThrow('Google Search API error: 403 API quota exceeded');
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