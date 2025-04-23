#!/bin/bash
# Start the Agent Provocateur frontend server with robust port handling and debugging
# This script handles port detection, automatic port switching, and provides detailed debug info

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Ensure we're in the project root
cd "$(get_project_root)"

# Configure server parameters
HOST="127.0.0.1"
DEFAULT_PORT=3001  # Default to 3001 to avoid conflicts with Grafana
BACKEND_URL="http://localhost:8000"
DEBUG=false
CLEAN=false
PORT=$DEFAULT_PORT

# Create frontend debug file
LOG_DIR="$(get_project_root)/logs"
mkdir -p "$LOG_DIR"
FRONTEND_DEBUG_LOG="$LOG_DIR/frontend_debug.log"
STDOUT_LOG="$LOG_DIR/frontend.out.log"
STDERR_LOG="$LOG_DIR/frontend.err.log"

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --port|-p)
      PORT="$2"
      shift 2
      ;;
    --host|-h)
      HOST="$2"
      shift 2
      ;;
    --backend-url|-b)
      BACKEND_URL="$2"
      shift 2
      ;;
    --debug|-d)
      DEBUG=true
      shift
      ;;
    --clean|-c)
      CLEAN=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--port|-p PORT] [--host|-h HOST] [--backend-url|-b URL] [--debug|-d] [--clean|-c]"
      exit 1
      ;;
  esac
done

# Log the startup
echo "$(date): Starting frontend server" | tee -a "$FRONTEND_DEBUG_LOG"
echo "Parameters:" | tee -a "$FRONTEND_DEBUG_LOG"
echo "- Host: $HOST" | tee -a "$FRONTEND_DEBUG_LOG"
echo "- Port: $PORT" | tee -a "$FRONTEND_DEBUG_LOG"
echo "- Backend URL: $BACKEND_URL" | tee -a "$FRONTEND_DEBUG_LOG"
echo "- Debug: $DEBUG" | tee -a "$FRONTEND_DEBUG_LOG"
echo "- Clean: $CLEAN" | tee -a "$FRONTEND_DEBUG_LOG"

# Clean existing logs if requested
if [ "$CLEAN" = true ]; then
  echo "Cleaning existing logs..." | tee -a "$FRONTEND_DEBUG_LOG"
  > "$STDOUT_LOG"
  > "$STDERR_LOG"
fi

# Function to check if a port is in use
check_port() {
  local port=$1
  nc -z "$HOST" "$port" 2> /dev/null
  return $?
}

# Function to find an available port starting from the given port
find_available_port() {
  local start_port=$1
  local current_port=$start_port
  local max_port=$((start_port + 20))  # Try up to 20 ports
  
  while [ $current_port -le $max_port ]; do
    echo "Checking port $current_port..." | tee -a "$FRONTEND_DEBUG_LOG"
    if ! check_port "$current_port"; then
      echo "Port $current_port is available" | tee -a "$FRONTEND_DEBUG_LOG"
      return $current_port
    else
      # Try to get more info about what's using the port
      echo "Port $current_port is in use" | tee -a "$FRONTEND_DEBUG_LOG"
      
      # On macOS/Linux, use lsof to find what's using the port
      if command -v lsof &> /dev/null; then
        echo "Process using port $current_port:" | tee -a "$FRONTEND_DEBUG_LOG"
        lsof -i :"$current_port" | tee -a "$FRONTEND_DEBUG_LOG"
      fi
      
      current_port=$((current_port + 1))
    fi
  done
  
  # If we get here, no ports are available
  echo "No available ports found in range $start_port-$max_port" | tee -a "$FRONTEND_DEBUG_LOG"
  return 1
}

