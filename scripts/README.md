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
  ./scripts/ap.sh help         # Show help information
  ```

- **`start_ap.sh`** - Service management script
  ```bash
  ./scripts/start_ap.sh start        # Start all services
  ./scripts/start_ap.sh start mcp_server frontend  # Start specific services
  ./scripts/start_ap.sh stop         # Stop all services
  ./scripts/start_ap.sh status       # Check service status
  ./scripts/start_ap.sh status --watch # Watch status continuously
  ./scripts/start_ap.sh restart      # Restart services
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

# Start services
./scripts/start_ap.sh start mcp_server frontend

# Run tests
./scripts/ap.sh test

# Check service status
./scripts/start_ap.sh status

# Stop services when done
./scripts/start_ap.sh stop
```

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