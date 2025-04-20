#!/bin/bash
# Unified startup script for Agent Provocateur
# This is a simplified bash wrapper around the Python service manager

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Ensure we're in the project root
cd "$(get_project_root)"

# Ensure required dependencies
ensure_package "psutil"

# Make the service manager executable
chmod +x "$SCRIPT_DIR/all_services.py"

# Ensure the virtual environment exists and is activated
ensure_tools

# Pass all arguments to the Python service manager
python "$SCRIPT_DIR/all_services.py" "$@"