#!/bin/bash

# Unified startup script for Agent Provocateur
# This is a simplified bash wrapper around the Python service manager

# Ensure we're in the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Check for Python dependencies
check_dependencies() {
    if ! pip show psutil &> /dev/null; then
        echo "Installing required dependencies..."
        pip install psutil
    fi
}

# Setup virtual environment if needed (copied from ap.sh)
check_venv() {
    if [ ! -d ".venv" ]; then
        echo "Virtual environment not found. Setting up..."
        "$SCRIPT_DIR/ap.sh" setup
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

# Make the service manager executable
chmod +x "$SCRIPT_DIR/all_services.py"

# Ensure the virtual environment exists and is activated
check_venv
activate_venv

# Check for Python dependencies
check_dependencies

# Pass all arguments to the Python service manager
python "$SCRIPT_DIR/all_services.py" "$@"