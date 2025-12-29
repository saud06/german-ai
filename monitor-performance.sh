#!/bin/bash

# Performance Monitor - Shows backend, Ollama, and system stats

echo "📊 German AI Performance Monitor"
echo "================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

while true; do
    clear
    echo "📊 German AI Performance Monitor"
    echo "================================="
    echo ""
    
    # Backend Status
    echo -e "${BLUE}🔧 Backend Status:${NC}"
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        BACKEND_PID=$(lsof -Pi :8000 -sTCP:LISTEN -t | head -1)
        BACKEND_CPU=$(ps -p $BACKEND_PID -o %cpu | tail -1 | xargs)
        BACKEND_MEM=$(ps -p $BACKEND_PID -o %mem | tail -1 | xargs)
        echo -e "  ${GREEN}✅ Running${NC} (PID: $BACKEND_PID)"
        echo "  CPU: ${BACKEND_CPU}% | Memory: ${BACKEND_MEM}%"
    else
        echo -e "  ${YELLOW}⚠️  Not running${NC}"
    fi
    echo ""
    
    # Ollama GPU Status
    echo -e "${BLUE}⚡ Ollama GPU (Port 11435):${NC}"
    if lsof -Pi :11435 -sTCP:LISTEN -t >/dev/null 2>&1; then
        OLLAMA_PID=$(lsof -Pi :11435 -sTCP:LISTEN -t | head -1)
        OLLAMA_CPU=$(ps -p $OLLAMA_PID -o %cpu | tail -1 | xargs)
        OLLAMA_MEM=$(ps -p $OLLAMA_PID -o %mem | tail -1 | xargs)
        echo -e "  ${GREEN}✅ Running${NC} (PID: $OLLAMA_PID)"
        echo "  CPU: ${OLLAMA_CPU}% | Memory: ${OLLAMA_MEM}%"
        
        # Check loaded models
        MODELS=$(curl -s http://localhost:11435/api/ps 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); print(', '.join([m['name'] for m in data.get('models', [])]))" 2>/dev/null || echo "None")
        echo "  Models: $MODELS"
    else
        echo -e "  ${YELLOW}⚠️  Not running${NC}"
    fi
    echo ""
    
    # Docker Services
    echo -e "${BLUE}🐳 Docker Services:${NC}"
    WHISPER_STATUS=$(docker compose ps whisper 2>/dev/null | grep "Up" | wc -l)
    PIPER_STATUS=$(docker compose ps piper 2>/dev/null | grep "Up" | wc -l)
    
    if [ $WHISPER_STATUS -gt 0 ]; then
        echo -e "  Whisper: ${GREEN}✅ Running${NC}"
    else
        echo -e "  Whisper: ${YELLOW}⚠️  Stopped${NC}"
    fi
    
    if [ $PIPER_STATUS -gt 0 ]; then
        echo -e "  Piper:   ${GREEN}✅ Running${NC}"
    else
        echo -e "  Piper:   ${YELLOW}⚠️  Stopped${NC}"
    fi
    echo ""
    
    # System Resources
    echo -e "${BLUE}💻 System Resources:${NC}"
    
    # CPU Usage
    CPU_USAGE=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
    echo "  CPU Usage: ${CPU_USAGE}%"
    
    # Memory Usage
    MEM_TOTAL=$(sysctl -n hw.memsize | awk '{print $1/1024/1024/1024}')
    MEM_USED=$(vm_stat | grep "Pages active" | awk '{print $3}' | sed 's/\.//' | awk '{print $1*4096/1024/1024/1024}')
    echo "  Memory: ${MEM_USED}GB / ${MEM_TOTAL}GB"
    
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to exit${NC}"
    echo ""
    echo "Last updated: $(date '+%H:%M:%S')"
    
    sleep 2
done
