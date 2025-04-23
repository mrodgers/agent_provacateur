#!/bin/bash
set -e

echo "Starting Entity Detector MCP server..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if .env file exists
if [ ! -f ".env" ]; then
  echo "No .env file found, creating default configuration..."
  cat > .env << EOF
PORT=8082
HOST=0.0.0.0
ENABLE_CACHE=true
CACHE_TTL_SECONDS=3600
ALLOWED_ORIGINS=*
LOG_LEVEL=info
DEFAULT_MODEL=nlp
NLP_LANGUAGE=en
EOF
  echo ".env file created with default configuration."
fi

# Build if dist directory doesn't exist
if [ ! -d "dist" ]; then
  echo "Building project first..."
  npm install
  npm run build
fi

# Run the server
echo "Starting server..."
node dist/index.js