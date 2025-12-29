#!/bin/bash
# German AI Project Shutdown Script

set -e

echo "🛑 Stopping German AI Project..."
echo ""

# Stop native backend
echo "🐍 Stopping Native Backend..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    PID=$(lsof -Pi :8000 -sTCP:LISTEN -t)
    kill $PID
    echo "✅ Backend stopped (PID: $PID)"
else
    echo "ℹ️  Backend not running"
fi

# Stop native frontend
echo ""
echo "⚛️  Stopping Native Frontend..."
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    PID=$(lsof -Pi :3000 -sTCP:LISTEN -t)
    kill $PID
    echo "✅ Frontend stopped (PID: $PID)"
else
    echo "ℹ️  Frontend not running"
fi

# Stop Docker services
echo ""
echo "🐳 Stopping Docker services..."
cd "$(dirname "$0")"
docker compose stop redis whisper piper

echo ""
echo "✅ Project Stopped Successfully!"
echo ""
echo "ℹ️  Note: Ollama is still running (native GPU service)"
echo "   To stop Ollama: pkill ollama"
echo ""
