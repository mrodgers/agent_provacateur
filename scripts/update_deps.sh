#!/bin/bash

# Script to update dependencies after changes to pyproject.toml

# Ensure we're in the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Running setup script instead..."
    bash scripts/setup_env.sh
    exit $?
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source .venv/Scripts/activate
else
    # Unix/MacOS
    source .venv/bin/activate
fi

echo "Updating development dependencies..."
uv pip install -e ".[dev]"

# Check if Redis is installed and update if necessary
if pip freeze | grep -q redis; then
    echo "Updating Redis dependencies..."
    uv pip install -e ".[redis]"
fi

echo "Dependencies updated successfully!"
echo "You can now run './scripts/run_tests.sh' to verify tests are working correctly."