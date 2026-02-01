#!/bin/bash

# ============================================
# Content Bot Dashboard Startup Script
# ============================================

echo ""
echo "============================================"
echo "🎛️  CONTENT BOT DASHBOARD"
echo "============================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT_DIR="$( dirname "$SCRIPT_DIR" )"

# Change to parent directory (content-bot)
cd "$PARENT_DIR"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "   Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "   Please edit .env with your credentials."
        echo ""
    fi
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check/install dependencies
echo "📦 Checking dependencies..."

if ! python3 -c "import flask" 2>/dev/null; then
    echo "   Installing Flask..."
    pip3 install flask flask-cors
fi

if ! python3 -c "import requests" 2>/dev/null; then
    echo "   Installing requests..."
    pip3 install requests
fi

if ! python3 -c "import openai" 2>/dev/null; then
    echo "   Installing openai..."
    pip3 install openai
fi

if ! python3 -c "import dotenv" 2>/dev/null; then
    echo "   Installing python-dotenv..."
    pip3 install python-dotenv
fi

echo "✅ Dependencies ready"
echo ""

# Start the server
echo "🚀 Starting dashboard server..."
echo ""
echo "   Dashboard: http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""
echo "============================================"
echo ""

# Open browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    sleep 2 && open "http://localhost:5000" &
fi

# Start Flask
cd "$SCRIPT_DIR"
python3 api.py
