#!/bin/bash

# AI Platform Stop Script

echo "🛑 Stopping AI Platform..."

# Stop frontend
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    kill $FRONTEND_PID 2>/dev/null && echo "✓ Frontend stopped"
    rm .frontend.pid
fi

# Stop backend
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill $BACKEND_PID 2>/dev/null && echo "✓ Backend stopped"
    rm .backend.pid
fi

# Stop Ollama
if [ -f ".ollama.pid" ]; then
    OLLAMA_PID=$(cat .ollama.pid)
    kill $OLLAMA_PID 2>/dev/null && echo "✓ Ollama stopped"
    rm .ollama.pid
fi

# Stop Docker containers if running
if command -v docker-compose &> /dev/null; then
    docker-compose down 2>/dev/null && echo "✓ Docker containers stopped"
fi

echo ""
echo "✅ All services stopped successfully!"