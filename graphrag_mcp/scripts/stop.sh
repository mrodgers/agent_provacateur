#!/bin/bash
# Stop script for GraphRAG MCP server

# Ensure we're in the graphrag_mcp directory
cd "$(dirname "$0")/.."

# Check if PID file exists
if [ -f ".pid" ]; then
  PID=$(cat .pid)
  
  # Check if process is running
  if ps -p $PID > /dev/null; then
    echo "Stopping GraphRAG MCP server (PID: $PID)..."
    kill $PID
    
    # Wait for process to terminate
    sleep 2
    
    # Check if process is still running and force kill if necessary
    if ps -p $PID > /dev/null; then
      echo "Server still running, forcing termination..."
      kill -9 $PID
    fi
    
    echo "GraphRAG MCP server stopped"
  else
    echo "GraphRAG MCP server not running (PID: $PID)"
  fi
  
  # Remove PID file
  rm .pid
else
  echo "No PID file found. GraphRAG MCP server may not be running"
  
  # Try to find and kill the process by name
  pkill -f "node dist/index.js"
fi