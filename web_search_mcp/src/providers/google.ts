/**
 * Google Search API provider
 * 
 * Implements Google Custom Search JSON API
 * Documentation: https://developers.google.com/custom-search/v1/overview
 */

import { SearchProvider, SearchResult, LocalResult, ProviderConfig } from './base.js';

interface GoogleSearchConfig extends ProviderConfig {
  cx: string;  // Google Custom Search Engine ID
}

/**
 * Google Search provider implementation
 */
export class GoogleSearchProvider implements SearchProvider {
  readonly name = 'google';
  private apiKey: string;
  private cx: string;
  
  constructor(config: GoogleSearchConfig) {
    if (!config.apiKey) {
      throw new Error('Google API key is required');
    }
    if (!config.cx) {
      throw new Error('Google Custom Search Engine ID (cx) is required');
    }
    
    this.apiKey = config.apiKey;
    this.cx = config.cx;
  }
  
  /**
   * Perform web search using Google Custom Search API
   */
  async searchWeb(query: string, count: number = 10, offset: number = 0): Promise<SearchResult[]> {
    try {
      // Google API uses 1-based indexing for startIndex
      const startIndex = offset + 1;
      
      // Cap count to 10 (Google API limit per request)
      const num = Math.min(count, 10);
      
      // Construct the API URL
      const url = new URL('https://www.googleapis.com/customsearch/v1');
      url.searchParams.append('key', this.apiKey);
      url.searchParams.append('cx', this.cx);
      url.searchParams.append('q', query);
      url.searchParams.append('num', num.toString());
      url.searchParams.append('start', startIndex.toString());
      
      // Make the API request
      const response = await fetch(url.toString());
      
      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Google Search API error: ${response.status} ${error}`);
      }
      
      const data = await response.json();
      
      // Map Google results to standard format
      return this.mapSearchResults(data);
    } catch (error) {
      console.error('Google search error:', error);
      throw new Error(`Google search failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * Map Google search results to our standard format
   */
  private mapSearchResults(data: any): SearchResult[] {
    if (!data.items || !Array.isArray(data.items)) {
      return [];
    }
    
    return data.items.map((item: any) => {
      const result: SearchResult = {
        title: item.title || 'Untitled',
        snippet: item.snippet || '',
        url: item.link || '',
      };
      
      // Add optional fields if available
      if (item.pagemap?.metatags?.[0]?.['og:locale']) {
        result.language = item.pagemap.metatags[0]['og:locale'];
      }
      
      if (item.pagemap?.article?.[0]?.datePublished) {
        result.published = item.pagemap.article[0].datePublished;
      }
      
      return result;
    });
  }
  
  /**
   * Check if this provider supports a specific capability
   */
  hasCapability(capability: string): boolean {
    return capability === 'web';
  }
}