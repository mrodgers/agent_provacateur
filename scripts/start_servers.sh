#!/bin/bash

# Script to start the MCP server with proper environment setup using uv

# Ensure we're in the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Running setup script first..."
    bash scripts/setup_env.sh
    if [ $? -ne 0 ]; then
        echo "Environment setup failed. Please check errors and try again."
        exit 1
    fi
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source .venv/Scripts/activate
else
    # Unix/MacOS
    source .venv/bin/activate
fi

# Default values
HOST="127.0.0.1"
PORT="8000"

# Check for arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --host=*)
      HOST="${1#*=}"
      shift
      ;;
    --port=*)
      PORT="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown parameter: $1"
      echo "Usage: $0 [--host=127.0.0.1] [--port=8000]"
      exit 1
      ;;
  esac
done

echo "Starting MCP server on $HOST:$PORT..."
ap-server --host "$HOST" --port "$PORT"