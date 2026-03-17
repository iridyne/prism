#!/bin/bash
set -e

echo "🚀 Starting Prism Portfolio Optimization Framework..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found, copying from .env.example"
    cp .env.example .env
    echo "📝 Please edit .env with your API keys"
fi

# Start backend
echo "🔧 Starting backend..."
cd "$(dirname "$0")"
source .venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Prism is running!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

wait
