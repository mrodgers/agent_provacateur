# Scripts

This directory contains utility scripts for the Agent Provocateur project.

## Overview

These scripts provide command-line tools for development, service management, and XML processing. They use shared utilities to ensure consistent behavior and reduce code duplication.

## Main Scripts

### Development Scripts

- **`ap.sh`** - Main development utility script
  ```bash
  ./scripts/ap.sh setup        # Create/update virtual environment
  ./scripts/ap.sh test         # Run tests
  ./scripts/ap.sh server       # Start MCP server
  ./scripts/ap.sh workflow     # Run a sample workflow
  ./scripts/ap.sh web-search   # Test web search functionality
  ./scripts/ap.sh help         # Show help information
  ```

- **`start_ap.sh`** - Service management script
  ```bash
  ./scripts/start_ap.sh start        # Start all services
  ./scripts/start_ap.sh start mcp_server frontend  # Start specific services
  ./scripts/start_ap.sh start web_search_mcp  # Start Web Search MCP server
  ./scripts/start_ap.sh stop         # Stop all services
  ./scripts/start_ap.sh status       # Check service status
  ./scripts/start_ap.sh status --watch # Watch status continuously
  ./scripts/start_ap.sh restart      # Restart services
  ./scripts/start_ap.sh ports        # Check for port conflicts
  ```

- **`start_frontend.sh`** - Dedicated frontend server script
  ```bash
  ./scripts/start_frontend.sh               # Start with automatic port detection
  ./scripts/start_frontend.sh --port 3002   # Use a specific port
  ./scripts/start_frontend.sh --debug       # Run with detailed logging
  ./scripts/start_frontend.sh --clean       # Clean logs before starting
  ./scripts/start_frontend.sh --host 0.0.0.0 --backend-url http://example.com:8000  # Custom config
  ```

- **`stop_frontend.sh`** - Frontend server termination script
  ```bash
  ./scripts/stop_frontend.sh         # Gracefully stop frontend server
  ./scripts/stop_frontend.sh --force # Force stop any stubborn processes
  ```

### XML Tools

- **`xml_cli.py`** - XML document management CLI
  ```bash
  ./scripts/xml_cli.py list                # List all XML documents
  ./scripts/xml_cli.py get xml1            # Get XML document details
  ./scripts/xml_cli.py get xml1 --content  # Show full content
  ./scripts/xml_cli.py upload file.xml     # Upload a new XML document
  ```

- **`xml_agent_cli.py`** - XML Agent verification CLI
  ```bash
  ./scripts/xml_agent_cli.py identify --file file.xml # Identify nodes
  ./scripts/xml_agent_cli.py plan xml1                # Plan verification
  ./scripts/xml_agent_cli.py verify xml1              # Verify XML document
  ```

### Goal Refinement Tools

- **`goal_refiner_cli.py`** - Goal Refinement CLI
  ```bash
  ./scripts/goal_refiner_cli.py "Research machine learning and extract entities from document"
  ./scripts/goal_refiner_cli.py "Search for information about AI" --max-results 10
  ./scripts/goal_refiner_cli.py "Analyze XML document" --doc-id xml1
  ./scripts/goal_refiner_cli.py "Research quantum computing" --provider google --json
  ```

## Utility Files

- **`utils.sh`** - Shared Bash functions for scripts
  - Virtual environment management
  - Project path resolution
  - Dependency checking
  - Service status utilities

- **`xml_utils.py`** - Shared Python utilities for XML tools
  - File path resolution
  - Python path setup
  - Server connection checking
  - API URL management

- **`all_services.py`** - Python service manager implementation
  - Handles starting/stopping of all required services
  - Monitors service status
  - Handles dependencies between services
  - Creates and manages logs

## Usage Examples

### Development Workflow

```bash
# Setup environment
./scripts/ap.sh setup

# Method 1: Using general service manager
./scripts/start_ap.sh start mcp_server frontend

# Method 2: Using specialized frontend scripts (recommended for development)
./scripts/start_ap.sh start mcp_server  # Start the backend
./scripts/start_frontend.sh --debug     # Start frontend with debugging

# Run tests
./scripts/ap.sh test

# Check service status
./scripts/start_ap.sh status

# Stop services when done
./scripts/stop_frontend.sh     # Stop the frontend first
./scripts/start_ap.sh stop     # Stop remaining services
```

### Web Search Workflow

```bash
# Method 1: Using the general service manager
./scripts/start_ap.sh start web_search_mcp

# Method 2: Using the dedicated web search manager (recommended)
./scripts/manage_web_search.sh start
./scripts/manage_web_search.sh start --port 8081 --debug  # With custom options

# Test web search with a query
./scripts/ap.sh web-search --query "latest AI developments"

# Test with a specific provider
./scripts/ap.sh web-search --query "climate change" --provider google

# Check web search server status
./scripts/manage_web_search.sh status

# Stop the server when done
./scripts/manage_web_search.sh stop
```

> **Note**: The older `run_web_search_mcp.sh` and `start_with_web_search.sh` scripts are deprecated and will be removed in a future update. Please use `manage_web_search.sh` instead.

### XML Processing Workflow

```bash
# Start services
./scripts/start_ap.sh start

# Upload XML document
./scripts/xml_cli.py upload examples/sample.xml --analyze

# Check uploaded documents
./scripts/xml_cli.py list

# Create verification plan
./scripts/xml_agent_cli.py plan xml1

# Run verification
./scripts/xml_agent_cli.py verify xml1 --search-depth high
```

## Extending Scripts

When adding new functionality:

1. Use the shared utilities in `utils.sh` and `xml_utils.py`
2. Follow the existing patterns for command-line argument parsing
3. Document the new functionality in this README
4. Use consistent error handling and user feedback