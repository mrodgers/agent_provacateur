# Development Guide

This document outlines the development workflow for the Agent Provocateur project using uv for virtual environment management.

## Environment Setup

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and environment manager

### Setup with uv

We provide a setup script that configures everything for you:

```bash
# Make the script executable (if needed)
chmod +x scripts/setup_env.sh

# Run the setup script
./scripts/setup_env.sh
```

The script will:
1. Install uv if not already installed
2. Create a virtual environment in `.venv/`
3. Install the project with development dependencies
4. Optionally install Redis dependencies

Alternatively, you can set up manually:

```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
uv pip install -e ".[dev]"
```

## Running Tests

Use our test script to run tests with the proper environment:

```bash
# Run all tests
./scripts/run_tests.sh

# Run specific tests
./scripts/run_tests.sh tests/test_a2a_messaging.py

# Run with coverage
./scripts/run_tests.sh --cov=src.agent_provocateur
```

Or manually run tests after activating the environment:

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_main.py

# Run with coverage
pytest --cov=agent_provocateur
```

## Running the Server

Use the provided script to start the MCP server:

```bash
# Start with default settings (localhost:8000)
./scripts/start_servers.sh

# Specify host and port
./scripts/start_servers.sh --host=0.0.0.0 --port=8080
```

Or manually:

```bash
# After activating the environment
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
├── .venv/                        # Virtual environment (generated)
└── pyproject.toml                # Project configuration
```

## Sample Workflow

```bash
# Start the MCP server in one terminal
./scripts/start_servers.sh

# In another terminal, run the CLI client
source .venv/bin/activate  # Activate environment first
ap-client ticket AP-1

# Run the sample agent workflow
ap-workflow "agent protocol research" --ticket AP-1 --doc doc1
```

## Development Workflow

1. **Set up the environment**: Run `./scripts/setup_env.sh`
2. **Make changes**: Edit code in the `src/agent_provocateur` directory
3. **Run tests**: Use `./scripts/run_tests.sh` to validate changes
4. **Run linting**: `ruff check .` and `mypy src` to ensure code quality
5. **Test manually**: Start the server and interact with it using the CLI or sample workflow

## Dependency Management

When adding new dependencies:

1. Add them to `pyproject.toml` in the appropriate section
2. Reinstall the package: `uv pip install -e ".[dev]"`
3. Update any relevant documentation