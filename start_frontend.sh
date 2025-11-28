#!/bin/bash
# Start script for frontend (Next.js)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FRONTEND_DIR="$SCRIPT_DIR/ai-cruel/frontend"

echo "🚀 Starting Frontend..."
echo "Working directory: $FRONTEND_DIR"

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start Next.js dev server
echo "Starting Next.js on http://localhost:3000"
npm run dev
