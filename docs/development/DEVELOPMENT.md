# Development Guide

This document outlines the development workflow for the Agent Provocateur project using uv for virtual environment management.

## Environment Setup

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and environment manager
- Docker or Podman (optional, for monitoring)
- Redis (optional, for production messaging)

### Port Usage

The Agent Provocateur system uses several ports for different services:

| Port | Service | Notes |
|------|---------|-------|
| 3000 | Grafana (monitoring) | Can conflict with frontend if on same port |
| 3001 | Frontend server | Default port for the web UI | 
| 8000 | MCP Server | Backend API service |
| 9090 | Prometheus | Metrics storage |
| 9091 | Pushgateway | Metrics collection |

**Known Port Conflicts:**
- Grafana uses port 3000, which can conflict with React development servers or the frontend if configured to use port 3000
- The MCP server port 8000 can conflict with Django or other development servers

**Diagnosing Port Conflicts:**
```bash
# Check for port conflicts
./scripts/start_ap.sh ports

# Check a specific port
./scripts/start_ap.sh ports --check 3000
```

### Unified Development Scripts

We provide unified scripts that handle all development tasks:

#### Development Script (`ap.sh`)

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

#### Service Management Script (`start_ap.sh`)

```bash
# Make the script executable (if needed)
chmod +x scripts/start_ap.sh

# Get status of all services
./scripts/start_ap.sh status
```

The service manager supports the following commands:

| Command | Description | Example |
|---------|-------------|---------|
| `start` | Start services | `./scripts/start_ap.sh start` or `./scripts/start_ap.sh start mcp_server frontend` |
| `stop` | Stop services | `./scripts/start_ap.sh stop` |
| `restart` | Restart services | `./scripts/start_ap.sh restart` |
| `status` | Check service status | `./scripts/start_ap.sh status` or `./scripts/start_ap.sh status --watch` |

### Common Development Examples

```bash
# Setup environment
./scripts/ap.sh setup

# Run all tests
./scripts/ap.sh test

# Run specific tests
./scripts/ap.sh test tests/test_a2a_messaging.py

# Start all services
./scripts/start_ap.sh start

# Check service status
./scripts/start_ap.sh status

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

# Run tests with standard pytest
pytest

# Run tests with uv (recommended)
uv run pytest              # Run all tests with pytest via uv
uv run pytest -v           # Run with verbose output
uv run python -m pytest    # Run pytest as a module
uv run pytest --cov=agent_provocateur  # Run with coverage

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
│   ├── ap.sh                     # Development script
│   ├── start_ap.sh               # Service management script
│   ├── all_services.py           # Service management implementation
│   ├── xml_cli.py                # XML document CLI
│   └── xml_agent_cli.py          # XML agent CLI
├── logs/                         # Service logs (generated)
├── monitoring/                   # Monitoring configuration
│   ├── docker-compose.yml        # Container definitions
│   ├── prometheus.yml            # Prometheus configuration
│   └── grafana/                  # Grafana dashboards
├── .venv/                        # Virtual environment (generated)
└── pyproject.toml                # Project configuration
```

## Development Workflow

1. **Set up the environment**: Run `./scripts/ap.sh setup`
2. **Start required services**: Run `./scripts/start_ap.sh start`
3. **Make changes**: Edit code in the `src/agent_provocateur` directory
4. **Run tests**: Use `./scripts/ap.sh test` to validate changes
5. **Test manually**: Start the server and interact with it using the CLI or sample workflow
6. **Monitor system status**: Use `./scripts/start_ap.sh status --watch` in a separate terminal

## Testing

The project has a comprehensive test suite for testing both frontend and backend components.

### Test Categories

1. **Unit Tests**: Test individual components in isolation
2. **Frontend Tests**: Test the frontend server functionality
3. **Backend Tests**: Test the backend MCP server API
4. **Integration Tests**: End-to-end tests that verify the frontend and backend work together

### Running Tests

Using the existing ap.sh script:
```bash
# Run all tests
./scripts/ap.sh test

# Run specific tests
./scripts/ap.sh test tests/test_frontend_server.py
./scripts/ap.sh test tests/test_backend_api.py
./scripts/ap.sh test tests/test_frontend_backend_integration.py
```

