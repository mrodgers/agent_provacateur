#!/bin/bash

# Script to run tests with proper environment setup using uv

# Ensure we're in the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Running setup script first..."
    bash scripts/setup_env.sh
    if [ $? -ne 0 ]; then
        echo "Environment setup failed. Please check errors and try again."
        exit 1
    fi
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source .venv/Scripts/activate
else
    # Unix/MacOS
    source .venv/bin/activate
fi

# Check for arguments
if [ $# -eq 0 ]; then
    # Run default test suite
    echo "Running all tests..."
    python -m pytest
else
    # Run specific tests if provided
    echo "Running specified tests..."
    python -m pytest "$@"
fi

# Run coverage if requested
if [[ "$*" == *"--cov"* ]]; then
    echo "Coverage report already generated."
else
    read -p "Generate coverage report? (y/n) " gen_coverage
    if [[ $gen_coverage == "y" || $gen_coverage == "Y" ]]; then
        echo "Generating coverage report..."
        python -m pytest --cov=src.agent_provocateur
    fi
fi

# Run linting
read -p "Run linting checks? (y/n) " run_linting
if [[ $run_linting == "y" || $run_linting == "Y" ]]; then
    echo "Running linting with ruff..."
    ruff check .
    
    echo "Running type checking with mypy..."
    mypy src
fi