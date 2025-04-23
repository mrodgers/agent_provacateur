#!/bin/bash
set -e

echo "Building Entity Detector MCP server..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Install dependencies
npm install

# Build TypeScript
npm run build

echo "Build completed successfully."