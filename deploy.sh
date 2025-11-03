#!/bin/bash

# Simple deployment script for Digital Ocean
# Run this locally after pushing to GitHub

echo "🚀 Deploying to Digital Ocean..."

ssh root@198.211.106.97 << 'ENDSSH'
    cd ~/ai-cruel-backend-updated
    
    echo "📥 Pulling latest code..."
    git pull origin main
    
    echo "🛑 Stopping old processes..."
    pkill -f 'python3 simple_email_reminder.py' || true
    pkill -f uvicorn || true
    sleep 2
    
    echo "🚀 Starting email reminder..."
    nohup python3 simple_email_reminder.py > email_reminders.log 2>&1 &
    
    echo "🚀 Starting backend..."
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    
    sleep 3
    echo "✅ Deployment complete!"
    ps aux | grep -E 'uvicorn|simple_email' | grep -v grep
ENDSSH

echo ""
echo "🏥 Testing health..."
curl -s http://198.211.106.97:8000/health
echo ""
echo "✅ Deployment finished!"