Using the dedicated test harness script:
```bash
# Run all tests
./scripts/run_tests.py

# Run only frontend tests
./scripts/run_tests.py --type frontend

# Run only backend tests
./scripts/run_tests.py --type backend

# Run only integration tests
./scripts/run_tests.py --type integration

# Generate coverage report
./scripts/run_tests.py --coverage

# Stop on first failure
./scripts/run_tests.py --failfast
```

### Test Fixtures

The test suite provides several fixtures:

- `xml_test_dir`: Path to XML test data
- `simple_xml_path`, `complex_xml_path`: Paths to sample XML files
- `client`: FastAPI test client for API testing
- `test_upload_dir`: Temporary directory for file uploads
- `frontend_server`, `backend_server`: Running server instances for integration tests

### Debugging Test Failures

Common issues during testing:

1. **Port conflicts**: Integration tests require ports 3001 and 8000 to be available
2. **Missing test data**: Ensure the test XML files exist in the expected locations
3. **Connection timeouts**: Long-running tests might time out if server startup is slow
4. **Environment variables**: Some tests might require specific environment variables

To troubleshoot failing tests:
```bash
# Run tests with increased verbosity
./scripts/run_tests.py --type integration -v

# Check for processes using test ports
lsof -i :3001
lsof -i :8000

# Ensure test files exist
ls -la tests/test_data/xml_documents/

## Service Management

The service manager handles all components of the Agent Provocateur system:

| Service | Description | Required Dependencies |
|---------|-------------|----------------------|
| monitoring | Prometheus, Pushgateway, and Grafana for metrics | Docker or Podman |
| redis | Redis for agent-to-agent messaging | Redis server & client |
| mcp_server | Main backend server | None |
| frontend | Web UI server | None |

### Logs

Service logs are stored in the `logs/` directory:
- `logs/mcp_server.out.log` - MCP server standard output
- `logs/mcp_server.err.log` - MCP server error output
- `logs/frontend.out.log` - Frontend server standard output
- `logs/frontend.err.log` - Frontend server error output
- `logs/monitoring.out.log` - Monitoring stack standard output
- `logs/monitoring.err.log` - Monitoring stack error output

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| MCP Server | 8000 | Main backend API |
| Frontend | 3001 | Web UI server |
| Prometheus | 9090 | Metrics storage and querying |
| Pushgateway | 9091 | Metrics ingestion |
| Grafana | 3000 | Metrics visualization |
| Redis | 6379 | Agent-to-agent communication |

### Troubleshooting Port Conflicts

Common port conflicts:

1. **Port 3000**: Grafana (part of monitoring) uses port 3000, which can conflict with the frontend or React development servers if configured to use the same port.

2. **Port 8000**: The MCP server uses port 8000, which can conflict with other development servers (Django, Python HTTP servers, etc).

#### Identifying Port Conflicts

```bash
# Check all common ports
./scripts/start_ap.sh ports

# Check a specific port
./scripts/start_ap.sh ports --check 3000
```

#### Resolving Port Conflicts

1. **Use a different port for services**:
   ```bash
   # Start frontend on a different port
   cd frontend && python server.py --host 127.0.0.1 --port 3002
   
   # Start MCP server on a different port
   ./scripts/ap.sh server --port 8001
   ```

2. **Stop conflicting processes**:
   ```bash
   # On Linux/macOS
   lsof -i :3000 | grep LISTEN
   kill <PID>
   
   # On Windows
   netstat -ano | findstr :3000
   taskkill /PID <PID> /F
   ```

3. **Configure explicit ports in URLs**:
   ```
   http://localhost:3001/  # Frontend UI
   http://localhost:8000/  # API
   ```

4. **Update frontend JavaScript code** to use explicit port if needed:
   ```javascript
   // In landing.js, document_viewer.js, etc.
   const response = await fetch('http://localhost:3001/api/endpoint');
   ```

## Dependency Management

When adding new dependencies:

1. Add them to `pyproject.toml` in the appropriate section
2. Reinstall the package: `./scripts/ap.sh setup` (it will update an existing environment)