/**
 * Common types and interfaces for search providers
 */

/**
 * Standard web search result format
 */
export interface SearchResult {
  title: string;
  snippet: string;
  url: string;
  language?: string;
  published?: string;
}

/**
 * Standard local search result format
 */
export interface LocalResult {
  name: string;
  address?: string;
  phone?: string;
  rating?: number;
  reviewCount?: number;
  priceRange?: string;
  description?: string;
  hours?: string[];
  website?: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
}

/**
 * Base interface for all search providers
 */
export interface SearchProvider {
  /**
   * Provider name identifier
   */
  readonly name: string;
  
  /**
   * Perform a web search
   * @param query Search query
   * @param count Maximum number of results
   * @param offset Pagination offset
   * @returns List of search results
   */
  searchWeb(query: string, count: number, offset: number): Promise<SearchResult[]>;
  
  /**
   * Perform a local business/place search (optional)
   * @param query Search query
   * @param count Maximum number of results
   * @returns List of local results
   */
  searchLocal?(query: string, count: number): Promise<LocalResult[]>;
  
  /**
   * Check if provider has a specific capability
   * @param capability Capability name ('web', 'local', etc.)
   * @returns True if provider supports the capability
   */
  hasCapability(capability: string): boolean;
}

/**
 * Provider configuration options
 */
export interface ProviderConfig {
  enabled: boolean;
  apiKey: string;
  [key: string]: any;
}