# Function to stop any existing frontend server processes
stop_frontend_server() {
  echo "Checking for existing frontend server processes..." | tee -a "$FRONTEND_DEBUG_LOG"
  
  # First try using cleanup_all.sh if it exists
  if [ -f "$SCRIPT_DIR/cleanup_all.sh" ]; then
    echo "Using comprehensive cleanup script..." | tee -a "$FRONTEND_DEBUG_LOG"
    
    # Run the cleanup script with filtered output to avoid overwhelming logs
    "$SCRIPT_DIR/cleanup_all.sh" --no-clean-pid 2>&1 | grep -i "frontend\|server.py\|port $PORT" | tee -a "$FRONTEND_DEBUG_LOG"
    
    # Let the cleanup script handle everything
    sleep 1
  else
    # Otherwise use the original cleanup code
    # Find processes by the pattern 'server.py --port' and kill them
    local pids=$(ps aux | grep "[s]erver.py.*--port" | awk '{print $2}')
    if [ -n "$pids" ]; then
      echo "Found existing frontend server processes. Stopping them..." | tee -a "$FRONTEND_DEBUG_LOG"
      for pid in $pids; do
        echo "Stopping process $pid" | tee -a "$FRONTEND_DEBUG_LOG"
        kill "$pid" 2> /dev/null
        
        # Wait for process to terminate
        local wait_count=0
        while kill -0 "$pid" 2> /dev/null && [ $wait_count -lt 10 ]; do
          sleep 0.5
          wait_count=$((wait_count + 1))
        done
        
        # Force kill if still running
        if kill -0 "$pid" 2> /dev/null; then
          echo "Process $pid did not terminate gracefully. Force killing..." | tee -a "$FRONTEND_DEBUG_LOG"
          kill -9 "$pid" 2> /dev/null
        fi
      done
    else
      echo "No existing frontend server processes found" | tee -a "$FRONTEND_DEBUG_LOG"
    fi
  fi
  
  # Double-check port availability regardless of which cleanup method was used
  if check_port "$PORT"; then
    echo "Warning: Port $PORT is still in use by another process" | tee -a "$FRONTEND_DEBUG_LOG"
    
    # On macOS/Linux, use lsof to find what's using the port
    if command -v lsof &> /dev/null; then
      echo "Process using port $PORT:" | tee -a "$FRONTEND_DEBUG_LOG"
      lsof -i :"$PORT" | tee -a "$FRONTEND_DEBUG_LOG"
      
      # Try to get PID and force kill it
      local port_pids=$(lsof -i :"$PORT" | grep LISTEN | awk '{print $2}' | uniq)
      if [ -n "$port_pids" ]; then
        echo "Attempting to force kill processes on port $PORT..." | tee -a "$FRONTEND_DEBUG_LOG"
        for pid in $port_pids; do
          echo "Force killing PID $pid on port $PORT..." | tee -a "$FRONTEND_DEBUG_LOG"
          kill -9 "$pid" 2>/dev/null
        done
        sleep 1
      fi
    fi
    
    # Check again after attempted force kill
    if check_port "$PORT"; then
      # Find alternative port as a last resort
      local new_port
      find_available_port "$((PORT + 1))"
      new_port=$?
      
      if [ $new_port -ne 1 ]; then
        echo "Switching to available port $new_port" | tee -a "$FRONTEND_DEBUG_LOG"
        PORT=$new_port
      else
        echo "Error: No available ports found. Cannot start frontend server." | tee -a "$FRONTEND_DEBUG_LOG"
        echo "Try running './scripts/cleanup_all.sh' to free up all ports." | tee -a "$FRONTEND_DEBUG_LOG"
        exit 1
      fi
    fi
  fi
}

