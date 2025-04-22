#!/bin/bash
# Run the GraphRAG MCP Server (Python implementation)

# Change to the project root directory
cd "$(dirname "$0")/.."

# Create required directories
mkdir -p logs
mkdir -p data/vectors

# Check if already running
if [ -f ".pid" ]; then
    pid=$(cat .pid)
    if ps -p $pid > /dev/null; then
        echo "GraphRAG MCP Server is already running with PID $pid"
        echo "To stop the server, run: ./scripts/stop.sh"
        exit 0
    else
        echo "Stale PID file found. Removing."
        rm .pid
    fi
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Check for uvicorn
if ! python3 -c "import uvicorn" &> /dev/null; then
    echo "Installing uvicorn..."
    pip install uvicorn fastapi
fi

# Check for sentence-transformers
if ! python3 -c "import sentence_transformers" &> /dev/null; then
    echo "Installing sentence-transformers..."
    pip install sentence-transformers
fi

# Check for FAISS
if ! python3 -c "import faiss" &> /dev/null; then
    echo "Installing FAISS CPU version..."
    pip install faiss-cpu
fi

# Set up environment variables
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8083}
export VECTOR_DB_TYPE=${VECTOR_DB_TYPE:-faiss}
export VECTOR_DB_PATH=${VECTOR_DB_PATH:-./data/vectors/faiss}
export LOG_LEVEL=${LOG_LEVEL:-info}

echo "Starting GraphRAG MCP Server (Python) on $HOST:$PORT..."

# Run the server in the background
python3 -m graphrag_mcp_py.src > ./logs/graphrag_mcp.out.log 2> ./logs/graphrag_mcp.err.log &

# Save the PID
echo $! > .pid

echo "GraphRAG MCP Server started with PID $(cat .pid)"
echo "Logs available at: ./logs/graphrag_mcp.out.log"

# Check if server is responding
echo "Waiting for server to become available..."
for i in {1..10}; do
    sleep 1
    if curl -s "http://localhost:$PORT/api/info" > /dev/null; then
        echo "✅ Server is now available at http://localhost:$PORT"
        curl -s "http://localhost:$PORT/api/info" | python3 -m json.tool
        echo ""
        break
    fi
    echo "Waiting... ($i/10)"
    if [ $i -eq 10 ]; then
        echo "⚠️  Server didn't respond in time, but may still be starting up."
        echo "Check logs at ./logs/graphrag_mcp.err.log for errors."
    fi
done

# Show usage instructions
echo ""
echo "Usage in Agent Provocateur:"
echo "  export GRAPHRAG_MCP_URL=http://localhost:$PORT"
echo "  export AGENT_TYPE=xml_graphrag"
echo ""
echo "To stop the server, run: ./scripts/stop.sh"