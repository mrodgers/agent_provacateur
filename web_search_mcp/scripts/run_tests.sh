#!/bin/bash
set -e

# Change to the project directory
cd "$(dirname "$0")/.."

# Source the utilities
source ./scripts/utils.sh

# Print information about what we're going to do
print_header "Running Web Search MCP tests"
echo "This script will run all tests for the Web Search MCP server including:"
echo " - TypeScript unit tests (providers, utilities)"
echo " - Integration tests (if configured)"
echo ""

# Check requirements
echo "Checking requirements..."
if ! check_requirements; then
  exit 1
fi

# Check if we have node_modules installed
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm ci
fi

# Run TypeScript tests
print_header "Running TypeScript unit tests"
npm test

# Check if we can run integration tests
print_header "Integration test availability"

if ! ensure_env_file; then
  print_header "All tests completed!"
  exit 0
fi

# Check API key availability and display integration test commands
echo "Found .env file - checking for API keys for integration tests"
source .env

if [ ! -z "$BRAVE_API_KEY" ]; then
  echo ""
  echo "✓ Brave API key found. To run integration test with Brave Search, use:"
  echo "python scripts/test_integration.py --query \"your search query\" --provider brave"
  echo ""
fi

if [ ! -z "$GOOGLE_API_KEY" ] && [ ! -z "$GOOGLE_SEARCH_CX" ]; then
  echo ""
  echo "✓ Google API keys found. To run integration test with Google Search, use:"
  echo "python scripts/test_integration.py --query \"your search query\" --provider google"
  echo ""
fi

if [ ! -z "$BING_API_KEY" ]; then
  echo ""
  echo "✓ Bing API key found. To run integration test with Bing Search, use:"
  echo "python scripts/test_integration.py --query \"your search query\" --provider bing"
  echo ""
fi

print_header "All tests completed!"