#!/bin/bash

# AI Platform Startup Script
# Complete setup and start all services

set -e

echo "🚀 Starting My AI Platform..."
echo "================================"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "📥 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ai-models/llama
mkdir -p ai-models/qwen
mkdir -p ai-models/mistral
mkdir -p ai-models/embeddings
mkdir -p ai-models/finetuned
mkdir -p database/vector/chromadb
mkdir -p documents/raw
mkdir -p documents/processed
mkdir -p training/datasets
mkdir -p training/checkpoints
mkdir -p logs

# Install dependencies
echo "📦 Installing dependencies..."

# Backend
if [ -f "backend/requirements.txt" ]; then
    echo "  Installing Python dependencies..."
    pip install -r backend/requirements.txt
fi

# Frontend
if [ -f "frontend/package.json" ]; then
    echo "  Installing Node.js dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Root package
if [ -f "package.json" ]; then
    echo "  Installing root dependencies..."
    npm install
fi

# Download models
echo "🧠 Downloading AI models..."
echo "  This may take a while depending on your internet speed..."

# Start Ollama service
echo "🔄 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!
echo $OLLAMA_PID > .ollama.pid

# Wait for Ollama to start
sleep 5

# Pull models
echo "📥 Pulling models from Ollama..."
models=("qwen2.5:7b" "llama3.2:3b" "mistral:7b" "nomic-embed-text")

for model in "${models[@]}"; do
    echo "  Pulling $model..."
    ollama pull $model || echo "  Warning: Failed to pull $model"
done

# Initialize database
echo "🗄️  Initializing database..."
if [ -f "backend/src/database/db.py" ]; then
    python3 -c "
import sys
sys.path.append('backend')
from src.database.db import db
import asyncio

async def init_db():
    await db.connect()
    print('Database initialized')

asyncio.run(init_db())
"
fi

# Start backend
echo "⚙️  Starting backend server..."
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..
echo $BACKEND_PID > .backend.pid

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5000"
echo "   API Documentation: http://localhost:5000/docs"
echo ""
echo "🧠 AI Models Available:"
echo "   • Qwen 2.5 7B (Recommended for Hindi)"
echo "   • Llama 3.2 3B"
echo "   • Mistral 7B"
echo ""
echo "📚 Next Steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Upload documents in the Documents section"
echo "   3. Start chatting in the Chat section"
echo "   4. Train custom models in the Training section"
echo ""
echo "🛑 To stop all services, run: ./stop.sh"
echo ""
echo "Happy AI building! 🚀"