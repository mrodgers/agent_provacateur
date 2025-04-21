/**
 * Bing Search API provider
 * 
 * Implements Bing Web Search API
 * Documentation: https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/overview
 */

import { SearchProvider, SearchResult, LocalResult, ProviderConfig } from './base.js';

/**
 * Bing Search provider implementation
 */
export class BingSearchProvider implements SearchProvider {
  readonly name = 'bing';
  private apiKey: string;
  
  constructor(config: ProviderConfig) {
    if (!config.apiKey) {
      throw new Error('Bing API key is required');
    }
    
    this.apiKey = config.apiKey;
  }
  
  /**
   * Perform web search using Bing Search API
   */
  async searchWeb(query: string, count: number = 10, offset: number = 0): Promise<SearchResult[]> {
    try {
      // Construct the API URL
      const url = new URL('https://api.bing.microsoft.com/v7.0/search');
      url.searchParams.append('q', query);
      url.searchParams.append('count', Math.min(count, 50).toString());
      url.searchParams.append('offset', offset.toString());
      url.searchParams.append('responseFilter', 'Webpages');
      url.searchParams.append('mkt', 'en-US');
      
      // Make the API request
      const response = await fetch(url.toString(), {
        headers: {
          'Ocp-Apim-Subscription-Key': this.apiKey
        }
      });
      
      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Bing Search API error: ${response.status} ${error}`);
      }
      
      const data = await response.json();
      
      // Map Bing results to standard format
      return this.mapSearchResults(data);
    } catch (error) {
      console.error('Bing search error:', error);
      throw new Error(`Bing search failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * Map Bing search results to our standard format
   */
  private mapSearchResults(data: any): SearchResult[] {
    if (!data.webPages?.value || !Array.isArray(data.webPages.value)) {
      return [];
    }
    
    return data.webPages.value.map((item: any) => {
      const result: SearchResult = {
        title: item.name || 'Untitled',
        snippet: item.snippet || '',
        url: item.url || '',
      };
      
      // Add optional fields if available
      if (item.language) {
        result.language = item.language;
      }
      
      if (item.datePublished) {
        result.published = item.datePublished;
      }
      
      return result;
    });
  }
  
  /**
   * Search for local businesses/places (not implemented for Bing yet)
   */
  async searchLocal(query: string, count: number = 5): Promise<LocalResult[]> {
    // Bing local search implementation could be added here in the future
    throw new Error('Local search is not implemented for Bing provider');
  }
  
  /**
   * Check if this provider supports a specific capability
   */
  hasCapability(capability: string): boolean {
    return capability === 'web';
  }
}