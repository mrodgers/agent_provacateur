#!/bin/bash

# Universal utility script for Agent Provocateur development

# Ensure we're in the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Check if virtual environment exists
check_venv() {
    if [ ! -d ".venv" ]; then
        echo "Virtual environment not found. Setting up..."
        setup_env
        if [ $? -ne 0 ]; then
            echo "Environment setup failed. Please check errors and try again."
            exit 1
        fi
    fi
}

# Activate virtual environment
activate_venv() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        source .venv/Scripts/activate
    else
        # Unix/MacOS
        source .venv/bin/activate
    fi
}

# Setup environment command
setup_env() {
    # Check if we're updating existing environment
    local update=0
    if [ -d ".venv" ]; then
        update=1
        echo "Existing environment detected. Updating dependencies..."
    else
        echo "Creating new virtual environment using uv..."
        # Check if uv is installed
        if ! command -v uv &> /dev/null; then
            echo "uv is not installed. Installing it now..."
            curl -sSf https://astral.sh/uv/install.sh | bash
            echo "Please restart your shell or run 'source ~/.bashrc' (or equivalent) to update your PATH"
            exit 1
        fi
        
        # Create virtual environment
        uv venv
    fi
    
    # Activate environment for script usage
    activate_venv
    
    # Install dependencies with uv
    echo "Installing project dependencies with uv..."
    uv pip install -e ".[dev]"
    
    # Optional: Install redis dependency if needed
    if [ $update -eq 0 ]; then
        read -p "Install Redis dependency for production messaging? (y/n) " install_redis
    else
        # Check if Redis is already installed when updating
        if pip freeze | grep -q redis; then
            install_redis="y"
        else
            read -p "Install Redis dependency for production messaging? (y/n) " install_redis
        fi
    fi
    
    if [[ $install_redis == "y" || $install_redis == "Y" ]]; then
        echo "Installing Redis dependencies..."
        uv pip install -e ".[redis]"
    fi
    
    echo -e "\nEnvironment ${update_str:-setup} complete! To activate the environment, run:"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo ".venv\\Scripts\\activate"
    else
        echo "source .venv/bin/activate"
    fi
}

# Run tests command
run_tests() {
    check_venv
    activate_venv
    
    # Check for test arguments
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
            python -m pytest --cov=agent_provocateur
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
}

# Start server command
start_server() {
    check_venv
    activate_venv
    
    # Default values
    HOST="127.0.0.1"
    PORT="8000"
    
    # Check for arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --host=*)
                HOST="${1#*=}"
                shift
                ;;
            --port=*)
                PORT="${1#*=}"
                shift
                ;;
            *)
                echo "Unknown parameter: $1"
                echo "Usage: $0 server [--host=127.0.0.1] [--port=8000]"
                exit 1
                ;;
        esac
    done
    
    echo "Starting MCP server on $HOST:$PORT..."
    ap-server --host "$HOST" --port "$PORT"
}

# Run workflow command
run_workflow() {
    check_venv
    activate_venv
    
    if [ $# -eq 0 ]; then
        echo "Usage: $0 workflow <query> [--ticket=TICKET-ID] [--doc=DOC-ID]"
        exit 1
    fi
    
    QUERY="$1"
    shift
    
    # Parse additional arguments
    TICKET=""
    DOC=""
    while [[ $# -gt 0 ]]; do
        case $1 in
            --ticket=*)
                TICKET="${1#*=}"
                shift
                ;;
            --doc=*)
                DOC="${1#*=}"
                shift
                ;;
            *)
                echo "Unknown parameter: $1"
                echo "Usage: $0 workflow <query> [--ticket=TICKET-ID] [--doc=DOC-ID]"
                exit 1
                ;;
        esac
    done
    
    # Build command
    CMD="ap-workflow \"$QUERY\""
    if [ -n "$TICKET" ]; then
        CMD="$CMD --ticket $TICKET"
    fi
    if [ -n "$DOC" ]; then
        CMD="$CMD --doc $DOC"
    fi
    
    echo "Running workflow: $CMD"
    eval $CMD
}

# Show help information
show_help() {
    echo "Agent Provocateur Development Utility"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Available commands:"
    echo "  setup    - Create or update virtual environment with dependencies"
    echo "  test     - Run tests (with optional arguments for pytest)"
    echo "  server   - Start the MCP server"
    echo "  workflow - Run a sample agent workflow"
    echo "  help     - Show this help information"
    echo ""
    echo "Examples:"
    echo "  $0 setup                                  # Setup environment"
    echo "  $0 test                                   # Run all tests"
    echo "  $0 test tests/test_main.py               # Run specific tests"
    echo "  $0 server                                # Start server on localhost:8000"
    echo "  $0 server --host=0.0.0.0 --port=8080     # Start server with custom host/port"
    echo "  $0 workflow \"research query\" --ticket=AP-1 # Run a workflow"
}

# Main command dispatcher
case "$1" in
    setup)
        shift
        setup_env "$@"
        ;;
    test)
        shift
        run_tests "$@"
        ;;
    server)
        shift
        start_server "$@"
        ;;
    workflow)
        shift
        run_workflow "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac