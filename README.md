# Agent Provocateur

A Python library for developing, benchmarking, and deploying AI agents for research tasks. The system enables modular agents to collaboratively perform end-to-end research against structured and unstructured data sources.

## Features

- **MCP Server Mock**: Simulates tool interactions (JIRA, Document, PDF, Search) with configurable latency and error injection
- **MCP Client SDK**: Type-safe Python client for interacting with the MCP server
- **CLI Interface**: Command-line tools for interacting with the server
- **Agent-to-Agent (A2A) Communication**: (Coming soon) Enables agent coordination and task delegation

## Installation

```bash
# Install in development mode with all dev dependencies
pip install -e ".[dev]"
```

## Project Structure

```
.
├── src/
│   └── agent_provocateur/        # Main package
│       ├── __init__.py
│       ├── main.py               # Server entry point
│       ├── models.py             # Data models
│       ├── mcp_server.py         # Mock MCP server implementation
│       ├── mcp_client.py         # Client SDK
│       └── cli.py                # CLI interface
├── tests/                        # Test directory
│   ├── __init__.py
│   └── test_main.py              # Tests for MCP server
├── CLAUDE.md                     # Guide for Claude AI
├── LICENSE                       # MIT License
├── README.md                     # This file
├── pyproject.toml                # Project configuration
└── setup.py                      # Installation script
```

## Development

```bash
# Run tests
pytest                     # Run all tests with pytest
pytest -v                  # Run with verbose output
python -m pytest --cov=src.agent_provocateur  # Run with coverage report

# Type checking
mypy src

# Linting
ruff check .
```

## Usage

### Running the MCP Server

```bash
# Start the MCP server
python -m agent_provocateur.main --host 127.0.0.1 --port 8000
```

### Using the CLI Client

```bash
# Fetch a JIRA ticket
python -m agent_provocateur.cli ticket AP-1

# Get document content
python -m agent_provocateur.cli doc doc1

# Get PDF content
python -m agent_provocateur.cli pdf pdf1

# Search web content
python -m agent_provocateur.cli search "agent protocol"

# Configure server latency and error rate
python -m agent_provocateur.cli config --min-latency 100 --max-latency 1000 --error-rate 0.1

# Output results as JSON
python -m agent_provocateur.cli ticket AP-1 --json

# Connect to a different server
python -m agent_provocateur.cli --server http://localhost:8008 ticket AP-1
```

### Using the Client SDK

```python
# Async client
import asyncio
from agent_provocateur.mcp_client import McpClient

async def main():
    client = McpClient("http://localhost:8000")
    try:
        # Fetch a JIRA ticket
        ticket = await client.fetch_ticket("AP-1")
        print(f"Ticket summary: {ticket.summary}")
        
        # Search the web
        results = await client.search_web("agent protocol")
        for result in results:
            print(f"- {result.title}: {result.snippet}")
    finally:
        await client.close()

asyncio.run(main())

# Synchronous client
from agent_provocateur.mcp_client import SyncMcpClient

with SyncMcpClient("http://localhost:8000") as client:
    ticket = client.fetch_ticket("AP-1")
    print(f"Ticket: {ticket.id} - {ticket.summary}")
```

## License

MIT License. See the LICENSE file for details.