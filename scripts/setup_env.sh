#!/bin/bash

# Script to set up the development environment using uv

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing it now..."
    curl -sSf https://astral.sh/uv/install.sh | bash
    
    # Add reminder to restart shell
    echo "Please restart your shell or run 'source ~/.bashrc' (or equivalent) to update your PATH"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment using uv..."
    uv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment (for script usage)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source .venv/Scripts/activate
else
    # Unix/MacOS
    source .venv/bin/activate
fi

# Install dependencies with uv
echo "Installing project dependencies with uv..."
uv pip install -e ".[dev]"

# Optional: Install redis dependency if needed
read -p "Install Redis dependency for production messaging? (y/n) " install_redis
if [[ $install_redis == "y" || $install_redis == "Y" ]]; then
    echo "Installing Redis dependencies..."
    uv pip install -e ".[redis]"
fi

echo -e "\nEnvironment setup complete! To activate the environment, run:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo ".venv\\Scripts\\activate"
else
    echo "source .venv/bin/activate"
fi

echo -e "\nRun 'pytest' to execute tests."