# Debug the environment
if [ "$DEBUG" = true ]; then
  echo "Debug information:" | tee -a "$FRONTEND_DEBUG_LOG"
  
  # System info
  echo "System:" | tee -a "$FRONTEND_DEBUG_LOG"
  uname -a | tee -a "$FRONTEND_DEBUG_LOG"
  
  # Python info
  echo "Python:" | tee -a "$FRONTEND_DEBUG_LOG"
  python --version | tee -a "$FRONTEND_DEBUG_LOG"
  
  # Current directory
  echo "Current directory:" | tee -a "$FRONTEND_DEBUG_LOG"
  pwd | tee -a "$FRONTEND_DEBUG_LOG"
  
  # Check frontend directory
  echo "Frontend directory:" | tee -a "$FRONTEND_DEBUG_LOG"
  ls -la "$(get_project_root)/frontend" | tee -a "$FRONTEND_DEBUG_LOG"
  
  # Check for server.py
  echo "Server.py exists:" | tee -a "$FRONTEND_DEBUG_LOG"
  test -f "$(get_project_root)/frontend/server.py" && echo "Yes" || echo "No" | tee -a "$FRONTEND_DEBUG_LOG"
  
  # Check for ports in use
  echo "Ports in use:" | tee -a "$FRONTEND_DEBUG_LOG"
  
  # Check common ports
  for port in 3000 3001 8000 9090 9091; do
    echo -n "Port $port: " | tee -a "$FRONTEND_DEBUG_LOG"
    if check_port "$port"; then
      echo "IN USE" | tee -a "$FRONTEND_DEBUG_LOG"
      
      # Get process info
      if command -v lsof &> /dev/null; then
        lsof -i :"$port" | tee -a "$FRONTEND_DEBUG_LOG"
      fi
    else
      echo "Available" | tee -a "$FRONTEND_DEBUG_LOG"
    fi
  done
  
  # Check backend availability
  echo "Backend availability:" | tee -a "$FRONTEND_DEBUG_LOG"
  backend_host=$(echo "$BACKEND_URL" | sed -E 's|https?://||' | sed -E 's|:[0-9]+.*||')
  backend_port=$(echo "$BACKEND_URL" | grep -oE ':[0-9]+' | tr -d ':')
  
  if [ -z "$backend_port" ]; then
    if [[ "$BACKEND_URL" == https://* ]]; then
      backend_port=443
    else
      backend_port=80
    fi
  fi
  
  echo "Backend host: $backend_host" | tee -a "$FRONTEND_DEBUG_LOG"
  echo "Backend port: $backend_port" | tee -a "$FRONTEND_DEBUG_LOG"
  
  # Check if backend is reachable
  if nc -z "$backend_host" "$backend_port" 2> /dev/null; then
    echo "Backend is reachable" | tee -a "$FRONTEND_DEBUG_LOG"
    
    # Try a health check
    if command -v curl &> /dev/null; then
      echo "Backend health check:" | tee -a "$FRONTEND_DEBUG_LOG"
      curl -s "$BACKEND_URL/api/health" | tee -a "$FRONTEND_DEBUG_LOG"
      echo "" | tee -a "$FRONTEND_DEBUG_LOG"
    fi
  else
    echo "Backend is NOT reachable" | tee -a "$FRONTEND_DEBUG_LOG"
    echo "Warning: The frontend server may not function correctly without the backend" | tee -a "$FRONTEND_DEBUG_LOG"
  fi
fi

# Stop any existing frontend server processes
stop_frontend_server

# Start the frontend server
echo "Starting frontend server on $HOST:$PORT with backend URL $BACKEND_URL" | tee -a "$FRONTEND_DEBUG_LOG"
echo "Logs will be saved to $STDOUT_LOG and $STDERR_LOG" | tee -a "$FRONTEND_DEBUG_LOG"

cd "$(get_project_root)/frontend"
python server.py --host "$HOST" --port "$PORT" --backend-url "$BACKEND_URL" > "$STDOUT_LOG" 2> "$STDERR_LOG" &
SERVER_PID=$!

echo "Frontend server process started with PID $SERVER_PID" | tee -a "$FRONTEND_DEBUG_LOG"

# Wait a moment to make sure the server started
sleep 2

# Check if the server is running
if kill -0 "$SERVER_PID" 2> /dev/null; then
  echo "Frontend server started successfully" | tee -a "$FRONTEND_DEBUG_LOG"
  echo "Access the frontend at http://$HOST:$PORT"
  echo "To stop the server, run: ./scripts/stop_frontend.sh"
  echo "  or directly with: kill $SERVER_PID"
  
  # Save the PID to a file for easy stopping later
  mkdir -p "$(get_project_root)/.pid"
  echo "$SERVER_PID" > "$(get_project_root)/.pid/frontend.pid"
  
  # If in debug mode, tail the logs
  if [ "$DEBUG" = true ]; then
    echo "Debug mode: Showing server logs (Ctrl+C to stop viewing logs)..."
    echo "Server will continue running in the background"
    tail -f "$STDOUT_LOG" "$STDERR_LOG"
  fi
else
  echo "Error: Frontend server failed to start" | tee -a "$FRONTEND_DEBUG_LOG"
  echo "Check logs for more information:"
  echo "- $STDOUT_LOG"
  echo "- $STDERR_LOG"
  exit 1
fi