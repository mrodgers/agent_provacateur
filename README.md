# Agent Provocateur

A Python library for developing, benchmarking, and deploying AI agents for research tasks. The system enables modular agents to collaboratively perform end-to-end research against structured and unstructured data sources.

## Features

- **MCP Server Mock**: Simulates tool interactions (JIRA, Document, PDF, Search) with configurable latency and error injection
- **MCP Client SDK**: Type-safe Python client for interacting with the MCP server
- **CLI Interface**: Command-line tools for interacting with the server
- **Agent-to-Agent (A2A) Communication**: Structured messaging system for agent coordination and task delegation
- **Agent Framework**: Base classes and utilities for building collaborative agent systems

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
│       ├── cli.py                # CLI interface
│       ├── a2a_models.py         # A2A message schemas
│       ├── a2a_messaging.py      # Agent messaging module
│       ├── a2a_redis.py          # Redis-based messaging
│       ├── agent_base.py         # Base agent framework
│       ├── agent_implementations.py # Sample agent implementations
│       └── sample_workflow.py    # Demo workflow
├── tests/                        # Test directory
│   ├── __init__.py
│   ├── test_main.py              # Tests for MCP server
│   ├── test_a2a_messaging.py     # Tests for A2A messaging
│   └── test_agent_base.py        # Tests for agent framework
├── CLAUDE.md                     # Guide for Claude AI
├── LICENSE                       # MIT License
├── README.md                     # This file
├── phase1_implementation.md      # Phase 1 documentation
├── phase2_implementation.md      # Phase 2 documentation
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
# Or using entry point
ap-server --host 127.0.0.1 --port 8000
```

### Using the CLI Client

```bash
# Fetch a JIRA ticket
python -m agent_provocateur.cli ticket AP-1
# Or using entry point
ap-client ticket AP-1

# Get document content
ap-client doc doc1

# Get PDF content
ap-client pdf pdf1

# Search web content
ap-client search "agent protocol"

# Configure server latency and error rate
ap-client config --min-latency 100 --max-latency 1000 --error-rate 0.1

# Output results as JSON
ap-client ticket AP-1 --json

# Connect to a different server
ap-client --server http://localhost:8008 ticket AP-1
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

### Running the Sample Agent Workflow

```bash
# Start the MCP server in one terminal
ap-server

# Run the sample workflow in another terminal
ap-workflow "agent protocol research" --ticket AP-1 --doc doc1
```

### Using the Agent Framework

```python
import asyncio
from agent_provocateur.a2a_messaging import InMemoryMessageBroker
from agent_provocateur.agent_base import BaseAgent
from agent_provocateur.a2a_models import TaskStatus

# Create your custom agent
class MyAgent(BaseAgent):
    async def handle_custom_task(self, task_request):
        # Process the task
        result = {"status": "success", "data": task_request.payload}
        return result

async def main():
    # Create shared broker and agents
    broker = InMemoryMessageBroker()
    agent1 = MyAgent("agent1", broker)
    agent2 = BaseAgent("agent2", broker)
    
    # Start agents
    await agent1.start()
    await agent2.start()
    
    try:
        # Send a request from agent2 to agent1
        result = await agent2.send_request_and_wait(
            target_agent="agent1",
            intent="custom_task",
            payload={"key": "value"},
        )
        
        # Process the result
        if result and result.status == TaskStatus.COMPLETED:
            print(f"Task completed: {result.output}")
    finally:
        # Stop agents
        await agent1.stop()
        await agent2.stop()

asyncio.run(main())
```

## License

MIT License. See the LICENSE file for details.