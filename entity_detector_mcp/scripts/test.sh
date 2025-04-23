#!/bin/bash
set -e

echo "Testing the Entity Detector MCP server..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Check for and create TypeScript type definitions if needed
if [ ! -d "node_modules/@types/supertest" ]; then
  echo "Installing required TypeScript type definitions..."
  npm install --save-dev @types/supertest
fi

# Run tests with coverage
echo "Running tests with coverage..."
npm test -- --coverage

echo "Tests completed successfully."

# Display coverage summary if report exists
if [ -f "./coverage/lcov-report/index.html" ]; then
  echo "Coverage summary:"
  cat ./coverage/lcov-report/index.html | grep -A 20 "coverage-summary" | head -n 15
  
  # Store location of coverage report
  echo ""
  echo "Detailed coverage report available at:"
  echo "file://$(pwd)/coverage/lcov-report/index.html"
else
  echo "No coverage report generated."
fi