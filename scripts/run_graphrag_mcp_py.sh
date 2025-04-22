#\!/bin/bash

# Script to run the GraphRAG MCP Python server

# Get the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Configuration
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8083}
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

# Check if already running
PID_FILE="$PROJECT_ROOT/.pid/graphrag_mcp_py.pid"
mkdir -p "$PROJECT_ROOT/.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null; then
        echo "GraphRAG MCP Python server is already running with PID $PID"
        exit 0
    else
        echo "Removing stale PID file"
        rm "$PID_FILE"
    fi
fi

echo "Starting GraphRAG MCP Python server on $HOST:$PORT..."
cd "$PROJECT_ROOT/graphrag_mcp_py" && \
    python -m src > "$LOG_DIR/graphrag_mcp_py.out.log" 2> "$LOG_DIR/graphrag_mcp_py.err.log" &

PID=$\!
echo $PID > "$PID_FILE"
echo "GraphRAG MCP Python server started with PID $PID"
echo "Logs are available at:"
echo "  $LOG_DIR/graphrag_mcp_py.out.log"
echo "  $LOG_DIR/graphrag_mcp_py.err.log"
