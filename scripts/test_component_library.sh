#!/bin/bash
# Test Component Library Script
# Stops any running servers, starts a fresh instance, and opens the test runner

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Get project root
PROJECT_ROOT="$(get_project_root)"

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse command line arguments
CLEAN_START=true
RUN_TESTS=false
OPEN_BROWSER=true
BROWSER_CMD=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --no-clean)
      CLEAN_START=false
      shift
      ;;
    --run-tests)
      RUN_TESTS=true
      shift
      ;;
    --no-browser)
      OPEN_BROWSER=false
      shift
      ;;
    --browser)
      BROWSER_CMD="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--no-clean] [--run-tests] [--no-browser] [--browser BROWSER_COMMAND]"
      exit 1
      ;;
  esac
done

echo -e "${CYAN}===== Component Library Test Runner =====${NC}"

# Step 1: Stop running services if clean start is requested
if [ "$CLEAN_START" = true ]; then
  echo -e "\n${YELLOW}Stopping any running services...${NC}"
  
  # Use the cleanup_all.sh script for thorough cleaning
  # Only clean ports 3001 and 3002 to avoid disrupting other services
  if [ -f "$SCRIPT_DIR/cleanup_all.sh" ]; then
    echo "Using comprehensive cleanup script..."
    # Create a temporary function to only clean the ports we need
    cleanup_ports() {
      "$SCRIPT_DIR/cleanup_all.sh" --verbose | grep -v "Checking port" | grep -v "No processes" | grep -v "Port .* is free"
    }
    cleanup_ports
  else
    # Fallback to old cleanup method if the script isn't available
    echo "Fallback: Using basic cleanup method..."
    
    # Stop any running component test server
    ps aux | grep "server.py.*--port 3001" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
    ps aux | grep "server.py.*--port 3002" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
    
    echo "Checking for other frontend processes..."
    "$SCRIPT_DIR/stop_frontend.sh" --force > /dev/null 2>&1 || true
    
    # Also check for any processes on the test ports
    for port in 3001 3002; do
      if command -v lsof &> /dev/null; then
        port_pids=$(lsof -i :"$port" | grep LISTEN | awk '{print $2}' | uniq)
        
        if [ -n "$port_pids" ]; then
          echo "Stopping processes on port $port..."
          for pid in $port_pids; do
            echo "Killing process $pid on port $port"
            kill -9 "$pid" 2>/dev/null || true
          done
        fi
      fi
    done
  fi
  
  # Double check that ports are free
  echo "Verifying ports are free..."
  for port in 3001 3002; do
    if lsof -i :"$port" 2>/dev/null | grep LISTEN; then
      echo -e "${RED}WARNING: Port $port is still in use after cleanup${NC}"
      echo "You may need to manually kill the process occupying this port."
    else
      echo -e "${GREEN}Port $port is free${NC}"
    fi
  done
  
  # Wait a moment to ensure processes are stopped
  sleep 1
fi

# Step 2: Start a dedicated frontend server for component tests
echo -e "\n${GREEN}Starting component test server...${NC}"

# Create logs directory if it doesn't exist
LOGS_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOGS_DIR"

# Start the frontend server on port 3002 (different from normal frontend)
cd "$PROJECT_ROOT/frontend" || exit 1
python server.py --host 127.0.0.1 --port 3002 > "$LOGS_DIR/component_test.out.log" 2> "$LOGS_DIR/component_test.err.log" &
SERVER_PID=$!

# Save PID for later
echo "$SERVER_PID" > "$PROJECT_ROOT/.pid/component_test.pid"

echo "Server started on http://localhost:3002 (PID: $SERVER_PID)"
echo "Log files: "
echo " - $LOGS_DIR/component_test.out.log"
echo " - $LOGS_DIR/component_test.err.log"

# Wait for server to start
echo "Waiting for server to start..."
sleep 2

# Check if server started properly
if ! kill -0 "$SERVER_PID" 2>/dev/null; then
  echo -e "\n${RED}Error: Server failed to start.${NC}"
  echo "Check the log files for errors."
  exit 1
