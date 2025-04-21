#!/bin/bash
# Stop the Agent Provocateur frontend server with robust process detection
# This script finds and stops all frontend server processes

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Create frontend debug file
LOG_DIR="$(get_project_root)/logs"
mkdir -p "$LOG_DIR"
FRONTEND_DEBUG_LOG="$LOG_DIR/frontend_debug.log"

# Log the stop action
echo "$(date): Stopping frontend server" | tee -a "$FRONTEND_DEBUG_LOG"

# Process command line arguments
FORCE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --force|-f)
      FORCE=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--force|-f]"
      exit 1
      ;;
  esac
done

# Function to stop frontend processes
stop_frontend() {
  local force=$1
  local found=false
  
  echo "Looking for frontend server processes..." | tee -a "$FRONTEND_DEBUG_LOG"
  
  # First check if we have a PID file
  local pid_file="$(get_project_root)/.pid/frontend.pid"
  if [ -f "$pid_file" ]; then
    local pid=$(cat "$pid_file")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      echo "Found frontend server process from PID file" | tee -a "$FRONTEND_DEBUG_LOG"
      echo "Stopping process $pid" | tee -a "$FRONTEND_DEBUG_LOG"
      
      # Get process info for logging
      ps -p "$pid" -o pid,ppid,command | tee -a "$FRONTEND_DEBUG_LOG"
      
      if [ "$force" = true ]; then
        # Force kill
        echo "Force killing process $pid" | tee -a "$FRONTEND_DEBUG_LOG"
        kill -9 "$pid" 2> /dev/null
      else
        # Graceful kill
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
      fi
      
      # Remove the PID file
      rm "$pid_file"
      found=true
    else
      echo "PID file exists but process not running. Cleaning up." | tee -a "$FRONTEND_DEBUG_LOG"
      rm "$pid_file"
    fi
  fi
  
  # Find processes by the pattern 'server.py' in frontend
  local pids=$(ps aux | grep "[s]erver.py" | grep -i frontend | awk '{print $2}')
  
  if [ -z "$pids" ]; then
    # Try a more general search if the specific one failed
    pids=$(ps aux | grep "[s]erver.py" | awk '{print $2}')
  fi
  
  if [ -n "$pids" ]; then
    echo "Found frontend server processes. Stopping them..." | tee -a "$FRONTEND_DEBUG_LOG"
    for pid in $pids; do
      echo "Stopping process $pid" | tee -a "$FRONTEND_DEBUG_LOG"
      
      # Get process info for logging
      ps -p "$pid" -o pid,ppid,command | tee -a "$FRONTEND_DEBUG_LOG"
      
      if [ "$force" = true ]; then
        # Force kill
        echo "Force killing process $pid" | tee -a "$FRONTEND_DEBUG_LOG"
        kill -9 "$pid" 2> /dev/null
      else
        # Graceful kill
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
      fi
      
      found=true
    done
  fi
  
  # Check for processes using frontend ports
  for port in 3000 3001; do
    if command -v lsof &> /dev/null; then
      local port_pids=$(lsof -i :"$port" | grep LISTEN | awk '{print $2}' | uniq)
      
      if [ -n "$port_pids" ]; then
        echo "Found processes using port $port. Stopping them..." | tee -a "$FRONTEND_DEBUG_LOG"
        for pid in $port_pids; do
          echo "Stopping process $pid on port $port" | tee -a "$FRONTEND_DEBUG_LOG"
          
          # Get process info for logging
          ps -p "$pid" -o pid,ppid,command | tee -a "$FRONTEND_DEBUG_LOG"
          
          if [ "$force" = true ]; then
            # Force kill
            echo "Force killing process $pid" | tee -a "$FRONTEND_DEBUG_LOG"
            kill -9 "$pid" 2> /dev/null
          else
            # Graceful kill
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
          fi
          
          found=true
        done
      fi
    fi
  done
  
  if [ "$found" = false ]; then
    echo "No frontend server processes found" | tee -a "$FRONTEND_DEBUG_LOG"
    return 1
  fi
  
  return 0
}

# Run the stop function
if stop_frontend "$FORCE"; then
  echo "Frontend server stopped successfully" | tee -a "$FRONTEND_DEBUG_LOG"
  exit 0
else
  echo "No frontend server processes found to stop" | tee -a "$FRONTEND_DEBUG_LOG"
  exit 1
fi