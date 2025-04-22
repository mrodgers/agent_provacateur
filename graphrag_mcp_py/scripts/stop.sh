#!/bin/bash
# Stop the GraphRAG MCP Server (Python implementation)

# Change to the project root directory
cd "$(dirname "$0")/.."

# Check if PID file exists
if [ ! -f ".pid" ]; then
    echo "No GraphRAG MCP Server PID file found. Server may not be running."
    exit 0
fi

# Get the PID
pid=$(cat .pid)

# Check if process is still running
if ! ps -p $pid > /dev/null; then
    echo "No GraphRAG MCP Server process found with PID $pid."
    rm .pid
    exit 0
fi

# Stop the process
echo "Stopping GraphRAG MCP Server with PID $pid..."
kill $pid

# Wait for the process to terminate
for i in {1..5}; do
    if ! ps -p $pid > /dev/null; then
        echo "GraphRAG MCP Server stopped successfully."
        rm .pid
        exit 0
    fi
    echo "Waiting for server to stop... ($i/5)"
    sleep 1
done

# Force kill if still running
if ps -p $pid > /dev/null; then
    echo "Server didn't stop gracefully, forcing termination..."
    kill -9 $pid
    if ! ps -p $pid > /dev/null; then
        echo "GraphRAG MCP Server terminated."
        rm .pid
        exit 0
    else
        echo "Failed to terminate server process. Please check manually."
        exit 1
    fi
fi