#!/usr/bin/env python3
"""
Increment the build number in build_number.txt.

This script reads the current build number (in format YYYYMMDD.n),
and increments the revision number. If the date portion has changed,
it resets the revision to 1.

Usage:
    python scripts/increment_build.py
"""

import os
import datetime
from pathlib import Path

# Get the current directory of the script
FRONTEND_DIR = Path(__file__).parent.parent.absolute()
BUILD_FILE = FRONTEND_DIR / "build_number.txt"

def increment_build_number():
    """Increment the build number in build_number.txt."""
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    
    # Read the current build number
    if BUILD_FILE.exists():
        with open(BUILD_FILE, "r") as f:
            current_build = f.read().strip()
        
        # Parse the build number
        try:
            date_part, rev_part = current_build.split(".")
            
            # If the date has changed, reset revision to 1
            if date_part != current_date:
                new_build = f"{current_date}.1"
            else:
                # Increment the revision
                new_build = f"{date_part}.{int(rev_part) + 1}"
        except ValueError:
            # Invalid format, create new build number
            new_build = f"{current_date}.1"
    else:
        # File doesn't exist, create new build number
        new_build = f"{current_date}.1"
    
    # Write the new build number
    with open(BUILD_FILE, "w") as f:
        f.write(new_build)
    
    print(f"Build number incremented from {current_build if 'current_build' in locals() else 'none'} to {new_build}")
    return new_build

if __name__ == "__main__":
    increment_build_number()