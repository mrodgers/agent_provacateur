#!/bin/bash
# Unified Web Search MCP service management script
# This script provides start, stop, and status functionality for the Web Search MCP server

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Ensure we're in the project root
cd "$(get_project_root)"

# Configure parameters
PORT=8080
DEBUG=false
CONTAINER_NAME="web-search-mcp"
CONTAINER_IMAGE="agent-provocateur/web-search-mcp"
LOG_DIR="$(get_project_root)/logs"
STDOUT_LOG="$LOG_DIR/web_search_mcp.out.log"
STDERR_LOG="$LOG_DIR/web_search_mcp.err.log"
DEBUG_LOG="$LOG_DIR/web_search_mcp_debug.log"
ACTION="status"  # Default action

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    start|stop|status|restart)
      ACTION="$1"
      shift
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --debug|-d)
      DEBUG=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [start|stop|status|restart] [--port PORT] [--debug]"
      echo ""
      echo "Commands:"
      echo "  start      Start the Web Search MCP server"
      echo "  stop       Stop the Web Search MCP server"
      echo "  status     Check the status of the Web Search MCP server"
      echo "  restart    Restart the Web Search MCP server"
      echo ""
      echo "Options:"
      echo "  --port PORT    Port to run the Web Search MCP server on (default: 8080)"
      echo "  --debug, -d    Enable debug mode with detailed logging"
      echo "  --help, -h     Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to write to debug log
log_debug() {
  local message="$1"
  echo "$(date): $message" | tee -a "$DEBUG_LOG"
}

# Function to detect container engine
detect_container_engine() {
  if command -v podman &> /dev/null; then
    echo "podman"
  elif command -v docker &> /dev/null; then
    echo "docker"
  else
    echo ""
  fi
}

# Function to check if container is running
is_container_running() {
  local container_name="$1"
  local container_cmd="$2"
  
  if [ -z "$container_cmd" ]; then
    return 1
  fi
  
  $container_cmd ps --format '{{.Names}}' 2>/dev/null | grep -q "^$container_name$"
  return $?
}

# Function to check if a port is in use
check_port() {
  local port=$1
  nc -z localhost "$port" 2> /dev/null
  return $?
}

# Function to get container status
get_container_status() {
  local container_name="$1"
  local container_cmd="$2"
  
  if [ -z "$container_cmd" ]; then
    echo "No container engine detected"
    return 1
  fi
  
  if is_container_running "$container_name" "$container_cmd"; then
    echo "Running"
    return 0
  else
    echo "Stopped"
    return 1
  fi
}

# Function to start the Web Search MCP server
start_web_search_mcp() {
  # Get the container engine
  CONTAINER_CMD=$(detect_container_engine)
  
  if [ -z "$CONTAINER_CMD" ]; then
    log_debug "Error: Neither podman nor docker is available. Please install one of them."
    echo "Error: Neither podman nor docker is available. Please install one of them."
    exit 1
  fi
  
  log_debug "Using container command: $CONTAINER_CMD"
  
  # Check if the container is already running
  if is_container_running "$CONTAINER_NAME" "$CONTAINER_CMD"; then
    log_debug "Web Search MCP is already running"
    echo "Web Search MCP is already running"
    return 0
  fi
  
  # Check if port is in use
  if check_port "$PORT"; then
    log_debug "Error: Port $PORT is already in use by another process"
    echo "Error: Port $PORT is already in use by another process"
    
    # Get process info using lsof if available
    if command -v lsof &> /dev/null; then
      log_debug "Process using port $PORT:"
      lsof -i :"$PORT" | tee -a "$DEBUG_LOG"
    fi
    
    return 1
  fi
  
  # Check if the container image exists
  log_debug "Checking if container image exists: $CONTAINER_IMAGE"
  if [ "$CONTAINER_CMD" = "podman" ]; then
    IMAGE_EXISTS=$(podman image exists "$CONTAINER_IMAGE:latest" 2>/dev/null && echo "true" || echo "false")
  else
    # For Docker, we need to use a different approach
    IMAGE_EXISTS=$(docker image inspect "$CONTAINER_IMAGE:latest" >/dev/null 2>&1 && echo "true" || echo "false")
  fi
  
  # Build the image if it doesn't exist
  if [ "$IMAGE_EXISTS" != "true" ]; then
    log_debug "Container image not found. Building it now..."
    echo "Container image not found. Building it now..."
    
    cd "$(get_project_root)/web_search_mcp"
    if [ -f "./scripts/build.sh" ]; then
      ./scripts/build.sh
    else
      log_debug "Error: build.sh script not found"
      echo "Error: Could not find build script at ./web_search_mcp/scripts/build.sh"
      return 1
    fi
  fi
  
  # Run the container with environment variables from .env
  log_debug "Starting web-search-mcp container on port $PORT..."
  echo "Starting web-search-mcp container on port $PORT..."
  
  cd "$(get_project_root)/web_search_mcp"
  
  # Check if .env file exists
  if [ ! -f "./.env" ]; then
    log_debug "Warning: .env file not found. You may need to create one with API keys."
    echo "Warning: .env file not found. You may need to create one with API keys."
  fi
  
  $CONTAINER_CMD run -d --rm -p "$PORT:8080" --name "$CONTAINER_NAME" --env-file=.env "$CONTAINER_IMAGE:latest" > "$STDOUT_LOG" 2> "$STDERR_LOG"
  
  # Check if the container started successfully
  if is_container_running "$CONTAINER_NAME" "$CONTAINER_CMD"; then
    log_debug "Web Search MCP server started successfully on port $PORT"
    echo "Web Search MCP server started successfully on port $PORT"
    echo "Set WEB_SEARCH_MCP_URL=http://localhost:$PORT when running the WebSearchAgent"
    
    # Save the port to a file for easy reference
    mkdir -p "$(get_project_root)/.pid"
    echo "$PORT" > "$(get_project_root)/.pid/web_search_mcp.port"
    
    # Wait a moment to make sure the server is ready
    sleep 2
    
    # Try a simple health check
    if command -v curl &> /dev/null; then
      log_debug "Testing Web Search MCP server health..."
      if curl -s "http://localhost:$PORT/health" | grep -q "ok"; then
        log_debug "Health check successful"
        echo "Health check successful - Web Search MCP is operational"
      else
        log_debug "Warning: Health check did not return expected response"
        echo "Warning: Health check did not return expected response"
      fi
    fi
    
    return 0
  else
    log_debug "Error: Failed to start Web Search MCP server"
    echo "Error: Failed to start Web Search MCP server"
    echo "Check logs for more information:"
    echo "- $STDOUT_LOG"
    echo "- $STDERR_LOG"
    return 1
  fi
}

