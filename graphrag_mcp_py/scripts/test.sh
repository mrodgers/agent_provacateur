#!/bin/bash
# Run tests for GraphRAG MCP Server (Python implementation)

# Change to the project root directory
cd "$(dirname "$0")/.."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Check for pytest
if ! python3 -c "import pytest" &> /dev/null; then
    echo "Installing pytest..."
    pip install pytest
fi

# Run tests
echo "Running GraphRAG MCP Server (Python) tests..."
python3 -m pytest tests/ -v