#!/bin/bash

# Voice Pipeline Test Script
# Tests the complete voice conversation pipeline

echo "🧪 Testing Voice Pipeline"
echo "=========================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test 1: Backend Health
echo "1️⃣  Testing Backend Health..."
BACKEND_STATUS=$(curl -s http://localhost:8000/ | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "unknown")
if [ "$BACKEND_STATUS" = "ok" ]; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend is not responding${NC}"
    exit 1
fi

# Test 2: GPU Environment
echo ""
echo "2️⃣  Testing GPU Environment..."
ENV_INFO=$(curl -s http://localhost:8000/api/v1/debug/backend-info 2>/dev/null)
ENV=$(echo $ENV_INFO | python3 -c "import sys, json; print(json.load(sys.stdin).get('environment', 'unknown'))" 2>/dev/null || echo "unknown")
GPU=$(echo $ENV_INFO | python3 -c "import sys, json; print(json.load(sys.stdin).get('gpu_available', False))" 2>/dev/null || echo "false")

if [ "$ENV" = "local_gpu" ]; then
    echo -e "${GREEN}✅ Environment: local_gpu${NC}"
else
    echo -e "${YELLOW}⚠️  Environment: $ENV (expected: local_gpu)${NC}"
fi

if [ "$GPU" = "True" ]; then
    echo -e "${GREEN}✅ GPU Available: True${NC}"
else
    echo -e "${RED}❌ GPU Available: False${NC}"
fi

# Test 3: Ollama GPU
echo ""
echo "3️⃣  Testing Ollama GPU..."
OLLAMA_MODELS=$(curl -s http://localhost:11435/api/tags 2>/dev/null | python3 -c "import sys, json; models = json.load(sys.stdin)['models']; print(', '.join([m['name'] for m in models]))" 2>/dev/null || echo "")
if [ ! -z "$OLLAMA_MODELS" ]; then
    echo -e "${GREEN}✅ Ollama GPU running${NC}"
    echo "   Models: $OLLAMA_MODELS"
else
    echo -e "${RED}❌ Ollama GPU not responding${NC}"
    exit 1
fi

# Test 4: Voice Services
echo ""
echo "4️⃣  Testing Voice Services..."
VOICE_STATUS=$(curl -s http://localhost:8000/api/v1/voice/status 2>/dev/null)
WHISPER=$(echo $VOICE_STATUS | python3 -c "import sys, json; print(json.load(sys.stdin).get('whisper_available', False))" 2>/dev/null || echo "false")
PIPER=$(echo $VOICE_STATUS | python3 -c "import sys, json; print(json.load(sys.stdin).get('piper_available', False))" 2>/dev/null || echo "false")

if [ "$WHISPER" = "True" ]; then
    echo -e "${GREEN}✅ Whisper available${NC}"
else
    echo -e "${RED}❌ Whisper not available${NC}"
fi

if [ "$PIPER" = "True" ]; then
    echo -e "${GREEN}✅ Piper available${NC}"
else
    echo -e "${RED}❌ Piper not available${NC}"
fi

# Test 5: Docker Services
echo ""
echo "5️⃣  Testing Docker Services..."
WHISPER_RUNNING=$(docker compose ps whisper | grep "Up" | wc -l)
PIPER_RUNNING=$(docker compose ps piper | grep "Up" | wc -l)

if [ $WHISPER_RUNNING -gt 0 ]; then
    echo -e "${GREEN}✅ Whisper container running${NC}"
else
    echo -e "${RED}❌ Whisper container not running${NC}"
fi

if [ $PIPER_RUNNING -gt 0 ]; then
    echo -e "${GREEN}✅ Piper container running${NC}"
else
    echo -e "${RED}❌ Piper container not running${NC}"
fi

# Test 6: Frontend
echo ""
echo "6️⃣  Testing Frontend..."
FRONTEND_STATUS=$(curl -s http://localhost:3000 2>/dev/null | head -c 100)
if [ ! -z "$FRONTEND_STATUS" ]; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
else
    echo -e "${RED}❌ Frontend not accessible${NC}"
fi

# Summary
echo ""
echo "=========================="
echo "📊 Test Summary"
echo "=========================="
echo ""

if [ "$BACKEND_STATUS" = "ok" ] && [ "$ENV" = "local_gpu" ] && [ "$GPU" = "True" ] && [ ! -z "$OLLAMA_MODELS" ] && [ "$WHISPER" = "True" ] && [ "$PIPER" = "True" ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "🎯 Voice Pipeline Status: READY"
    echo ""
    echo "📝 Next Steps:"
    echo "  1. Open http://localhost:3000/voice-chat"
    echo "  2. Click the microphone button"
    echo "  3. Speak in German: 'Hallo, wie geht's?'"
    echo "  4. Wait for AI response (~5-7 seconds)"
    echo ""
    echo "📊 Expected Performance:"
    echo "  - Transcription: 0.5-1.5s"
    echo "  - AI Generation: 1-3s (GPU)"
    echo "  - Synthesis: 2-3s"
    echo "  - Total: ~5-7s"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "  - Check logs: tail -f /tmp/backend-dev.log"
    echo "  - Restart: ./dev-start.sh"
    echo "  - Check services: docker compose ps"
    echo ""
    exit 1
fi
