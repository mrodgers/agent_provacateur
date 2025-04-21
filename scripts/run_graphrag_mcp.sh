#!/bin/bash
# Run script for GraphRAG MCP server with Agent Provocateur integration

# Set base directory
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
GRAPHRAG_DIR="$BASE_DIR/graphrag_mcp"
LOGS_DIR="$BASE_DIR/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"
mkdir -p "$GRAPHRAG_DIR/logs"

# Output banner
echo "====================================================================="
echo "    GraphRAG MCP Server - Source Attribution Microservice"
echo "====================================================================="

# Check for GraphRAG MCP server
if [ ! -d "$GRAPHRAG_DIR" ]; then
  echo "Error: GraphRAG MCP directory not found at $GRAPHRAG_DIR"
  exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
  echo "Error: Node.js is not installed. Please install Node.js to run the GraphRAG MCP server."
  exit 1
fi

# Configure environment variables
export GRAPHRAG_MCP_URL=${GRAPHRAG_MCP_URL:-"http://localhost:8083"}
export PORT=${PORT:-8083}

# Parse arguments
RUN_AP=false
REBUILD=false
FORCE_RESTART=false

for arg in "$@"; do
  case $arg in
    --with-ap)
      RUN_AP=true
      shift
      ;;
    --rebuild)
      REBUILD=true
      shift
      ;;
    --restart)
      FORCE_RESTART=true
      shift
      ;;
    *)
      # Unknown option
      ;;
  esac
done

# Check if server is already running
GRAPHRAG_PID=""
if [ -f "$GRAPHRAG_DIR/.pid" ]; then
  GRAPHRAG_PID=$(cat "$GRAPHRAG_DIR/.pid")
  if ps -p $GRAPHRAG_PID > /dev/null; then
    if [ "$FORCE_RESTART" = true ]; then
      echo "Stopping existing GraphRAG MCP server (PID: $GRAPHRAG_PID)..."
      kill $GRAPHRAG_PID
      sleep 2
      GRAPHRAG_PID=""
    else
      echo "GraphRAG MCP server is already running with PID $GRAPHRAG_PID"
      echo "Using existing server at $GRAPHRAG_MCP_URL"
    fi
  else
    echo "GraphRAG MCP server PID file exists but server is not running. Starting new server..."
    GRAPHRAG_PID=""
  fi
fi

# Start GraphRAG MCP server if not already running
if [ -z "$GRAPHRAG_PID" ]; then
  cd "$GRAPHRAG_DIR"
  
  # Install dependencies if needed
  if [ ! -d "node_modules" ] || [ "$REBUILD" = true ]; then
    echo "Installing GraphRAG MCP dependencies..."
    npm install
  fi
  
  # Build TypeScript if needed
  if [ ! -d "dist" ] || [ ! -f "dist/index.js" ] || [ "$REBUILD" = true ]; then
    echo "Building GraphRAG MCP TypeScript..."
    npm run build
  fi
  
  # Start server
  echo "Starting GraphRAG MCP server on port $PORT..."
  node dist/index.js > "$LOGS_DIR/graphrag_mcp.log" 2> "$LOGS_DIR/graphrag_mcp.err.log" &
  GRAPHRAG_PID=$!
  
  # Save PID to file
  echo $GRAPHRAG_PID > .pid
  
  echo "GraphRAG MCP server started with PID $GRAPHRAG_PID"
  echo "Logs available at: $LOGS_DIR/graphrag_mcp.log"
  
  # Wait for server to start
  echo "Waiting for server to start..."
  
  # Try up to 10 times with 1 second between attempts
  for i in {1..10}; do
    sleep 1
    curl -s "$GRAPHRAG_MCP_URL/api/info" > /dev/null
    if [ $? -eq 0 ]; then
      break
    fi
    echo "Waiting for server to become available... ($i/10)"
  done
fi

# Test GraphRAG MCP server
echo "Testing GraphRAG MCP server..."
curl -s "$GRAPHRAG_MCP_URL/api/info" > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ GraphRAG MCP server is running and responding at $GRAPHRAG_MCP_URL"
  
  # Show available tools
  echo ""
  echo "Available GraphRAG tools:"
  TOOLS=$(curl -s "$GRAPHRAG_MCP_URL/api/info" | grep -o '"tools":\[[^]]*\]' | sed 's/"tools":\[//g' | sed 's/\]//g' | sed 's/"//g' | sed 's/,/\n  - /g')
  echo "  - $TOOLS"
  echo ""
else
  echo "❌ GraphRAG MCP server is not responding. Check logs at $LOGS_DIR/graphrag_mcp.err.log"
  exit 1
fi

# Show usage instructions
echo "Usage:"
echo "  Python: from agent_provocateur.graphrag_client import GraphRAGClient"
echo "  Environment: export GRAPHRAG_MCP_URL=$GRAPHRAG_MCP_URL"
echo ""

# Start Agent Provocateur with GraphRAG integration if requested
if [ "$RUN_AP" = true ]; then
  echo "Starting Agent Provocateur with GraphRAG integration..."
  # Run the main Agent Provocateur start script if present
  if [ -f "$BASE_DIR/scripts/start_ap.sh" ]; then
    echo "Running Agent Provocateur start script..."
    GRAPHRAG_MCP_URL=$GRAPHRAG_MCP_URL AGENT_TYPE=xml_graphrag "$BASE_DIR/scripts/start_ap.sh"
  else
    echo "Agent Provocateur start script not found. You can start Agent Provocateur manually with:"
    echo "GRAPHRAG_MCP_URL=$GRAPHRAG_MCP_URL AGENT_TYPE=xml_graphrag python -m agent_provocateur.main"
  fi
else
  echo "To start Agent Provocateur with GraphRAG integration, run:"
  echo "  GRAPHRAG_MCP_URL=$GRAPHRAG_MCP_URL AGENT_TYPE=xml_graphrag python -m agent_provocateur.main"
  echo ""
  echo "Or run this script with --with-ap flag:"
  echo "  ./scripts/run_graphrag_mcp.sh --with-ap"
fi

# Show how to stop the server
echo ""
echo "GraphRAG MCP server is running with PID $GRAPHRAG_PID"
echo "To stop the server, run: kill $GRAPHRAG_PID or use $GRAPHRAG_DIR/scripts/stop.sh"
echo "====================================================================="