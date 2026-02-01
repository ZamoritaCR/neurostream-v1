#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# DOPAMINE.WATCH 2027 - QUICK START
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           🧠 dopamine.watch 2027 - Starting...                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt -q
    touch .deps_installed
fi

echo ""
echo "🚀 Starting server..."
echo ""
echo "   Frontend:  http://localhost:8000"
echo "   API Docs:  http://localhost:8000/api/docs"
echo "   Health:    http://localhost:8000/api/health"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

python3 server.py
