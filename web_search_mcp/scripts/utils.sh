#!/bin/bash
# Common utility functions for Web Search MCP scripts

# Print a section header
print_header() {
  echo ""
  echo "=========================================================================="
  echo "$1"
  echo "=========================================================================="
  echo ""
}

# Check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check for required commands
check_requirements() {
  local missing=0
  
  if ! command_exists podman; then
    if command_exists docker; then
      echo "Podman not found, but Docker found. We'll use Docker instead."
      # Create an alias for podman that points to docker
      alias podman=docker
    else
      echo "Error: Neither Podman nor Docker found. Please install one of them."
      missing=1
    fi
  fi
  
  if ! command_exists node; then
    echo "Error: Node.js not found. Please install Node.js v18 or newer."
    missing=1
  fi
  
  if ! command_exists npm; then
    echo "Error: npm not found. Please install Node.js and npm."
    missing=1
  fi
  
  if [ $missing -ne 0 ]; then
    echo "Please install the missing requirements and try again."
    return 1
  fi
  
  return 0
}

# Get the container engine (podman or docker)
get_container_engine() {
  if command_exists podman; then
    echo "podman"
  elif command_exists docker; then
    echo "docker"
  else
    echo "none"
  fi
}

# Ensure the .env file exists
ensure_env_file() {
  if [ ! -f .env ]; then
    if [ ! -f .env.example ]; then
      echo "Error: .env.example file not found. Cannot create .env file."
      return 1
    fi
    
    cp .env.example .env
    echo "Created .env file from .env.example."
    echo "Please edit the .env file to add your API keys before continuing."
    return 1
  fi
  
  return 0
}

# Check for API keys in the .env file
check_api_keys() {
  local has_keys=0
  
  # Source the .env file to get variables
  source .env
  
  if [ ! -z "$BRAVE_API_KEY" ]; then
    echo "✓ Brave Search API key found"
    has_keys=1
  else
    echo "✗ Brave Search API key not found"
  fi
  
  if [ ! -z "$GOOGLE_API_KEY" ] && [ ! -z "$GOOGLE_SEARCH_CX" ]; then
    echo "✓ Google Search API keys found"
    has_keys=1
  else
    echo "✗ Google Search API keys not found or incomplete"
  fi
  
  if [ ! -z "$BING_API_KEY" ]; then
    echo "✓ Bing Search API key found"
    has_keys=1
  else
    echo "✗ Bing Search API key not found"
  fi
  
  if [ $has_keys -eq 0 ]; then
    echo "No API keys found. Please add at least one API key to the .env file."
    return 1
  fi
  
  return 0
}