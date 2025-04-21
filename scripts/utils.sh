#!/bin/bash
# Common utility functions for Agent Provocateur scripts

# Get the project root directory
get_project_root() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo "$(cd "$script_dir/.." && pwd)"
}

# Check if virtual environment exists
check_venv() {
    local project_root="$(get_project_root)"
    if [ ! -d "$project_root/.venv" ]; then
        echo "Virtual environment not found. Setting up..."
        if [ -f "$project_root/scripts/ap.sh" ]; then
            "$project_root/scripts/ap.sh" setup
            if [ $? -ne 0 ]; then
                echo "Environment setup failed. Please check errors and try again."
                return 1
            fi
        else
            echo "Could not find ap.sh to set up environment."
            return 1
        fi
    fi
    return 0
}

# Activate virtual environment
activate_venv() {
    local project_root="$(get_project_root)"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        source "$project_root/.venv/Scripts/activate"
    else
        # Unix/MacOS
        source "$project_root/.venv/bin/activate"
    fi
}

# Get container engine (docker or podman)
get_container_engine() {
    if command -v podman &> /dev/null; then
        echo "podman"
    elif command -v docker &> /dev/null; then
        echo "docker"
    else
        echo ""
    fi
}

# Ensure a Python package is installed in the virtual environment
ensure_package() {
    local package_name="$1"
    if ! pip show "$package_name" &> /dev/null; then
        echo "Installing required dependency: $package_name..."
        pip install "$package_name"
    fi
}

# Ensure we have all the tools we need
ensure_tools() {
    # Make sure scripts are executable
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    chmod +x "$script_dir"/*.py "$script_dir"/*.sh
    
    # Check if we're in a virtual environment
    if ! python -c "import sys; sys.exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)" &> /dev/null; then
        check_venv || return 1
        activate_venv
    fi
}

# Get the status of a specific service
get_service_status() {
    local service_name="$1"
    local project_root="$(get_project_root)"
    
    ensure_tools
    
    python "$project_root/scripts/all_services.py" status | grep -E "^$service_name" | awk '{print $2}'
}

# Get human-readable project name
get_project_name() {
    echo "Agent Provocateur"
}