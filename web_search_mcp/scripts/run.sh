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

# Check for API keys
if ! check_api_keys; then
  echo "Warning: No API keys found in .env file. The server will start but may not work properly."
  echo "Press Ctrl+C to cancel, or Enter to continue anyway..."
  read -r
fi

# Determine container engine
CONTAINER_ENGINE=$(get_container_engine)

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

# Run the container with environment variables from .env
print_header "Starting web-search-mcp container..."
$CONTAINER_ENGINE run --rm -i --env-file=.env agent-provocateur/web-search-mcp:latest

# Note: This script is meant for interactive use with stdio. For integration with
# Agent Provocateur, use the appropriate configuration in your agent setup.