fi

# Verify server is reachable
if ! curl -s "http://localhost:3002/" > /dev/null; then
  echo -e "${RED}Warning: Server doesn't seem to be responding.${NC}"
  echo "Process is running but might not be serving requests yet."
else
  echo -e "${GREEN}Server is up and running!${NC}"
fi

# Step 3: Open browser if requested
if [ "$OPEN_BROWSER" = true ]; then
  echo -e "\n${CYAN}Opening test runner in browser...${NC}"
  
  # Determine browser command based on platform
  if [ -z "$BROWSER_CMD" ]; then
    if [ "$(uname)" == "Darwin" ]; then
      BROWSER_CMD="open"
    elif [ "$(uname)" == "Linux" ]; then
      if command -v xdg-open &> /dev/null; then
        BROWSER_CMD="xdg-open"
      elif command -v firefox &> /dev/null; then
        BROWSER_CMD="firefox"
      elif command -v google-chrome &> /dev/null; then
        BROWSER_CMD="google-chrome"
      else
        echo -e "${YELLOW}No browser command found. Please open manually:${NC}"
        echo "http://localhost:3002/test-runner"
        BROWSER_CMD=""
      fi
    elif [[ "$(uname)" == MINGW* ]] || [[ "$(uname)" == CYGWIN* ]]; then
      BROWSER_CMD="start"
    fi
  fi
  
  # Open browser if command is available
  if [ -n "$BROWSER_CMD" ]; then
    $BROWSER_CMD "http://localhost:3002/test-runner"
    echo "Opened test runner in browser."
  fi
fi

# Step 4: Run tests directly if requested
if [ "$RUN_TESTS" = true ]; then
  echo -e "\n${CYAN}Running component tests...${NC}"
  
  # Wait a moment to ensure server is fully started
  sleep 3
  
  # Use curl to fetch the test runner page
  RUNNER_HTML=$(curl -s "http://localhost:3002/test-runner")
  
  if [ -z "$RUNNER_HTML" ]; then
    echo -e "${RED}Error: Could not fetch test runner page.${NC}"
  else
    echo "Test runner loaded. Fetching test script..."
    
    # Fetch test script
    TEST_SCRIPT=$(curl -s "http://localhost:3002/tests/component-library-test.js")
    
    if [ -z "$TEST_SCRIPT" ]; then
      echo -e "${RED}Error: Could not fetch test script.${NC}"
    else
      echo "Test script loaded. Executing tests..."
      
      # Create a temporary HTML file with embedded test runner
      TMP_HTML=$(mktemp)
      
      cat > "$TMP_HTML" << EOL
<!DOCTYPE html>
<html>
<head>
  <title>Component Test Runner</title>
  <script>
    // Load necessary utilities and components
    ${TEST_SCRIPT}
    
    // Execute tests when page loads
    window.addEventListener('DOMContentLoaded', () => {
      console.log('Running component tests...');
      const tester = new ComponentTester();
      tester.runTests().then(results => {
        console.log('Tests completed:', JSON.stringify(results));
        document.getElementById('results').textContent = JSON.stringify(results, null, 2);
      });
    });
  </script>
</head>
<body>
  <h1>Component Test Results</h1>
  <pre id="results">Running tests...</pre>
</body>
</html>
EOL
      
      # Open the test runner in a browser
      if [ -n "$BROWSER_CMD" ]; then
        $BROWSER_CMD "$TMP_HTML"
        echo "Test execution started in browser. Check browser console for results."
      else
        echo -e "${YELLOW}No browser command available. Open this file manually:${NC}"
        echo "$TMP_HTML"
      fi
    fi
  fi
fi

echo -e "\n${GREEN}Component test environment is ready!${NC}"
echo "To stop the test server when finished, run: kill $SERVER_PID"
echo -e "Use the following URLs for testing:"
echo -e "  - Test Runner: ${CYAN}http://localhost:3002/test-runner${NC}"
echo -e "  - Component Test Page: ${CYAN}http://localhost:3002/component-test${NC}"