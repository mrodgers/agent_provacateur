import { SearchProvider, ProviderConfig } from './base.js';
import { BraveSearchProvider } from './brave.js';
import { GoogleSearchProvider } from './google.js';
import { BingSearchProvider } from './bing.js';

/**
 * Configuration for all search providers
 */
export interface SearchProvidersConfig {
  defaultProvider: string;
  providers: {
    [key: string]: ProviderConfig;
  };
}

/**
 * Factory for creating and managing search providers
 */
export class SearchProviderFactory {
  private config: SearchProvidersConfig;
  private providers: Map<string, SearchProvider> = new Map();
  
  constructor(config: SearchProvidersConfig) {
    this.config = config;
    this.initializeProviders();
  }
  
  /**
   * Initialize all enabled providers
   */
  private initializeProviders(): void {
    // Initialize Brave provider if enabled
    if (this.config.providers.brave?.enabled) {
      try {
        const braveProvider = new BraveSearchProvider(this.config.providers.brave);
        this.providers.set('brave', braveProvider);
      } catch (error) {
        console.error('Failed to initialize Brave provider:', error);
      }
    }
    
    // Initialize Google provider if enabled
    if (this.config.providers.google?.enabled) {
      try {
        // Ensure the google provider config has the right type with cx parameter
        const googleConfig = this.config.providers.google as ProviderConfig & { cx: string };
        const googleProvider = new GoogleSearchProvider(googleConfig);
        this.providers.set('google', googleProvider);
      } catch (error) {
        console.error('Failed to initialize Google provider:', error);
      }
    }
    
    // Initialize Bing provider if enabled
    if (this.config.providers.bing?.enabled) {
      try {
        const bingProvider = new BingSearchProvider(this.config.providers.bing);
        this.providers.set('bing', bingProvider);
      } catch (error) {
        console.error('Failed to initialize Bing provider:', error);
      }
    }
  }
  
  /**
   * Get a provider by name
   */
  getProvider(name: string): SearchProvider | undefined {
    return this.providers.get(name);
  }
  
  /**
   * Get the default search provider
   */
  getDefaultProvider(): SearchProvider | undefined {
    return this.getProvider(this.config.defaultProvider) || 
           this.getEnabledProviders()[0];
  }
  
  /**
   * Get all enabled providers
   */
  getEnabledProviders(): SearchProvider[] {
    return Array.from(this.providers.values());
  }
  
  /**
   * Check if a provider is available
   */
  isProviderAvailable(name: string): boolean {
    return this.providers.has(name);
  }
}