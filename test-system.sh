#!/bin/bash

echo "🧪 Testing German AI System"
echo "=============================="
echo ""

# Test 1: Backend Status
echo "1️⃣  Testing Backend..."
BACKEND_STATUS=$(curl -s http://localhost:8000/ | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
if [ "$BACKEND_STATUS" = "ok" ]; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is NOT running"
    exit 1
fi

# Test 2: Backend Environment
echo ""
echo "2️⃣  Checking Backend Environment..."
curl -s http://localhost:8000/api/v1/debug/backend-info | python3 -m json.tool
echo ""

# Test 3: GPU Ollama
echo "3️⃣  Testing GPU Ollama (port 11435)..."
GPU_OLLAMA=$(curl -s http://localhost:11435/api/tags 2>/dev/null)
if [ ! -z "$GPU_OLLAMA" ]; then
    echo "✅ GPU Ollama is running"
    echo "   Models: $(echo $GPU_OLLAMA | python3 -c "import sys, json; models = json.load(sys.stdin)['models']; print(', '.join([m['name'] for m in models]))" 2>/dev/null)"
else
    echo "❌ GPU Ollama is NOT running"
fi

# Test 4: Docker Ollama
echo ""
echo "4️⃣  Testing Docker Ollama (port 11434)..."
DOCKER_OLLAMA=$(curl -s http://localhost:11434/api/tags 2>/dev/null)
if [ ! -z "$DOCKER_OLLAMA" ]; then
    echo "✅ Docker Ollama is running"
else
    echo "⚠️  Docker Ollama is NOT running (not needed for GPU mode)"
fi

# Test 5: Whisper
echo ""
echo "5️⃣  Testing Whisper..."
WHISPER_STATUS=$(curl -s http://localhost:9000/ 2>/dev/null)
if [ ! -z "$WHISPER_STATUS" ]; then
    echo "✅ Whisper is running"
    docker compose exec whisper env | grep ASR
else
    echo "❌ Whisper is NOT running"
fi

# Test 6: Piper
echo ""
echo "6️⃣  Testing Piper..."
PIPER_STATUS=$(timeout 2 nc -z localhost 10200 2>/dev/null && echo "ok")
if [ "$PIPER_STATUS" = "ok" ]; then
    echo "✅ Piper is running"
else
    echo "❌ Piper is NOT running"
fi

# Test 7: Voice Status
echo ""
echo "7️⃣  Testing Voice Features..."
curl -s http://localhost:8000/api/v1/voice/status | python3 -m json.tool
echo ""

# Summary
echo ""
echo "=============================="
echo "📊 System Summary"
echo "=============================="
echo "Backend:  Native (GPU-enabled)"
echo "Ollama:   GPU (port 11435)"
echo "Whisper:  Docker (port 9000)"
echo "Piper:    Docker (port 10200)"
echo ""
echo "Expected Performance:"
echo "  Transcribe:  0.5-1.5s (tiny model)"
echo "  Generate:    1-3s (GPU)"
echo "  Synthesize:  2-3s"
echo "  Total:       ~5-7s"
echo ""
