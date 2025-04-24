#!/bin/bash
# Update UI script - increments build number and restarts the UI server
# Usage: ./scripts/update_ui.sh [--no-restart]

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
FRONTEND_DIR="$(dirname "$SCRIPT_DIR")"
NO_RESTART=false

# Check for --no-restart flag
if [[ "$1" == "--no-restart" ]]; then
    NO_RESTART=true
fi

echo "Updating UI..."

# Increment the build number
"$SCRIPT_DIR/increment_build.sh"

# Save the current build number
BUILD_NUMBER=$(cat "$FRONTEND_DIR/build_number.txt")

# Run any UI build steps here
# For example, compile assets, run webpack, etc.
echo "Build $BUILD_NUMBER prepared successfully."

# Restart the UI server unless --no-restart flag is provided
if [ "$NO_RESTART" = false ]; then
    echo "Restarting UI server..."
    
    # Try to identify running UI processes
    UI_PIDS=$(ps aux | grep "[p]ython.*server.py" | awk '{print $2}')
    
    if [ -n "$UI_PIDS" ]; then
        # Kill the existing UI processes
        echo "Stopping existing UI processes: $UI_PIDS"
        kill $UI_PIDS
        
        # Wait a moment for the processes to exit
        sleep 1
    else
        echo "No running UI processes found."
    fi
    
    # Start the UI server in the background
    echo "Starting UI server..."
    cd "$FRONTEND_DIR" && python server.py --reload > /dev/null 2>&1 &
    
    echo "UI server restarted with build $BUILD_NUMBER"
else
    echo "UI update completed with build $BUILD_NUMBER (server restart skipped)"
fi