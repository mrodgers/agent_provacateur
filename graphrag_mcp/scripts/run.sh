#!/bin/bash
# Run script for GraphRAG MCP server

# Ensure we're in the graphrag_mcp directory
cd "$(dirname "$0")/.."

# Create logs directory if it doesn't exist
mkdir -p logs

# Check for installed dependencies
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

# Check for TypeScript build
if [ ! -d "dist" ] || [ ! -f "dist/index.js" ]; then
  echo "Building TypeScript..."
  npm run build
fi

# Set default port if not specified
export PORT=${PORT:-8083}

# Start the server
echo "Starting GraphRAG MCP server on port $PORT..."
node dist/index.js > logs/server.log 2>&1 &
SERVER_PID=$!

# Save PID to file
echo $SERVER_PID > .pid

echo "GraphRAG MCP server started with PID $SERVER_PID"
echo "Logs available at: $(pwd)/logs/server.log"