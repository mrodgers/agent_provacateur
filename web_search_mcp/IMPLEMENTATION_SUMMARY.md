# Web Search MCP Server Implementation Summary

This document provides a summary of the Web Search MCP Server implementation, including its architecture, components, and integration with Agent Provocateur.

## Project Overview

The Web Search MCP Server is a Model Context Protocol (MCP) server that provides web search capabilities for Agent Provocateur. It supports multiple search providers (currently Brave Search) and implements both web search and local search functionality.

## Architecture

### Core Components

1. **Search Provider Interface** (`src/providers/base.ts`)
   - Defines the common interface for all search providers
   - Standardizes search result formats
   - Supports capability checking

2. **Provider Implementations** (`src/providers/brave.ts`)
   - Brave Search provider with web and local search
   - Configurable through API keys
   - Error handling and result formatting

3. **Provider Factory** (`src/providers/factory.ts`)
   - Creates and manages provider instances
   - Supports multiple providers with fallbacks
   - Configuration-based provider selection

4. **Utilities**
   - **Cache** (`src/utils/cache.ts`) - In-memory caching with TTL
   - **Rate Limiter** (`src/utils/rate-limiter.ts`) - Prevents API overuse

5. **MCP Tools** (`src/tools/search-tools.ts`)
   - Dynamic tool registration based on available providers
   - Tool definitions for web and local search
   - Result formatting utilities

6. **Server Core** (`src/index.ts`)
   - MCP protocol implementation
   - Request handling and routing
   - Error handling and logging

### Data Flow

1. Client sends a tool call request to the MCP server
2. Server validates request and checks rate limits
3. If cache hit, returns cached result
4. Otherwise, routes request to appropriate provider
5. Provider makes API call(s) to search service
6. Results are formatted and returned to client
7. Results are cached for future requests

## Implementation Details

### Provider Support

The server is designed to support multiple search providers:

- **Brave Search** - Fully implemented
- **Google Search** - Fully implemented
- **Bing Search** - Fully implemented

New providers can be added by implementing the `SearchProvider` interface.

### Caching Strategy

- In-memory caching with configurable TTL
- Cache keys based on provider, query, count, and offset
- Cache invalidation on TTL expiry
- Cache bypassing option available via configuration

### Rate Limiting

- Per-second and per-day rate limiting
- Configurable limits via environment variables
- Automatic reset of counters at appropriate intervals
- Status reporting for monitoring

### Error Handling

- Graceful handling of API errors
- Fallback mechanisms when providers fail
- Detailed error messages for debugging
- Cache miss reporting and statistics

## Testing

1. **Unit Tests** - Testing individual components
   - `tests/utils/cache.test.ts` - Cache functionality
   - `tests/utils/rate-limiter.test.ts` - Rate limiting
   - `tests/providers/brave.test.ts` - Brave provider functionality

2. **Integration Tests** - Testing component interaction (planned)
   - Testing server with mock providers
   - Testing server with mock clients

## Deployment

The server is deployed as a container using Podman or Docker:

1. **Build Process**
   - TypeScript compilation
   - Dependency management
   - Production optimizations

2. **Runtime Environment**
   - Alpine-based Node.js container
   - Environment variable configuration
   - Stdio-based communication

3. **Scripts**
   - `scripts/build.sh` - Builds the container image
   - `scripts/run.sh` - Runs the container with environment variables

## Integration with Agent Provocateur

The Web Search MCP Server integrates with Agent Provocateur through the following steps:

1. **MCP Client Integration**
   - WebSearchAgent initializes MCP client
   - Client connects to the MCP server
   - Server provides tools to the client

2. **Search Handling**
   - Agent forwards search requests to MCP server
   - Server performs search and returns results
   - Agent processes results for display and attribution

3. **Source Attribution**
   - Agent parses search results into Source objects
   - Sources include confidence scores and citations
   - Results are presented with proper attribution

## Future Enhancements

1. **Additional Provider Support**
   - Add DuckDuckGo and other providers

2. **Advanced Caching**
   - Disk-persistent caching
   - Cache sharing between instances
   - Smart cache invalidation

3. **Result Aggregation**
   - Combine results from multiple providers
   - De-duplication and ranking
   - Confidence scoring based on source agreement

4. **Authentication and Security**
   - API key rotation
   - Request authentication
   - Rate limiting per client

5. **Monitoring and Analytics**
   - Usage tracking
   - Provider performance metrics
   - Search pattern analysis