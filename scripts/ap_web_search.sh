#!/bin/bash
# Unified Web Search MCP Management Script for Agent Provocateur

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
PROJECT_ROOT="$(get_project_root)"

# Default ports
WEB_SEARCH_PORT=8080

# Function to show help information
show_help() {
    echo "Agent Provocateur Web Search Manager"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Available commands:"
    echo "  start      - Start the Web Search MCP server"
    echo "  stop       - Stop the Web Search MCP server"
    echo "  status     - Check Web Search MCP server status"
    echo "  test       - Run Web Search tests"
    echo "  full-stack - Start Agent Provocateur with Web Search integration"
    echo "  help       - Show this help information"
    echo ""
    echo "Options:"
    echo "  --port=PORT - Specify port for Web Search MCP (default: 8080)"
    echo "  --query=QUERY - Used with 'test' to specify search query"
    echo ""
    echo "Examples:"
    echo "  $0 start             # Start Web Search MCP server"
    echo "  $0 test --query=AI   # Test Web Search with 'AI' query"
    echo "  $0 full-stack        # Start all services including Web Search"
}

# Function to check if Web Search MCP server is running
check_web_search_running() {
    local container_name="web-search-mcp"
    local container_engine=$(get_container_engine)
    
    if [ -z "$container_engine" ]; then
        echo "No container engine (Docker/Podman) found. Please install one."
        return 1
    fi
    
    $container_engine ps | grep -q "$container_name"
    return $?
}

# Function to start Web Search MCP server
start_web_search() {
    local port=$1
    
    if check_web_search_running; then
        echo "Web Search MCP server is already running."
        return 0
    fi
    
    echo "Starting Web Search MCP Server on port $port..."
    echo "Using Brave API key from web_search_mcp/.env"
    
    # Check if podman or docker is available
    local container_engine=$(get_container_engine)
    if [ -z "$container_engine" ]; then
        echo "Error: Neither podman nor docker is available. Please install one of them."
        return 1
    fi
    
    echo "Using container command: $container_engine"
    
    # Check if the container image exists
    local image_exists=false
    if [ "$container_engine" = "podman" ]; then
        if podman image exists agent-provocateur/web-search-mcp:latest 2>/dev/null; then
            image_exists=true
        fi
    else
        # For Docker, we need to use a different approach
        if docker image inspect agent-provocateur/web-search-mcp:latest >/dev/null 2>&1; then
            image_exists=true
        fi
    fi
    
    # Build the image if it doesn't exist
    if [ "$image_exists" != "true" ]; then
        echo "Container image not found. Building it now..."
        cd "$PROJECT_ROOT/web_search_mcp"
        ./scripts/build.sh
    fi
    
    # Run the container with environment variables from .env
    echo "Starting web-search-mcp container on port $port..."
    cd "$PROJECT_ROOT/web_search_mcp"
    $container_engine run -d --rm -p "${port}:8080" --name web-search-mcp --env-file=.env agent-provocateur/web-search-mcp:latest
    
    # Check if container started successfully
    if check_web_search_running; then
        echo "Web Search MCP server started on port $port"
        echo "Set WEB_SEARCH_MCP_URL=http://localhost:$port environment variable when running the WebSearchAgent"
        return 0
    else
        echo "Failed to start Web Search MCP server. Check for errors."
        return 1
    fi
}

# Function to stop Web Search MCP server
stop_web_search() {
    if ! check_web_search_running; then
        echo "Web Search MCP server is not running."
        return 0
    fi
    
    local container_engine=$(get_container_engine)
    echo "Stopping Web Search MCP server..."
    $container_engine stop web-search-mcp
    
    # Verify it stopped
    if ! check_web_search_running; then
        echo "Web Search MCP server stopped successfully."
        return 0
    else
        echo "Failed to stop Web Search MCP server."
        return 1
    fi
}

# Function to check Web Search MCP server status
check_web_search_status() {
    if check_web_search_running; then
        local container_engine=$(get_container_engine)
        echo "Web Search MCP server is running."
        echo "Container details:"
        $container_engine ps --filter name=web-search-mcp
        return 0
    else
        echo "Web Search MCP server is not running."
        return 1
    fi
}

# Function to run Web Search tests
run_web_search_tests() {
    local query=$1
    local port=$2
    
    # Ensure Web Search MCP is running
    if ! check_web_search_running; then
        echo "Web Search MCP server is not running. Starting it now..."
        start_web_search "$port"
    fi
    
    # Run the test script
    echo "Running Web Search tests..."
    export WEB_SEARCH_MCP_URL="http://localhost:$port"
    
    if [ -n "$query" ]; then
        python "$SCRIPT_DIR/test_web_search.py" --query="$query"
    else
        python "$SCRIPT_DIR/test_web_search.py"
    fi
    
    return $?
}

# Function to start full stack with Web Search
start_full_stack() {
    local port=$1
    
    # First start the Web Search MCP
    start_web_search "$port"
    
    # Then start the main Agent Provocateur server
    echo "Starting Agent Provocateur..."
    export WEB_SEARCH_MCP_URL="http://localhost:$port"
    python -m agent_provocateur.main
}

# Parse command line arguments
COMMAND=""
PORT="$WEB_SEARCH_PORT"
QUERY=""

# Parse the first argument as command
if [ $# -gt 0 ]; then
    COMMAND="$1"
    shift
    
    # Parse remaining arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --port=*)
                PORT="${1#*=}"
                ;;
            --query=*)
                QUERY="${1#*=}"
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done
fi

# Execute the appropriate command
case "$COMMAND" in
    start)
        start_web_search "$PORT"
        ;;
    stop)
        stop_web_search
        ;;
    status)
        check_web_search_status
        ;;
    test)
        run_web_search_tests "$QUERY" "$PORT"
        ;;
    full-stack)
        start_full_stack "$PORT"
        ;;
    help|"")
        show_help
        ;;
    *)
        echo "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
