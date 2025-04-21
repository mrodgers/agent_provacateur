# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Lint/Test Commands

### Using the unified scripts (recommended)
- Setup environment: `./scripts/ap.sh setup`
- Run tests: `./scripts/ap.sh test`
- Start MCP server: `./scripts/ap.sh server`
- Run workflow: `./scripts/ap.sh workflow "query" --ticket=AP-1`
- Get help: `./scripts/ap.sh help`

### Using the service manager
- Start all services: `./scripts/start_ap.sh start`
- Start specific services: `./scripts/start_ap.sh start mcp_server frontend`
- Check service status: `./scripts/start_ap.sh status`
- Watch service status: `./scripts/start_ap.sh status --watch`
- Restart services: `./scripts/start_ap.sh restart`
- Stop all services: `./scripts/start_ap.sh stop`
- Or use the Python entry point: `ap-services status`

### Manual commands
- Install dependencies: `uv pip install -e ".[dev]"` or `pip install -e ".[dev]"`
- Run MCP server: `ap-server --host 127.0.0.1 --port 8000`
- Run CLI client: `ap-client [command] [options]`
- Run sample workflow: `ap-workflow "research query" --ticket AP-1 --doc doc1`
- Run linting: `ruff check .`
- Run type checking: `mypy src`
- Run tests: `pytest`
- Run tests with coverage: `pytest --cov=agent_provocateur`

### Web Search MCP Server
- Start the Web Search MCP server: `./scripts/ap_web_search.sh start`
- Stop the Web Search MCP server: `./scripts/ap_web_search.sh stop`
- Check Web Search MCP status: `./scripts/ap_web_search.sh status`
- Test web search functionality: `./scripts/ap_web_search.sh test --query=AI`
- Start full stack with Web Search: `./scripts/ap_web_search.sh full-stack`
- Configure the Brave API key in `web_search_mcp/.env`
- Docker/Podman is required to run the Web Search MCP server

## Server Responsibilities During Testing

For testing and debugging, follow these guidelines regarding server responsibilities:

1. **User Responsibilities**:
   - Starting and managing the main backend servers (ap-server, Redis, etc.)
   - Providing port information for running services
   - Clarifying which servers are already running

2. **Claude Responsibilities**:
   - Running specific commands for testing/debugging
   - Starting only components needed for testing (e.g., frontend server for UI testing)
   - Avoiding starting servers already managed by the user
   - Using provided port information to configure test commands

Example workflow:
```
User: "I've started the backend server on port 8000. Please test the frontend server connection."
Claude: [starts only the frontend server with appropriate backend URL]
```

## Testing Server Configuration

When running integration tests involving the frontend and backend servers:

1. **Backend Server**:
   - Should run on port 8765 to avoid conflicts with default port 8000
   - Use `--no-metrics` flag when running in test environments
   - Command: `python -m agent_provocateur.main --no-metrics --port 8765`

2. **Frontend Server**:
   - Should run on port 3001 to avoid conflicts with default port 3000
   - Configure with correct backend URL to port 8765
   - Command: `python frontend/server.py --port 3001 --backend-url http://localhost:8765`

3. **Health Endpoints**:
   - Backend health check: `http://localhost:8765/api/health`
   - Frontend health check: `http://localhost:3001/api/health`
   - Frontend backend status check: `http://localhost:3001/api/info`

## Project Overview
This project implements a multi-agent research system with:
1. MCP Server Mock for simulated tool interactions
2. MCP Client SDK for standardized tool access
3. A2A Messaging Layer for agent coordination
4. Sample agent implementations for collaborative workflows
5. Web UI for document viewing and processing
6. Web Search integration with real search providers (Brave, Google, Bing)

## Code Style Guidelines
- **Formatting**: 88 character line length (enforced by ruff)
- **Imports**: Group imports (stdlib, third-party, local) with blank lines between groups
- **Types**: Use type hints for all function parameters and return values
- **Naming**: 
  - snake_case for variables and functions
  - PascalCase for classes
- **Error handling**: Use explicit exception handling with specific exception types
- **Documentation**: Docstrings for all public functions, classes, and methods
- **Testing**: Write tests for all new functionality

## Project Structure
- Keep code organized in the `src/agent_provocateur` directory
- Place tests in the `tests` directory
- Frontend code is in the `frontend` directory
- Web Search MCP server in the `web_search_mcp` directory
- Follow Python package best practices
- Use type annotations for all functions
- Update documentation when making significant changes

## Current Project Status
- Phase 1 (MCP Tools Development) - Complete
  - MCP Server Mock
  - MCP Client SDK
  - CLI Demo

- Phase 2 (A2A Communication Development) - Complete
  - Message Schema: JSON definitions for TaskRequest, TaskResult, Heartbeat
  - Pub/Sub Infrastructure: In-memory broker and Redis implementation
  - Agent Messaging Module: Base agent framework with task handling and retries
  - Sample Workflow: Demo with JIRA, Doc, Search, and Synthesis agents

- Phase 3 (Web UI and CLI Enhancement) - Complete
  - FastAPI frontend server
  - Three-panel UI for document processing
  - Document upload and processing
  - XML research CLI integration
  - Web Search with real providers integration via MCP server