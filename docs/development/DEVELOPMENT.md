# Development Guide

This document outlines the development workflow for the Agent Provocateur project using uv for virtual environment management.

## Environment Setup

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and environment manager

### Unified Development Script

We provide a single unified script (`ap.sh`) that handles all development tasks:

```bash
# Make the script executable (if needed)
chmod +x scripts/ap.sh

# Get help information
./scripts/ap.sh help
```

The script supports the following commands:

| Command | Description | Example |
|---------|-------------|---------|
| `setup` | Create or update the virtual environment | `./scripts/ap.sh setup` |
| `test` | Run tests (with optional pytest arguments) | `./scripts/ap.sh test tests/test_main.py` |
| `server` | Start the MCP server | `./scripts/ap.sh server --host=0.0.0.0 --port=8080` |
| `workflow` | Run a sample agent workflow | `./scripts/ap.sh workflow "query" --ticket=AP-1` |
| `help` | Show help information | `./scripts/ap.sh help` |

Common usage examples:

```bash
# Setup environment
./scripts/ap.sh setup

# Run all tests
./scripts/ap.sh test

# Run specific tests
./scripts/ap.sh test tests/test_a2a_messaging.py

# Start MCP server
./scripts/ap.sh server

# Run workflow
./scripts/ap.sh workflow "agent protocol research" --ticket=AP-1 --doc=doc1
```

### Manual Setup

If you prefer, you can perform operations manually:

```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Start server
ap-server --host 127.0.0.1 --port 8000
```

## Project Structure

```
.
├── src/
│   └── agent_provocateur/        # Main package
│       ├── __init__.py
│       ├── main.py               # Server entry point
│       ├── models.py             # Data models
│       ├── mcp_server.py         # Mock MCP server
│       ├── mcp_client.py         # Client SDK
│       ├── cli.py                # CLI interface
│       ├── a2a_models.py         # A2A message schemas
│       ├── a2a_messaging.py      # Agent messaging module
│       ├── a2a_redis.py          # Redis-based messaging
│       ├── agent_base.py         # Base agent framework
│       ├── agent_implementations.py # Sample agents
│       └── sample_workflow.py    # Demo workflow
├── tests/                        # Test directory
├── scripts/                      # Helper scripts
│   └── ap.sh                     # Unified development script
├── .venv/                        # Virtual environment (generated)
└── pyproject.toml                # Project configuration
```

## Development Workflow

1. **Set up the environment**: Run `./scripts/ap.sh setup`
2. **Make changes**: Edit code in the `src/agent_provocateur` directory
3. **Run tests**: Use `./scripts/ap.sh test` to validate changes
4. **Test manually**: Start the server and interact with it using the CLI or sample workflow

## Dependency Management

When adding new dependencies:

1. Add them to `pyproject.toml` in the appropriate section
2. Reinstall the package: `./scripts/ap.sh setup` (it will update an existing environment)