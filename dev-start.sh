#!/bin/bash

# Development Environment Startup Script
# Uses native backend with GPU Ollama for maximum performance

set -e

echo "🚀 Starting German AI - Development Mode"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if GPU Ollama is running
echo "1️⃣  Checking GPU Ollama..."
if lsof -Pi :11435 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${GREEN}✅ GPU Ollama is running on port 11435${NC}"
else
    echo -e "${YELLOW}⚠️  GPU Ollama not running. Starting...${NC}"
    ./setup-gpu.sh
fi

# Check if models are available
echo ""
echo "2️⃣  Checking Ollama models..."
MODELS=$(curl -s http://localhost:11435/api/tags 2>/dev/null | python3 -c "import sys, json; models = json.load(sys.stdin)['models']; print(', '.join([m['name'] for m in models]))" 2>/dev/null || echo "")
if [ ! -z "$MODELS" ]; then
    echo -e "${GREEN}✅ Models available: $MODELS${NC}"
else
    echo -e "${RED}❌ No models found${NC}"
    exit 1
fi

# Start Docker services (except backend)
echo ""
echo "3️⃣  Starting Docker services..."
docker compose up -d whisper piper redis frontend
sleep 3

# Check if backend is already running
echo ""
echo "4️⃣  Checking backend..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Backend already running on port 8000${NC}"
    read -p "Kill and restart? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ps aux | grep uvicorn | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null || true
        sleep 2
    else
        echo "Keeping existing backend"
    fi
fi

# Start native backend if not running
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${GREEN}Starting native backend with GPU...${NC}"
    cd backend
    
    # Check if venv exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Start backend in background
    uvicorn app.main:app --reload --port 8000 > /tmp/backend-dev.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    echo "Waiting for backend to start..."
    sleep 5
    
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${RED}❌ Backend failed to start${NC}"
        echo "Check logs: tail -f /tmp/backend-dev.log"
        exit 1
    fi
fi

# Verify environment
echo ""
echo "5️⃣  Verifying environment..."
BACKEND_INFO=$(curl -s http://localhost:8000/api/v1/debug/backend-info 2>/dev/null || echo "{}")
ENV=$(echo $BACKEND_INFO | python3 -c "import sys, json; print(json.load(sys.stdin).get('environment', 'unknown'))" 2>/dev/null || echo "unknown")
GPU=$(echo $BACKEND_INFO | python3 -c "import sys, json; print(json.load(sys.stdin).get('gpu_available', False))" 2>/dev/null || echo "false")

if [ "$ENV" = "local_gpu" ] && [ "$GPU" = "True" ]; then
    echo -e "${GREEN}✅ Backend using GPU Ollama${NC}"
else
    echo -e "${RED}❌ Backend NOT using GPU${NC}"
    echo "Environment: $ENV"
    echo "GPU Available: $GPU"
fi

# Final status
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 Development Environment Ready!${NC}"
echo "=========================================="
echo ""
echo "📊 Services:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  Voice Chat: http://localhost:3000/voice-chat"
echo ""
echo "🔧 Backend:"
echo "  Environment: $ENV"
echo "  GPU: $GPU"
echo "  Ollama: http://localhost:11435"
echo "  Logs: tail -f /tmp/backend-dev.log"
echo ""
echo "🛑 To stop:"
echo "  Backend: ps aux | grep uvicorn | grep -v grep | awk '{print \$2}' | xargs kill"
echo "  Docker: docker compose down"
echo ""
