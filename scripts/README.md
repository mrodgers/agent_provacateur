# Scripts

This directory contains utility scripts for the Agent Provocateur project.

## Overview

These scripts provide command-line tools for development, service management, and XML processing. They use shared utilities to ensure consistent behavior and reduce code duplication.

## Main Scripts

### Core Service Scripts

- **`start_ap.sh`** - Unified service management script
  ```bash
  ./scripts/start_ap.sh start        # Start all services
  ./scripts/start_ap.sh start document_service frontend  # Start specific services
  ./scripts/start_ap.sh start graphrag_service  # Start GraphRAG service
  ./scripts/start_ap.sh stop         # Stop all services
  ./scripts/start_ap.sh status       # Check service status
  ./scripts/start_ap.sh status --watch # Watch status continuously
  ./scripts/start_ap.sh restart      # Restart services
  ./scripts/start_ap.sh ports        # Check for port conflicts
  ```
  
- **`run_enhanced_mcp_server.sh`** - Enhanced Document Service API with improved documentation
  ```bash
  ./scripts/run_enhanced_mcp_server.sh                 # Start with auto-detection of services (uses uv)
  ./scripts/run_enhanced_mcp_server.sh --port 8001     # Use a specific port
  ./scripts/run_enhanced_mcp_server.sh --entity-port 9585 --graphrag-port 9584  # Configure service ports
  ./scripts/run_enhanced_mcp_server.sh --host 0.0.0.0  # Bind to all interfaces
  ./scripts/run_enhanced_mcp_server.sh --stop          # Stop the running enhanced server
  ```
  
  This script launches the enhanced Document Service API with improved API documentation and service integration:
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
  ./scripts/ap.sh server       # Start Document Service API
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

### XML Tools

#### Unified XML CLI (NEW)

- **`unified_xml_cli.py`** - Comprehensive XML tool combining functionality from multiple scripts
  ```bash
  # List all XML documents
  ./scripts/unified_xml_cli.py list
  
  # Get a specific XML document
  ./scripts/unified_xml_cli.py get DOC_ID [--content]
  
  # Upload a new XML document
  ./scripts/unified_xml_cli.py upload XML_FILE [--title TITLE]
  
  # Get researchable nodes for a document
  ./scripts/unified_xml_cli.py nodes DOC_ID
  
  # Analyze an XML file with XmlAgent
  ./scripts/unified_xml_cli.py analyze XML_FILE
  
  # Extract entities with GraphRAG integration
  ./scripts/unified_xml_cli.py entities DOC_ID
  
  # Extract Cisco commands from a document
  ./scripts/unified_xml_cli.py commands DOC_ID [--summary]
  
  # Validate XML structure
  ./scripts/unified_xml_cli.py validate --doc-id DOC_ID
  ./scripts/unified_xml_cli.py validate --file XML_FILE
  ```

#### Cisco XML Agent (NEW)

- **`cisco_xml_agent.py`** - Specialized agent for Cisco command extraction
  ```bash
  # Extract configuration commands
  ./scripts/cisco_xml_agent.py extract DOC_ID [--json]
  
  # Categorize commands by function
  ./scripts/cisco_xml_agent.py categorize DOC_ID
  
  # Generate human-readable summaries
  ./scripts/cisco_xml_agent.py summarize DOC_ID
  
  # Format commands for documentation
  ./scripts/cisco_xml_agent.py format DOC_ID [--format markdown|html|json|text]
  ```

#### Legacy XML Tools (DEPRECATED)

These tools are maintained for backward compatibility but will be removed in a future release:

- **`xml_cli.py`** - XML document management CLI (use `unified_xml_cli.py` instead)
- **`xml_agent_cli.py`** - XML Agent verification CLI (use `unified_xml_cli.py` instead)
- **`xml_command_agent.py`** - Cisco command extraction (use `cisco_xml_agent.py` instead)
- **`extract_cisco_commands.py`** - Command extraction script (use `cisco_xml_agent.py extract` instead)

### System Testing Scripts

- **`test_system_e2e.sh`** - End-to-end system testing script
  ```bash
  ./scripts/test_system_e2e.sh             # Test full backend workflow with real services
  ```
  
  This script tests the complete backend workflow:
  1. Upload XML file to the backend
  2. Extract entities using the entity detector
  3. Research entities using GraphRAG
  4. Generate a result XML with research and entities
  
  Requires all services (Document Service, entity detector, and GraphRAG) to be running.

- **`robust_system_test.sh`** - Enhanced system testing with resilience
  ```bash
  ./scripts/robust_system_test.sh          # Run robust system test with retry mechanisms
  ```

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
./scripts/start_ap.sh start document_service frontend entity_detector_mcp

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

# Use the enhanced Document Service API with improved documentation
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

### XML Processing Workflow (NEW)

```bash
# Start services
./scripts/start_ap.sh start

# Upload XML document with the unified CLI
./scripts/unified_xml_cli.py upload examples/sample.xml --title "Sample"

# Check uploaded documents
./scripts/unified_xml_cli.py list

# Get document details
./scripts/unified_xml_cli.py get xml1

# Get researchable nodes
./scripts/unified_xml_cli.py nodes xml1

# Extract entities with GraphRAG integration
./scripts/unified_xml_cli.py entities xml1

# For Cisco documents, extract commands
./scripts/unified_xml_cli.py commands xml1 --summary

# For advanced Cisco command processing
./scripts/cisco_xml_agent.py categorize xml1

# End-to-end system test (requires all services running)
./scripts/test_system_e2e.sh

# If services not running, use the mock test instead
./scripts/mock_system_test.sh
```

### Legacy XML Workflow (DEPRECATED)

```bash
# Upload XML document (DEPRECATED - use unified_xml_cli.py instead)
./scripts/xml_cli.py upload examples/sample.xml --analyze

# Check uploaded documents (DEPRECATED - use unified_xml_cli.py instead)
./scripts/xml_cli.py list

# Create verification plan (DEPRECATED - use unified_xml_cli.py instead)
./scripts/xml_agent_cli.py plan xml1

# Run verification (DEPRECATED - use unified_xml_cli.py instead)
./scripts/xml_agent_cli.py verify xml1 --search-depth high
```

## Migration Guide

The following legacy scripts have been consolidated into new unified tools:

- `xml_cli.py` → `unified_xml_cli.py list|get|upload`
- `xml_agent_cli.py` → `unified_xml_cli.py analyze|entities`
- `xml_command_agent.py` → `cisco_xml_agent.py`
- `extract_cisco_commands.py` → `unified_xml_cli.py commands`

Service names have also been updated for clarity:
- `mcp_server` is now `document_service` (Document Service API)
- `graphrag_mcp_py` is now `graphrag_service` (GraphRAG Service)
- TypeScript GraphRAG implementation has been removed in favor of the Python version

## Extending Scripts

When adding new functionality:

1. Use the shared utilities in `utils.sh` and `xml_utils.py`
2. Follow the existing patterns for command-line argument parsing
3. Document the new functionality in this README
4. Use consistent error handling and user feedback
5. Add new scripts to the unified interfaces where possible, rather than creating standalone scripts