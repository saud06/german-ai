#!/bin/bash

# Start system for Task 4: Life Simulation
# Ensures native backend + Docker frontend (no Docker backend conflict)

echo "🚀 Starting German AI - Life Simulation"
echo "========================================"
echo ""

# Stop Docker backend if running (we use native backend)
if docker ps | grep -q german_backend; then
    echo "⚠️  Stopping Docker backend (using native backend instead)..."
    docker stop german_backend > /dev/null 2>&1
fi

# Check if native backend is running
if ! ps aux | grep -v grep | grep -q "uvicorn app.main:app"; then
    echo "🔧 Starting native backend..."
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --reload --port 8000 > /tmp/backend-native.log 2>&1 &
    cd ..
    sleep 3
fi

# Start Docker services (frontend, whisper, piper, redis)
echo "🐳 Starting Docker services..."
docker compose up -d whisper piper redis frontend > /dev/null 2>&1

# Wait for services
sleep 3

# Check status
echo ""
echo "📊 System Status:"
echo "================="

# Backend
if curl -s http://localhost:8000/ | grep -q "ok"; then
    echo "✅ Backend: Running (native, port 8000)"
else
    echo "❌ Backend: Not responding"
fi

# Frontend
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q 200; then
    echo "✅ Frontend: Running (Docker, port 3000)"
else
    echo "❌ Frontend: Not responding"
fi

# Scenarios API
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"saud@gmail.com","password":"password"}' | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
    SCENARIO_COUNT=$(curl -s "http://localhost:8000/api/v1/scenarios/" \
        -H "Authorization: Bearer $TOKEN" | \
        python3 -c "import sys, json; print(json.load(sys.stdin)['total'])" 2>/dev/null)
    echo "✅ Scenarios: $SCENARIO_COUNT available"
else
    echo "⚠️  Scenarios: Could not verify"
fi

echo ""
echo "🌐 Access URLs:"
echo "==============="
echo "  - Scenarios: http://localhost:3000/scenarios"
echo "  - Dashboard: http://localhost:3000/dashboard"
echo "  - API Docs:  http://localhost:8000/docs"
echo ""
echo "🔑 Login Credentials:"
echo "  - Email:    saud@gmail.com"
echo "  - Password: password"
echo ""
echo "✨ Ready to practice German! ✨"
echo ""
