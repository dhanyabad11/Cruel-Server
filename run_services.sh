#!/bin/bash
# Wrapper script to run all services from correct directory
# This ensures celery can find the app module properly

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/ai-cruel/backend"

echo "Starting all services (celery beat, celery worker, uvicorn)..."
echo "Working directory: $BACKEND_DIR"

cd "$BACKEND_DIR"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found in $BACKEND_DIR"
    exit 1
fi

# Run the services startup script
/opt/homebrew/bin/python3.9 start_services.py
