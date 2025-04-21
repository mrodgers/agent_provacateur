#!/bin/bash
set -e

# Change to the project directory
cd "$(dirname "$0")/.."

# Source the utilities
source ./scripts/utils.sh

# Check requirements
print_header "Checking requirements..."
if ! check_requirements; then
  exit 1
fi

# Ensure .env file exists
print_header "Checking configuration..."
if ! ensure_env_file; then
  exit 1
fi

# Determine container engine
CONTAINER_ENGINE=$(get_container_engine)

# Check for API keys
echo "Checking API keys..."
check_api_keys

# Check if the container image exists
if [ "$CONTAINER_ENGINE" = "podman" ]; then
  IMAGE_EXISTS=$($CONTAINER_ENGINE image exists agent-provocateur/web-search-mcp:latest 2>/dev/null)
else
  # For Docker, we need to use a different approach
  IMAGE_EXISTS=$(docker image inspect agent-provocateur/web-search-mcp:latest >/dev/null 2>&1 && echo "true" || echo "false")
fi

if [ "$IMAGE_EXISTS" != "true" ]; then
  print_header "Container image not found. Building it now..."
  ./scripts/build.sh
fi

# Start the container
print_header "Starting Web Search MCP server..."
echo "The server is now running. Press Ctrl+C to stop."
echo ""
$CONTAINER_ENGINE run --rm -i --env-file=.env agent-provocateur/web-search-mcp:latest