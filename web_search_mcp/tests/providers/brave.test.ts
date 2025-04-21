import { describe, it, expect, beforeEach, vi } from 'vitest';
import { BraveSearchProvider } from '../../src/providers/brave';

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('BraveSearchProvider', () => {
  let provider: BraveSearchProvider;
  
  beforeEach(() => {
    // Reset mocks
    mockFetch.mockReset();
    
    // Create a new provider for each test
    provider = new BraveSearchProvider({
      enabled: true,
      apiKey: 'test-api-key'
    });
  });
  
  it('should create the provider correctly', () => {
    expect(provider.name).toBe('brave');
    expect(provider.hasCapability('web')).toBe(true);
    expect(provider.hasCapability('local')).toBe(true);
    expect(provider.hasCapability('unknown')).toBe(false);
  });
  
  it('should throw if API key is missing', () => {
    expect(() => {
      new BraveSearchProvider({
        enabled: true,
        apiKey: ''
      });
    }).toThrow('Brave API key is required');
  });
  
  it('should perform web search correctly', async () => {
    // Mock successful API response
    const mockResponse = {
      web: {
        results: [
          {
            title: 'Test Result 1',
            description: 'Test Description 1',
            url: 'https://example.com/1',
            language: 'en',
            published: '2023-01-01'
          },
          {
            title: 'Test Result 2',
            description: 'Test Description 2',
            url: 'https://example.com/2'
          }
        ]
      }
    };
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });
    
    const results = await provider.searchWeb('test query', 10, 0);
    
    // Check that fetch was called correctly
    expect(mockFetch).toHaveBeenCalledTimes(1);
    expect(mockFetch.mock.calls[0][0].toString()).toContain('https://api.search.brave.com/res/v1/web/search');
    expect(mockFetch.mock.calls[0][0].toString()).toContain('q=test+query'); // Node's URL encodes spaces as + by default
    expect(mockFetch.mock.calls[0][0].toString()).toContain('count=10');
    expect(mockFetch.mock.calls[0][0].toString()).toContain('offset=0');
    
    // Check that the headers include the API key
    expect(mockFetch.mock.calls[0][1].headers['X-Subscription-Token']).toBe('test-api-key');
    
    // Check results
    expect(results).toHaveLength(2);
    expect(results[0].title).toBe('Test Result 1');
    expect(results[0].snippet).toBe('Test Description 1');
    expect(results[0].url).toBe('https://example.com/1');
    expect(results[0].language).toBe('en');
    expect(results[0].published).toBe('2023-01-01');
    
    expect(results[1].title).toBe('Test Result 2');
    expect(results[1].snippet).toBe('Test Description 2');
    expect(results[1].url).toBe('https://example.com/2');
  });
  
  it('should handle API errors in web search', async () => {
    // Mock failed API response
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      statusText: 'Unauthorized'
    });
    
    // The search should throw an error
    await expect(provider.searchWeb('test query')).rejects.toThrow('Brave API error: 401 Unauthorized');
  });
  
  it('should handle empty web search results', async () => {
    // Mock empty API response
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({})
    });
    
    const results = await provider.searchWeb('test query');
    
    expect(results).toHaveLength(0);
  });
  
  it('should format results correctly when fields are missing', async () => {
    // Mock response with missing fields
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        web: {
          results: [
            { /* No fields */ },
            { title: 'Only Title' }
          ]
        }
      })
    });
    
    const results = await provider.searchWeb('test query');
    
    expect(results).toHaveLength(2);
    expect(results[0].title).toBe('');
    expect(results[0].snippet).toBe('');
    expect(results[0].url).toBe('');
    
    expect(results[1].title).toBe('Only Title');
    expect(results[1].snippet).toBe('');
    expect(results[1].url).toBe('');
  });
  
  // Basic test for local search (mock implementation)
  it('should perform local search correctly', async () => {
    // Mock for first API call (to get location IDs)
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        locations: {
          results: [
            { id: 'location1', title: 'Location 1' },
            { id: 'location2', title: 'Location 2' }
          ]
        }
      })
    });
    
    // Mock for second API call (to get POI data)
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        results: [
          {
            id: 'location1',
            name: 'Location 1',
            address: {
              streetAddress: '123 Main St',
              addressLocality: 'City',
              addressRegion: 'State',
              postalCode: '12345'
            },
            phone: '123-456-7890',
            rating: {
              ratingValue: 4.5,
              ratingCount: 100
            }
          }
        ]
      })
    });
    
    // Mock for third API call (to get descriptions)
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        descriptions: {
          location1: 'This is a description of Location 1'
        }
      })
    });
    
    const results = await provider.searchLocal('test location');
    
    // Check that fetch was called correctly for each API
    expect(mockFetch).toHaveBeenCalledTimes(3);
    
    // Check result format
    expect(results).toHaveLength(1);
    expect(results[0].name).toBe('Location 1');
    expect(results[0].address).toBe('123 Main St, City, State, 12345');
    expect(results[0].phone).toBe('123-456-7890');
    expect(results[0].rating).toBe(4.5);
    expect(results[0].reviewCount).toBe(100);
    expect(results[0].description).toBe('This is a description of Location 1');
  });
  
  it('should handle no local results', async () => {
    // Mock empty locations response
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        locations: {
          results: []
        }
      })
    });
    
    const results = await provider.searchLocal('test location');
    
    // Should return empty array
    expect(results).toHaveLength(0);
    
    // Should only make one API call
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });
});