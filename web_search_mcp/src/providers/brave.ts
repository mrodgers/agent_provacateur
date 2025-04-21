import { SearchProvider, SearchResult, LocalResult, ProviderConfig } from './base.js';

/**
 * Brave Search API response interfaces
 */
interface BraveWebResponse {
  web?: {
    results?: Array<{
      title: string;
      description: string;
      url: string;
      language?: string;
      published?: string;
      rank?: number;
    }>;
  };
  locations?: {
    results?: Array<{
      id: string;
      title?: string;
    }>;
  };
}

interface BraveLocation {
  id: string;
  name: string;
  address: {
    streetAddress?: string;
    addressLocality?: string;
    addressRegion?: string;
    postalCode?: string;
  };
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  phone?: string;
  rating?: {
    ratingValue?: number;
    ratingCount?: number;
  };
  openingHours?: string[];
  priceRange?: string;
}

interface BravePoiResponse {
  results: BraveLocation[];
}

interface BraveDescription {
  descriptions: {[id: string]: string};
}

/**
 * Implementation of Search Provider for Brave Search
 */
export class BraveSearchProvider implements SearchProvider {
  readonly name = 'brave';
  private apiKey: string;
  
  constructor(config: ProviderConfig) {
    if (!config.apiKey) {
      throw new Error('Brave API key is required');
    }
    
    this.apiKey = config.apiKey;
  }
  
  /**
   * Perform a web search using Brave Search API
   */
  async searchWeb(query: string, count: number = 10, offset: number = 0): Promise<SearchResult[]> {
    const url = new URL('https://api.search.brave.com/res/v1/web/search');
    url.searchParams.set('q', query);
    url.searchParams.set('count', Math.min(count, 20).toString()); // API limit
    url.searchParams.set('offset', offset.toString());
    
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': this.apiKey
      }
    });
    
    if (!response.ok) {
      throw new Error(`Brave API error: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json() as BraveWebResponse;
    
    // Extract just web results
    return (data.web?.results || []).map(result => ({
      title: result.title || '',
      snippet: result.description || '',
      url: result.url || '',
      language: result.language,
      published: result.published
    }));
  }
  
  /**
   * Perform a local search using Brave Search API
   */
  async searchLocal(query: string, count: number = 5): Promise<LocalResult[]> {
    // Initial search to get location IDs
    const webUrl = new URL('https://api.search.brave.com/res/v1/web/search');
    webUrl.searchParams.set('q', query);
    webUrl.searchParams.set('search_lang', 'en');
    webUrl.searchParams.set('result_filter', 'locations');
    webUrl.searchParams.set('count', Math.min(count, 20).toString());
    
    const webResponse = await fetch(webUrl, {
      headers: {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': this.apiKey
      }
    });
    
    if (!webResponse.ok) {
      throw new Error(`Brave API error: ${webResponse.status} ${webResponse.statusText}`);
    }
    
    const webData = await webResponse.json() as BraveWebResponse;
    const locationIds = webData.locations?.results?.filter((r): r is {id: string; title?: string} => r.id != null).map(r => r.id) || [];
    
    if (locationIds.length === 0) {
      // If no locations found, return empty array
      return [];
    }
    
    // Get POI details and descriptions in parallel
    const [poisData, descriptionsData] = await Promise.all([
      this.getPoisData(locationIds),
      this.getDescriptionsData(locationIds)
    ]);
    
    // Map to standard LocalResult format
    return poisData.results.map(poi => {
      // Build address string
      const address = [
        poi.address?.streetAddress,
        poi.address?.addressLocality,
        poi.address?.addressRegion,
        poi.address?.postalCode
      ].filter(Boolean).join(', ');
      
      return {
        name: poi.name,
        address,
        phone: poi.phone,
        rating: poi.rating?.ratingValue,
        reviewCount: poi.rating?.ratingCount,
        priceRange: poi.priceRange,
        description: descriptionsData.descriptions[poi.id],
        hours: poi.openingHours,
        website: poi.id.startsWith('http') ? poi.id : undefined,
        coordinates: poi.coordinates
      };
    });
  }
  
  /**
   * Check if provider supports a capability
   */
  hasCapability(capability: string): boolean {
    return ['web', 'local'].includes(capability);
  }
  
  /**
   * Get POI data from Brave API
   * @private
   */
  private async getPoisData(ids: string[]): Promise<BravePoiResponse> {
    const url = new URL('https://api.search.brave.com/res/v1/local/pois');
    ids.filter(Boolean).forEach(id => url.searchParams.append('ids', id));
    
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': this.apiKey
      }
    });
    
    if (!response.ok) {
      throw new Error(`Brave API error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json() as BravePoiResponse;
  }
  
  /**
   * Get descriptions for POIs
   * @private
   */
  private async getDescriptionsData(ids: string[]): Promise<BraveDescription> {
    const url = new URL('https://api.search.brave.com/res/v1/local/descriptions');
    ids.filter(Boolean).forEach(id => url.searchParams.append('ids', id));
    
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': this.apiKey
      }
    });
    
    if (!response.ok) {
      throw new Error(`Brave API error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json() as BraveDescription;
  }
}