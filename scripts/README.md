# Scripts

This directory contains utility scripts for the Agent Provocateur project.

## Overview

These scripts provide command-line tools for development, service management, and XML processing. They use shared utilities to ensure consistent behavior and reduce code duplication.

## Main Scripts

### Core Service Scripts

- **`start_ap.sh`** - Unified service management script
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
  
- **`run_enhanced_mcp_server.sh`** - Enhanced MCP server with improved API documentation
  ```bash
  ./scripts/run_enhanced_mcp_server.sh                 # Start with auto-detection of services (uses uv)
  ./scripts/run_enhanced_mcp_server.sh --port 8001     # Use a specific port
  ./scripts/run_enhanced_mcp_server.sh --entity-port 9585 --graphrag-port 9584  # Configure service ports
  ./scripts/run_enhanced_mcp_server.sh --host 0.0.0.0  # Bind to all interfaces
  ./scripts/run_enhanced_mcp_server.sh --stop          # Stop the running enhanced MCP server
  ```
  
  This script launches the enhanced MCP server with improved API documentation and service integration:
  1. Automatically detects Entity Detector and GraphRAG services
  2. Provides port conflict resolution
  3. Configures proxy endpoints for end-to-end workflow processing
  4. Creates comprehensive API documentation at `/docs`

- **`cleanup_all.sh`** - Comprehensive system cleanup
  ```bash
  ./scripts/cleanup_all.sh                # Force kill all running services
  ./scripts/cleanup_all.sh --no-force     # Try graceful shutdown first
  ./scripts/cleanup_all.sh --verbose      # Show detailed process information
  ./scripts/cleanup_all.sh --no-clean-pid # Don't remove PID files
  ```
  
  Use this script when services aren't stopping properly, port conflicts occur, or to ensure a clean environment before starting services.

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

- **`test_component_library.sh`** - UI component testing script
  ```bash
  ./scripts/test_component_library.sh              # Start test server and open browser
  ./scripts/test_component_library.sh --no-clean   # Start without stopping existing servers
  ./scripts/test_component_library.sh --run-tests  # Auto-run tests after starting
  ./scripts/test_component_library.sh --no-browser # Start server without opening browser
  ./scripts/test_component_library.sh --browser firefox # Use specific browser
  ```
  
  This script starts a dedicated server for UI component testing. It uses the `cleanup_all.sh` script to ensure a clean test environment, preventing "already declared" errors and port conflicts.

- **`cleanup_all.sh`** - Comprehensive system cleanup
  ```bash
  ./scripts/cleanup_all.sh                # Force kill all running services
  ./scripts/cleanup_all.sh --no-force     # Try graceful shutdown first
  ./scripts/cleanup_all.sh --verbose      # Show detailed process information
  ./scripts/cleanup_all.sh --no-clean-pid # Don't remove PID files
  ```
  
  Use this script when services aren't stopping properly, port conflicts occur, or to ensure a clean environment before starting services.

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

- **`test_system_e2e.sh`** - End-to-end system testing script
  ```bash
  ./scripts/test_system_e2e.sh             # Test full backend workflow with real services
  ```
  
  This script tests the complete backend workflow:
  1. Upload XML file to the backend
  2. Extract entities using the entity detector
  3. Research entities using GraphRAG
  4. Generate a result XML with research and entities
  
  Requires all services (MCP server, entity detector, and GraphRAG) to be running.

- **`mock_system_test.sh`** - Mock system testing script
  ```bash
  ./scripts/mock_system_test.sh            # Test workflow with mock/simulated services
  ```
  
  This script simulates the complete backend workflow without requiring services to be running.
  It uses the sample XML file directly and generates mock entities and research results.
  Useful for testing the general workflow structure or when services aren't available.

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

# Clean up any existing services first (recommended for a clean start)
./scripts/cleanup_all.sh

# Start all services
./scripts/start_ap.sh start

# Alternatively, start specific services only
./scripts/start_ap.sh start mcp_server frontend web_search_mcp

# For development with custom frontend settings
./scripts/start_frontend.sh --debug --port 3001

# Run tests
./scripts/ap.sh test

# Test UI components specifically
./scripts/test_component_library.sh

# Check service status
./scripts/start_ap.sh status

# Monitor services continuously
./scripts/start_ap.sh status --watch

# Use the enhanced MCP server with improved documentation
./scripts/run_enhanced_mcp_server.sh

# Access the enhanced API documentation at http://localhost:8000/docs

# Stop services when done
./scripts/start_ap.sh stop

# If services aren't stopping cleanly:
./scripts/cleanup_all.sh
```

### Web Search Workflow

```bash
# Start Web Search MCP using the general service manager
./scripts/start_ap.sh start web_search_mcp

# Alternatively, use the dedicated web search manager
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

> **Note**: The following scripts have been moved to the `scripts/deprecated` directory:
> - `run_web_search_mcp.sh` - Replaced by `manage_web_search.sh`
> - `start_with_web_search.sh` - Replaced by `start_ap.sh start web_search_mcp`
> - `ap_web_search.sh` - Replaced by `ap.sh web-search`

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

# End-to-end system test (requires all services running)
./scripts/test_system_e2e.sh

# If services not running, use the mock test instead
./scripts/mock_system_test.sh
```

## Extending Scripts

When adding new functionality:

1. Use the shared utilities in `utils.sh` and `xml_utils.py`
2. Follow the existing patterns for command-line argument parsing
3. Document the new functionality in this README
4. Use consistent error handling and user feedback