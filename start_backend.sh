#!/bin/bash
# Quick start script for backend API only (no celery)
# Useful for development and testing

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/ai-cruel/backend"

echo "🚀 Starting Backend API..."
echo "Working directory: $BACKEND_DIR"

cd "$BACKEND_DIR"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found in $BACKEND_DIR"
    exit 1
fi

# Start uvicorn
echo "Starting uvicorn on http://localhost:8000"
/opt/homebrew/bin/python3.9 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
