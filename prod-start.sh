#!/bin/bash

# Production Environment Startup Script
# Uses Docker for all services including backend

set -e

echo "🚀 Starting German AI - Production Mode"
echo "=========================================="
echo ""

# Stop any native backend
echo "1️⃣  Stopping native backend..."
ps aux | grep uvicorn | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null || true
sleep 2

# Stop GPU Ollama if running (production uses Docker Ollama)
echo ""
echo "2️⃣  Checking Ollama services..."
if lsof -Pi :11435 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  GPU Ollama running on port 11435 (will use Docker Ollama instead)"
fi

# Start all Docker services
echo ""
echo "3️⃣  Starting Docker services..."
docker compose up -d

echo ""
echo "4️⃣  Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "5️⃣  Checking service status..."
docker compose ps

# Verify backend
echo ""
echo "6️⃣  Verifying backend..."
sleep 5
BACKEND_STATUS=$(curl -s http://localhost:8000/ 2>/dev/null | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "unknown")

if [ "$BACKEND_STATUS" = "ok" ]; then
    echo "✅ Backend is responding"
else
    echo "❌ Backend not responding"
    echo "Check logs: docker compose logs backend"
fi

# Final status
echo ""
echo "=========================================="
echo "🎉 Production Environment Ready!"
echo "=========================================="
echo ""
echo "📊 Services:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  Voice Chat: http://localhost:3000/voice-chat"
echo ""
echo "🔧 Backend:"
echo "  Environment: docker"
echo "  Ollama: Docker (port 11434)"
echo "  Logs: docker compose logs -f backend"
echo ""
echo "🛑 To stop:"
echo "  docker compose down"
echo ""
