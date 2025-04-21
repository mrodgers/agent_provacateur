import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { SearchProvider } from '../providers/base.js';

/**
 * Create web search tool definition for a provider
 */
export function createWebSearchTool(provider: SearchProvider): Tool {
  return {
    name: `${provider.name}_web_search`,
    description: 
      `Performs a web search using the ${provider.name.charAt(0).toUpperCase() + provider.name.slice(1)} Search API.\n` +
      `Ideal for general queries, news, articles, and online content.\n` +
      `Use this for broad information gathering, recent events, or when you need diverse web sources.\n` +
      `Returns search results with titles, snippets, and URLs.\n` +
      `Maximum 20 results per request, with offset for pagination.`,
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query (max 400 chars, 50 words)'
        },
        count: {
          type: 'number',
          description: 'Number of results (1-20, default 10)',
          default: 10
        },
        offset: {
          type: 'number',
          description: 'Pagination offset (default 0)',
          default: 0
        }
      },
      required: ['query']
    }
  };
}

/**
 * Create local search tool definition for a provider
 */
export function createLocalSearchTool(provider: SearchProvider): Tool {
  return {
    name: `${provider.name}_local_search`,
    description:
      `Searches for local businesses and places using ${provider.name.charAt(0).toUpperCase() + provider.name.slice(1)}'s Local Search API.\n` +
      `Best for queries related to physical locations, businesses, restaurants, services, etc.\n` +
      `Returns detailed information including:\n` +
      `- Business names and addresses\n` +
      `- Ratings and review counts\n` +
      `- Phone numbers and opening hours\n` +
      `Use this when the query implies 'near me' or mentions specific locations.\n` +
      `Automatically falls back to web search if no local results are found.`,
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Local search query (e.g. "pizza near Central Park")'
        },
        count: {
          type: 'number',
          description: 'Number of results (1-20, default 5)',
          default: 5
        }
      },
      required: ['query']
    }
  };
}

/**
 * Format web search results as a text string
 */
export function formatWebResults(results: any[]): string {
  if (!results || results.length === 0) {
    return 'No results found.';
  }
  
  return results.map((result, index) => {
    const title = result.title || 'Untitled';
    const snippet = result.snippet || 'No description available';
    const url = result.url || '';
    
    return `[${index + 1}] ${title}\n${snippet}\nURL: ${url}`;
  }).join('\n\n');
}

/**
 * Format local search results as a text string
 */
export function formatLocalResults(results: any[]): string {
  if (!results || results.length === 0) {
    return 'No local results found.';
  }
  
  return results.map((result, index) => {
    const name = result.name || 'Unnamed location';
    const address = result.address || 'No address available';
    const phone = result.phone || 'No phone available';
    const rating = typeof result.rating === 'number' ? `${result.rating}/5` : 'No rating';
    const reviews = result.reviewCount ? `(${result.reviewCount} reviews)` : '';
    const hours = result.hours?.length ? `\nHours: ${result.hours.join(', ')}` : '';
    const description = result.description ? `\nDescription: ${result.description}` : '';
    const website = result.website ? `\nWebsite: ${result.website}` : '';
    
    return `[${index + 1}] ${name}\n` +
           `Address: ${address}\n` +
           `Phone: ${phone}\n` +
           `Rating: ${rating} ${reviews}` +
           hours +
           description +
           website;
  }).join('\n\n');
}

/**
 * Build a list of tools based on available providers
 */
export function buildToolList(providers: SearchProvider[]): Tool[] {
  const tools: Tool[] = [];
  
  for (const provider of providers) {
    // Add web search tool for all providers
    tools.push(createWebSearchTool(provider));
    
    // Add local search tool only if provider has local capability
    if (provider.hasCapability('local')) {
      tools.push(createLocalSearchTool(provider));
    }
  }
  
  return tools;
}