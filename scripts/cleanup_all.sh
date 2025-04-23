#!/bin/bash
# Comprehensive cleanup script for Agent Provocateur
# Forcefully terminates all running services and clears used ports

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse command line arguments
FORCE=true
CLEAN_PID=true
VERBOSE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --no-force)
      FORCE=false
      shift
      ;;
    --no-clean-pid)
      CLEAN_PID=false
      shift
      ;;
    --verbose|-v)
      VERBOSE=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--no-force] [--no-clean-pid] [--verbose]"
      exit 1
      ;;
  esac
done

echo -e "${CYAN}===== Agent Provocateur System Cleanup =====${NC}"

# First try graceful shutdown with the all_services.py script
echo -e "\n${YELLOW}Attempting graceful shutdown of all services...${NC}"
python "$SCRIPT_DIR/all_services.py" stop

# Function to kill processes by port
kill_port_process() {
  local port=$1
  local force=$2
  local port_pids
  
  echo "Checking port $port..."
  port_pids=$(lsof -i :"$port" | grep LISTEN | awk '{print $2}' | uniq)
  
  if [ -n "$port_pids" ]; then
    echo "Found processes using port $port: $port_pids"
    for pid in $port_pids; do
      # Get process info
      ps -p "$pid" -o pid,ppid,command
      
      if [ "$force" = true ]; then
        echo "Force killing process $pid"
        kill -9 "$pid" 2>/dev/null
      else
        echo "Stopping process $pid"
        kill "$pid" 2>/dev/null
        
        # Wait briefly for graceful shutdown
        sleep 1
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
          echo "Process still running. Force killing $pid"
          kill -9 "$pid" 2>/dev/null
        fi
      fi
    done
    
    # Verify port is now free
    sleep 1
    if lsof -i :"$port" 2>/dev/null; then
      echo -e "${RED}WARNING: Port $port is still in use after killing processes${NC}"
    else
      echo -e "${GREEN}Port $port is now free${NC}"
    fi
  else
    [ "$VERBOSE" = true ] && echo "No processes found using port $port"
  fi
}

# Kill processes by name pattern
kill_processes_by_pattern() {
  local pattern=$1
  local force=$2
  local pids
  
  echo "Looking for processes matching: $pattern"
  pids=$(ps aux | grep -E "$pattern" | grep -v grep | awk '{print $2}')
  
  if [ -n "$pids" ]; then
    echo "Found processes: $pids"
    for pid in $pids; do
      # Get process info
      ps -p "$pid" -o pid,ppid,command
      
      if [ "$force" = true ]; then
        echo "Force killing process $pid"
        kill -9 "$pid" 2>/dev/null
      else
        echo "Stopping process $pid"
        kill "$pid" 2>/dev/null
        
        # Wait briefly for graceful shutdown
        sleep 1
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
          echo "Process still running. Force killing $pid"
          kill -9 "$pid" 2>/dev/null
        fi
      fi
    done
  else
    [ "$VERBOSE" = true ] && echo "No processes found matching pattern: $pattern"
  fi
}

# Check and kill processes using known ports
echo -e "\n${YELLOW}Checking for processes on known ports...${NC}"
# Frontend ports
kill_port_process 3000 "$FORCE"
kill_port_process 3001 "$FORCE"
kill_port_process 3002 "$FORCE"

# Backend ports
kill_port_process 8000 "$FORCE" # MCP Server
kill_port_process 8080 "$FORCE" # Alternative API port
kill_port_process 8081 "$FORCE" # Alternative Web Search port
kill_port_process 8083 "$FORCE" # GraphRAG MCP

# Monitoring ports
kill_port_process 9090 "$FORCE" # Prometheus
kill_port_process 9091 "$FORCE" # Pushgateway
kill_port_process 6379 "$FORCE" # Redis

# Check for known process patterns
echo -e "\n${YELLOW}Checking for known server processes...${NC}"
kill_processes_by_pattern "server.py" "$FORCE"         # Frontend server
kill_processes_by_pattern "ap-server" "$FORCE"         # MCP server
kill_processes_by_pattern "redis-server" "$FORCE"      # Redis
kill_processes_by_pattern "web_search_mcp" "$FORCE"    # Web Search MCP
kill_processes_by_pattern "graphrag_mcp" "$FORCE"      # GraphRAG MCP

# Clean PID files if requested
if [ "$CLEAN_PID" = true ]; then
  echo -e "\n${YELLOW}Cleaning PID files...${NC}"
  
  # Get PID directory
  PID_DIR="$(get_project_root)/.pid"
  
  if [ -d "$PID_DIR" ]; then
    echo "Found PID directory: $PID_DIR"
    ls -la "$PID_DIR"
    
    # Delete all PID files
    rm -f "$PID_DIR"/*
    echo "PID files removed."
  else
    echo "No PID directory found."
  fi
fi

# Check Docker/Podman for monitoring containers
echo -e "\n${YELLOW}Checking for monitoring containers...${NC}"
if command -v docker &>/dev/null; then
  echo "Found Docker, checking for containers..."
  
  # Check if containers are running
  containers=$(docker ps -a | grep -E 'prometheus|grafana|pushgateway' | awk '{print $1}')
  
  if [ -n "$containers" ]; then
    echo "Found monitoring containers, stopping them..."
    
    # Stop monitoring containers
    cd "$(get_project_root)/monitoring" && docker-compose down
    
    # Force remove any remaining containers
    for container in prometheus grafana pushgateway; do
      docker rm -f "$container" 2>/dev/null
    done
    
    # Clean up volumes
    docker volume rm monitoring_grafana-storage 2>/dev/null
  else
    [ "$VERBOSE" = true ] && echo "No monitoring containers found."
  fi
elif command -v podman &>/dev/null; then
  echo "Found Podman, checking for containers..."
  
  # Check if containers are running
  containers=$(podman ps -a | grep -E 'prometheus|grafana|pushgateway' | awk '{print $1}')
  
  if [ -n "$containers" ]; then
    echo "Found monitoring containers, stopping them..."
    
    # Stop monitoring containers
    cd "$(get_project_root)/monitoring" && podman-compose down
    
    # Force remove any remaining containers
    for container in prometheus grafana pushgateway; do
      podman rm -f "$container" 2>/dev/null
    done
    
    # Clean up volumes
    podman volume rm monitoring_grafana-storage 2>/dev/null
  else
    [ "$VERBOSE" = true ] && echo "No monitoring containers found."
  fi
else
  echo "No container runtime found (Docker/Podman)."
fi

# Final verification
echo -e "\n${CYAN}=== Final verification ====${NC}"
echo "Checking for processes on any known ports..."

# Check all critical ports again
for port in 3000 3001 3002 8000 8080 8081 8083 9090 9091 6379; do
  if lsof -i :"$port" 2>/dev/null | grep LISTEN; then
    echo -e "${RED}WARNING: Port $port is still in use${NC}"
  else
    [ "$VERBOSE" = true ] && echo -e "${GREEN}Port $port is free${NC}"
  fi
done

# Check for any remaining Python processes matching our patterns
remaining_processes=$(ps aux | grep -E "server.py|ap-server|web_search_mcp|graphrag_mcp" | grep -v grep)
if [ -n "$remaining_processes" ]; then
  echo -e "${RED}WARNING: There are still some server processes running:${NC}"
  echo "$remaining_processes"
else
  echo -e "${GREEN}No remaining server processes found.${NC}"
fi

echo -e "\n${GREEN}Cleanup completed!${NC}"
echo "All services and ports should now be stopped and available."