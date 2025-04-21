#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import { loadConfig } from './config.js';
import { SearchProviderFactory } from './providers/factory.js';
import { RateLimiter } from './utils/rate-limiter.js';
import { ResultCache } from './utils/cache.js';
import { buildToolList, formatWebResults, formatLocalResults } from './tools/search-tools.js';
import { SearchProvider } from './providers/base.js';

// Load configuration
const config = loadConfig();

// Initialize provider factory
const providerFactory = new SearchProviderFactory(config.providers);
const activeProviders = providerFactory.getEnabledProviders();

// Validate that we have at least one provider
if (activeProviders.length === 0) {
  console.error('Error: No search providers enabled. Please configure at least one search provider.');
  process.exit(1);
}

// Initialize rate limiter and cache
const rateLimiter = new RateLimiter(config.rateLimit);
const cache = new ResultCache(config.cache);

// Create server
const server = new Server(
  {
    name: config.serverName,
    version: config.serverVersion,
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Helper function to find provider by name
function findProvider(name: string): SearchProvider | undefined {
  return activeProviders.find(provider => provider.name === name);
}

// Helper functions for MCP responses
function createSuccessResponse(text: string) {
  return {
    content: [{ type: 'text', text }],
    isError: false,
  };
}

function createErrorResponse(message: string) {
  return {
    content: [{ type: 'text', text: `Error: ${message}` }],
    isError: true,
  };
}

// Register request handlers
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: buildToolList(activeProviders),
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const { name, arguments: args } = request.params;
    
    if (!args) {
      return createErrorResponse('No arguments provided');
    }
    
    // Check rate limit
    if (!rateLimiter.allowRequest()) {
      return createErrorResponse('Rate limit exceeded. Please try again later.');
    }
    
    // Parse the tool name to get provider and action
    const [providerName, action] = name.split('_');
    
    if (!providerName || !action) {
      return createErrorResponse(`Invalid tool name: ${name}`);
    }
    
    // Find the provider
    const provider = findProvider(providerName);
    
    if (!provider) {
      return createErrorResponse(`Provider not available: ${providerName}`);
    }
    
    // Handle web search
    if (action === 'web' && name.endsWith('_search')) {
      const { query, count = 10, offset = 0 } = args as { query?: string; count?: number; offset?: number };
      
      if (!query) {
        return createErrorResponse('Missing required parameter: query');
      }
      
      // Check cache first
      const cacheKey = `web:${providerName}:${query}:${count}:${offset}`;
      const cachedResult = cache.get<string>(cacheKey);
      
      if (cachedResult) {
        console.error(`Cache hit for: ${cacheKey}`);
        return createSuccessResponse(cachedResult);
      }
      
      // Execute search
      try {
        console.error(`Searching web with ${providerName}: "${query}"`);
        const results = await provider.searchWeb(query, count, offset);
        const formattedResults = formatWebResults(results);
        
        // Cache results
        cache.set(cacheKey, formattedResults);
        
        return createSuccessResponse(formattedResults);
      } catch (error: any) {
        console.error(`Error in web search:`, error);
        return createErrorResponse(`Web search failed: ${error.message}`);
      }
    }
    
    // Handle local search
    if (action === 'local' && name.endsWith('_search')) {
      const { query, count = 5 } = args as { query?: string; count?: number };
      
      if (!query) {
        return createErrorResponse('Missing required parameter: query');
      }
      
      // Check if provider supports local search
      if (!provider.hasCapability('local') || !provider.searchLocal) {
        return createErrorResponse(`Provider ${providerName} does not support local search`);
      }
      
      // Check cache
      const cacheKey = `local:${providerName}:${query}:${count}`;
      const cachedResult = cache.get<string>(cacheKey);
      
      if (cachedResult) {
        console.error(`Cache hit for: ${cacheKey}`);
        return createSuccessResponse(cachedResult);
      }
      
      // Execute search
      try {
        console.error(`Searching local with ${providerName}: "${query}"`);
        const results = await provider.searchLocal(query, count);
        
        // If no local results, fall back to web search
        if (results.length === 0 && provider.hasCapability('web')) {
          console.error(`No local results found, falling back to web search`);
          const webResults = await provider.searchWeb(query, count, 0);
          const formattedWebResults = formatWebResults(webResults);
          
          // Cache results
          cache.set(cacheKey, formattedWebResults);
          
          return createSuccessResponse(formattedWebResults);
        }
        
        const formattedResults = formatLocalResults(results);
        
        // Cache results
        cache.set(cacheKey, formattedResults);
        
        return createSuccessResponse(formattedResults);
      } catch (error: any) {
        console.error(`Error in local search:`, error);
        
        // Try web search as a fallback
        if (provider.hasCapability('web')) {
          try {
            console.error(`Local search failed, falling back to web search`);
            const webResults = await provider.searchWeb(query, count, 0);
            const formattedWebResults = formatWebResults(webResults);
            return createSuccessResponse(formattedWebResults);
          } catch (webError) {
            return createErrorResponse(`Search failed: ${error.message}`);
          }
        } else {
          return createErrorResponse(`Local search failed: ${error.message}`);
        }
      }
    }
    
    return createErrorResponse(`Unknown action: ${action} for provider: ${providerName}`);
  } catch (error: any) {
    console.error('Unexpected error:', error);
    return createErrorResponse(`Unexpected error: ${error.message}`);
  }
});

// Start the server
async function runServer() {
  try {
    // Log active providers
    console.error(`Starting web search MCP server with providers: ${activeProviders.map(p => p.name).join(', ')}`);
    
    const transport = new StdioServerTransport();
    await server.connect(transport);
    
    console.error(`Web Search MCP Server running on stdio`);
  } catch (error) {
    console.error('Error starting server:', error);
    process.exit(1);
  }
}

// Handle process signals
process.on('SIGINT', () => {
  console.error('Received SIGINT, shutting down');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error('Received SIGTERM, shutting down');
  process.exit(0);
});

// Run the server
runServer().catch((error) => {
  console.error('Fatal error running server:', error);
  process.exit(1);
});