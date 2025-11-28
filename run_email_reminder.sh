#!/bin/bash
# Wrapper script to run email reminder from correct directory
# This ensures the script runs in ai-cruel/backend/ where it can find dependencies

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/ai-cruel/backend"

echo "Starting email reminder system..."
echo "Working directory: $BACKEND_DIR"

cd "$BACKEND_DIR"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found in $BACKEND_DIR"
    exit 1
fi

# Run the reminder script
/opt/homebrew/bin/python3.9 simple_email_reminder.py
