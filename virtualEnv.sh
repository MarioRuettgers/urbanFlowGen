#!/bin/bash

# Name of the requirements file
REQUIREMENTS_FILE="requirements.txt"

# Name of the virtual environment directory
VENV_DIR="venv"

# Check if requirements file exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
  echo "Error: $REQUIREMENTS_FILE not found!"
  exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment in ./$VENV_DIR"
  python3 -m venv "$VENV_DIR"
else
  echo "Virtual environment already exists in ./$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install libraries from the requirements file
echo "Installing libraries from $REQUIREMENTS_FILE..."
pip install -r "$REQUIREMENTS_FILE"

echo "Setup complete. Virtual environment is in ./$VENV_DIR"

