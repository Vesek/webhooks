#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

ENV_DIR="env"
REQUIREMENTS_FILE="requirements.txt"

# Check if the virtual environment exists
if [ ! -d "$ENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$ENV_DIR"
fi

# Activate the virtual environment
source "$ENV_DIR/bin/activate"

# Check if requirements file exists and install dependencies
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "Requirements file $REQUIREMENTS_FILE not found. Skipping dependency installation."
fi

# Run the FastAPI app
uvicorn main:app --host 127.0.0.1 --port 8000
