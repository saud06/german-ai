#!/bin/bash
# German AI Project Startup Script
# Architecture: Native Backend + GPU Ollama | Docker for everything else

set -e

echo "🚀 Starting German AI Project..."
echo ""

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Ollama not running. Starting Ollama..."
    ollama serve > /dev/null 2>&1 &
    sleep 2
fi

# Verify Ollama models
echo "📦 Checking Ollama models..."
if curl -s http://localhost:11435/api/tags | grep -q "mistral:7b"; then
    echo "✅ Mistral 7B model available"
else
    echo "❌ Mistral 7B not found. Run: ollama pull mistral:7b"
    exit 1
fi

if curl -s http://localhost:11435/api/tags | grep -q "llama3.2:1b"; then
    echo "✅ Llama 3.2 1B model available"
else
    echo "❌ Llama 3.2 1B not found. Run: ollama pull llama3.2:1b"
    exit 1
fi

echo ""
echo "🐳 Starting Docker services (Redis, Whisper, Piper)..."
cd "$(dirname "$0")"
docker compose up -d redis whisper piper

echo ""
echo "⏳ Waiting for Docker services to be ready..."
sleep 5

# Check if backend is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Backend already running on port 8000"
else
    echo "🐍 Starting Native Backend (Python with GPU access)..."
    cd backend
    source venv/bin/activate
    nohup uvicorn app.main:app --reload --port 8000 > /tmp/backend-native.log 2>&1 &
    echo "Backend PID: $!"
    cd ..
    
    echo "⏳ Waiting for backend to start..."
    sleep 5
fi

# Check if frontend is already running
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Frontend already running on port 3000"
else
    echo "⚛️  Starting Native Frontend (Next.js Dev Mode with Hot Reload)..."
    cd frontend
    nohup npm run dev > /tmp/frontend-dev.log 2>&1 &
    echo "Frontend PID: $!"
    cd ..
    
    echo "⏳ Waiting for frontend to start..."
    sleep 8
fi

echo ""
echo "🔍 Health Check..."
HEALTH=$(curl -s http://localhost:8000/api/v1/analytics/health)
echo "$HEALTH" | python3 -m json.tool

echo ""
echo "✅ Project Started Successfully!"
echo ""
echo "📍 Access Points:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📊 Architecture:"
echo "   🖥️  Native (GPU + Dev Mode):"
echo "      - Backend (Python/FastAPI) - Port 8000 [Hot Reload]"
echo "      - Frontend (Next.js) - Port 3000 [Hot Reload]"
echo "      - Ollama (mistral:7b, llama3.2:1b) - Port 11435"
echo ""
echo "   🐳 Docker:"
echo "      - Redis - Port 6379"
echo "      - Whisper (STT) - Port 9000"
echo "      - Piper (TTS) - Port 10200"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f /tmp/backend-native.log"
echo "   Frontend: tail -f /tmp/frontend-dev.log"
echo "   Docker:   docker compose logs -f [service]"
echo ""
