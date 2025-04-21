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

# Determine container engine
CONTAINER_ENGINE=$(get_container_engine)

# Build the image
print_header "Building web-search-mcp image..."
$CONTAINER_ENGINE build -t agent-provocateur/web-search-mcp:latest .

print_header "Build completed successfully!"
echo "To run the container, use one of the following commands:"
echo ""
echo "With environment variables from file:"
echo "$CONTAINER_ENGINE run --rm -i --env-file=.env agent-provocateur/web-search-mcp:latest"
echo ""
echo "With explicit environment variables:"
echo "$CONTAINER_ENGINE run --rm -i -e BRAVE_API_KEY=your_key agent-provocateur/web-search-mcp:latest"
echo ""
echo "Or simply use the scripts/start.sh script to run the server."
echo ""