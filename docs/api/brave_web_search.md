# Brave Search API Integration

This document explains how Agent Provocateur integrates with the Brave Search API for web search capabilities.

## Overview

Brave Search API provides web search and local search functionality with robust privacy features. Agent Provocateur uses the Brave Search API as the default web search provider in the Web Search MCP server.

## Setup

### API Key

To use the Brave Search API, you need to obtain an API key:

1. Visit [Brave Search API](https://brave.com/search/api/)
2. Sign up for an API key
3. Copy your API key to the `.env` file in the web_search_mcp directory

```bash
# In web_search_mcp/.env
BRAVE_API_KEY=your_brave_api_key_here
```

### Rate Limits

Brave Search API has the following rate limits:

- **Free tier**: 2 queries per second, up to 1000 queries per month
- **Pro tier**: Higher limits available for paid subscriptions

To prevent exceeding rate limits, the Web Search MCP server includes rate limiting functionality.

## API Features

Brave Search API supports two main types of searches:

### Web Search

General web search with options for pagination and content filtering:

```bash
# Basic web search
./scripts/ap.sh web-search --query "climate change" --provider brave

# With additional parameters
./scripts/ap.sh web-search --query "climate change" --provider brave --max-results 10
```

### Local Search

Business and location searches with detailed business information:

```bash
# Local search example (not currently implemented in CLI)
# Format: "search term near location"
./scripts/ap.sh web-search --query "restaurants near San Francisco" --provider brave
```

## API Response

The Brave Search API returns structured results that are parsed by the WebSearchAgent:

### Web Search Results

Each web search result includes:
- Title
- Snippet (description)
- URL
- Optional: language, publication date

### Local Search Results

Each local search result includes:
- Business name
- Address
- Phone number
- Ratings and review count
- Business hours
- Website
- Geographic coordinates

## Integration in Agent Provocateur

The Web Search MCP server handles API requests and response parsing:

1. The WebSearchAgent creates a search task
2. The MCP client sends the task to the Web Search MCP server
3. The server calls the Brave Search API with appropriate parameters
4. Results are parsed and returned with confidence scores and source attribution
5. The WebSearchAgent processes the results and makes them available to other agents

## Source Attribution

All search results include robust source attribution:

- Unique source IDs
- Confidence scores based on result ranking
- Properly formatted citations
- Metadata including provider information and retrieval time

## Error Handling

The Web Search MCP server handles API errors gracefully:

- Rate limit exceeded
- API key validation
- Malformed queries
- Network errors

## Related Documentation

- [Web Search Integration](./web_search_integration.md)
- [Source Attribution Guide](../guides/source_attribution.md)
- [Web Search MCP Server README](../../web_search_mcp/README.md)