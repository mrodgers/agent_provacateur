#\!/bin/bash

# Script to stop the GraphRAG MCP Python server

# Get the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Check if running
PID_FILE="$PROJECT_ROOT/.pid/graphrag_mcp_py.pid"

if [ \! -f "$PID_FILE" ]; then
    echo "GraphRAG MCP Python server is not running (no PID file)"
    exit 0
fi

PID=$(cat "$PID_FILE")
if \! ps -p "$PID" > /dev/null; then
    echo "Removing stale PID file"
    rm "$PID_FILE"
    exit 0
fi

echo "Stopping GraphRAG MCP Python server with PID $PID..."
kill "$PID"

# Wait for process to terminate
for i in {1..10}; do
    if \! ps -p "$PID" > /dev/null; then
        break
    fi
    echo "Waiting for process to terminate..."
    sleep 1
done

# Force kill if still running
if ps -p "$PID" > /dev/null; then
    echo "Force killing process..."
    kill -9 "$PID"
fi

rm "$PID_FILE"
echo "GraphRAG MCP Python server stopped"