# Function to stop the Web Search MCP server
stop_web_search_mcp() {
  # Get the container engine
  CONTAINER_CMD=$(detect_container_engine)
  
  if [ -z "$CONTAINER_CMD" ]; then
    log_debug "Error: Neither podman nor docker is available. Please install one of them."
    echo "Error: Neither podman nor docker is available. Please install one of them."
    exit 1
  fi
  
  log_debug "Using container command: $CONTAINER_CMD"
  
  # Check if the container is running
  if ! is_container_running "$CONTAINER_NAME" "$CONTAINER_CMD"; then
    log_debug "Web Search MCP is not running"
    echo "Web Search MCP is not running"
    return 0
  fi
  
  # Stop the container
  log_debug "Stopping Web Search MCP container..."
  echo "Stopping Web Search MCP container..."
  
  $CONTAINER_CMD stop "$CONTAINER_NAME" > "$STDOUT_LOG" 2> "$STDERR_LOG"
  
  # Check if the container was stopped successfully
  if ! is_container_running "$CONTAINER_NAME" "$CONTAINER_CMD"; then
    log_debug "Web Search MCP server stopped successfully"
    echo "Web Search MCP server stopped successfully"
    
    # Remove the port file
    rm -f "$(get_project_root)/.pid/web_search_mcp.port"
    
    return 0
  else
    log_debug "Error: Failed to stop Web Search MCP server"
    echo "Error: Failed to stop Web Search MCP server"
    echo "Try using --force to force stop the container"
    return 1
  fi
}

# Function to check the status of the Web Search MCP server
status_web_search_mcp() {
  # Get the container engine
  CONTAINER_CMD=$(detect_container_engine)
  
  if [ -z "$CONTAINER_CMD" ]; then
    log_debug "Error: Neither podman nor docker is available. Please install one of them."
    echo "Error: Neither podman nor docker is available. Please install one of them."
    exit 1
  fi
  
  # Get the status
  STATUS=$(get_container_status "$CONTAINER_NAME" "$CONTAINER_CMD")
  
  echo "Web Search MCP Status: $STATUS"
  
  # If running, get more information
  if [ "$STATUS" = "Running" ]; then
    # Get container information
    if [ "$CONTAINER_CMD" = "podman" ]; then
      CONTAINER_INFO=$($CONTAINER_CMD inspect "$CONTAINER_NAME" --format '{{.State.StartedAt}}')
    else
      CONTAINER_INFO=$($CONTAINER_CMD inspect "$CONTAINER_NAME" --format '{{.State.StartedAt}}')
    fi
    
    echo "Started at: $CONTAINER_INFO"
    
    # Check if port is accessible
    if check_port "$PORT"; then
      echo "Port $PORT is open and in use by Web Search MCP"
    else
      echo "Warning: Port $PORT is not accessible even though container is running"
    fi
    
    # Try a health check
    if command -v curl &> /dev/null; then
      if curl -s "http://localhost:$PORT/health" | grep -q "ok"; then
        echo "Health check: Operational"
      else
        echo "Health check: Failed - Service may be starting up or unhealthy"
      fi
    fi
  fi
  
  return 0
}

# Execute the requested action
case "$ACTION" in
  start)
    start_web_search_mcp
    ;;
  stop)
    stop_web_search_mcp
    ;;
  status)
    status_web_search_mcp
    ;;
  restart)
    stop_web_search_mcp
    start_web_search_mcp
    ;;
  *)
    echo "Unknown action: $ACTION"
    echo "Use --help for usage information"
    exit 1
    ;;
esac