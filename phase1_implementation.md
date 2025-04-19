# Phase 1 Implementation: MCP Tools Development

This document details the implementation of Phase 1 of the Agent Provocateur project, focusing on the development of MCP (Model Context Protocol) tools.

## Components Implemented

### 1. MCP Server Mock

The mock MCP server (`mcp_server.py`) provides standardized endpoints for tool interactions:

- **JIRA Tickets**: `/jira/ticket/{ticket_id}` - Retrieve ticket information
- **Documents**: `/docs/{doc_id}` - Retrieve document content
- **PDF Documents**: `/pdf/{pdf_id}` - Retrieve PDF document content
- **Web Search**: `/search?query={query}` - Perform web search

The server includes:
- Configurable latency (0-500ms by default)
- Configurable error injection (0% by default)
- Sample mock data for each endpoint

Configuration endpoints allow runtime adjustment of server behavior:
- `GET /config` - Get current configuration
- `POST /config` - Update configuration

### 2. MCP Client SDK

The client SDK (`mcp_client.py`) provides both asynchronous and synchronous interfaces:

**Asynchronous Client (`McpClient`)**:
- `async fetch_ticket(ticket_id)` - Fetch JIRA ticket
- `async get_doc(doc_id)` - Get document content
- `async get_pdf(pdf_id)` - Get PDF document
- `async search_web(query)` - Search the web
- `async update_server_config(...)` - Update server configuration

**Synchronous Client (`SyncMcpClient`)**:
- Wrapper around the async client
- Context manager support (`with` statement)
- Synchronous interface to all async methods

### 3. CLI Interface

The command-line interface (`cli.py`) provides easy access to all client functionality:

- `ticket` command - Fetch JIRA tickets
- `doc` command - Fetch documents
- `pdf` command - Fetch PDF documents
- `search` command - Search the web
- `config` command - Update server configuration

Additional options:
- `--json` - Output results as JSON
- `--server` - Specify a different server URL

### 4. Data Models

Type-safe models (`models.py`) ensure consistent data structures:

- `JiraTicket` - Model for JIRA ticket data
- `DocumentContent` - Model for document content
- `PdfDocument` and `PdfPage` - Models for PDF data
- `SearchResult` and `SearchResults` - Models for search results
- `McpError` - Model for error responses

## Testing

The implementation includes comprehensive tests:

- Server configuration tests
- Ticket retrieval tests
- Web search tests

Test coverage for the core MCP server is above 80%.

## Usage Examples

### Server Startup

```bash
python -m agent_provocateur.main --host 127.0.0.1 --port 8000
```

### CLI Usage

```bash
# Fetch a ticket
python -m agent_provocateur.cli ticket AP-1

# Search with JSON output
python -m agent_provocateur.cli search "agent protocol" --json
```

### SDK Usage

```python
from agent_provocateur.mcp_client import SyncMcpClient

with SyncMcpClient() as client:
    # Fetch a ticket
    ticket = client.fetch_ticket("AP-1")
    print(f"Ticket: {ticket.id} - {ticket.summary}")
    
    # Update server configuration
    client.update_server_config(
        latency_min_ms=100,
        latency_max_ms=1000,
        error_rate=0.1
    )
```

## Success Metrics

The implementation meets all defined acceptance criteria from the PRD:

- Mock server responds within 0-500 ms by default (configurable to 0-1500 ms)
- SDK methods return properly typed objects matching defined schemas
- CLI demo executes complete workflows and formats results
- Test coverage exceeds the required threshold

## Next Steps

The next phase (Phase 2) will focus on A2A Communication Development:
- Create message schemas for task requests and results
- Implement pub/sub infrastructure 
- Build agent messaging modules
- Develop a sample workflow with agent collaboration