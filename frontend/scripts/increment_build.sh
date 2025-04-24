#!/bin/bash
# Increment the build number for the frontend
# Usage: ./scripts/increment_build.sh

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
FRONTEND_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_FILE="$FRONTEND_DIR/build_number.txt"

# Get the current date in YYYYMMDD format
CURRENT_DATE=$(date +%Y%m%d)

# If the build file exists, read it
if [ -f "$BUILD_FILE" ]; then
    CURRENT_BUILD=$(cat "$BUILD_FILE")
    
    # Check if the build number is in the correct format
    if [[ $CURRENT_BUILD =~ ^[0-9]{8}\.[0-9]+$ ]]; then
        # Extract date and revision parts
        DATE_PART=${CURRENT_BUILD%.*}
        REV_PART=${CURRENT_BUILD#*.}
        
        # If the date has changed, reset revision to 1
        if [ "$DATE_PART" != "$CURRENT_DATE" ]; then
            NEW_BUILD="${CURRENT_DATE}.1"
        else
            # Increment the revision
            NEW_BUILD="${DATE_PART}.$((REV_PART + 1))"
        fi
    else
        # Invalid format, create new build number
        NEW_BUILD="${CURRENT_DATE}.1"
    fi
else
    # File doesn't exist, create new build number
    NEW_BUILD="${CURRENT_DATE}.1"
fi

# Write the new build number
echo "$NEW_BUILD" > "$BUILD_FILE"

echo "Build number incremented from ${CURRENT_BUILD:-none} to $NEW_BUILD"