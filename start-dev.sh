#!/bin/bash

# Quick Start Script for Local Development

echo "🚀 Starting German AI Development Environment..."
echo ""

# Check if GPU backend is set up
if lsof -Pi :11435 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ GPU Backend detected on port 11435"
    echo "   Expected performance: ~5-8s total"
else
    echo "⚠️  GPU Backend not running on port 11435"
    echo "   Running setup script..."
    ./setup-gpu.sh
fi

echo ""
echo "🐳 Starting Docker services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ Development environment ready!"
echo ""
echo "📊 Services:"
echo "  - Frontend:  http://localhost:3000"
echo "  - Backend:   http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo ""
echo "🎯 Backend will automatically use:"
echo "  - GPU (port 11435) if available → ~5-8s"
echo "  - CPU (port 11434) as fallback → ~23-35s"
echo ""
echo "📝 Check backend logs:"
echo "  docker compose logs backend | grep 'Backend Environment'"
echo ""
