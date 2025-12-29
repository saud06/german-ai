#!/bin/bash

# German AI Learner - System Monitoring Script
# Real-time monitoring of all services

echo "📊 German AI Learner - System Monitor"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get system metrics
get_metrics() {
    # Backend health
    BACKEND_STATUS=$(curl -s http://localhost:8000/ 2>/dev/null | grep -o '"status":"ok"' && echo "✓" || echo "✗")
    
    # Frontend health
    FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ 2>/dev/null)
    if [ "$FRONTEND_STATUS" = "200" ]; then
        FRONTEND_STATUS="✓"
    else
        FRONTEND_STATUS="✗"
    fi
    
    # MongoDB health
    MONGO_STATUS=$(docker exec german_mongodb_prod mongosh --quiet --eval "db.adminCommand('ping').ok" 2>/dev/null || echo "0")
    if [ "$MONGO_STATUS" = "1" ]; then
        MONGO_STATUS="✓"
    else
        MONGO_STATUS="✗"
    fi
    
    # Redis health
    REDIS_STATUS=$(docker exec german_redis_prod redis-cli ping 2>/dev/null | grep -o "PONG" && echo "✓" || echo "✗")
    
    # Ollama health
    OLLAMA_STATUS=$(curl -s http://localhost:11434/api/tags 2>/dev/null | grep -o "models" && echo "✓" || echo "✗")
    
    # Whisper health
    WHISPER_STATUS=$(curl -s http://localhost:9000/ 2>/dev/null | grep -o "Whisper" && echo "✓" || echo "✗")
    
    # Piper health
    PIPER_STATUS=$(echo "test" | nc -z localhost 10200 2>/dev/null && echo "✓" || echo "✗")
    
    # Get analytics
    ANALYTICS=$(curl -s http://localhost:8000/api/v1/analytics/metrics 2>/dev/null)
    
    # Parse analytics
    TOTAL_USERS=$(echo "$ANALYTICS" | grep -o '"total_users":[0-9]*' | grep -o '[0-9]*' || echo "0")
    TOTAL_SCENARIOS=$(echo "$ANALYTICS" | grep -o '"total_scenarios":[0-9]*' | grep -o '[0-9]*' || echo "0")
    TOTAL_QUIZZES=$(echo "$ANALYTICS" | grep -o '"total_quizzes":[0-9]*' | grep -o '[0-9]*' || echo "0")
    
    # System resources
    if command -v docker stats &> /dev/null; then
        DOCKER_STATS=$(docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | tail -n +2)
    fi
}

# Display dashboard
display_dashboard() {
    clear
    echo "📊 German AI Learner - System Monitor"
    echo "======================================"
    echo "$(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    echo "🔧 Service Status:"
    echo "  Backend:    $BACKEND_STATUS"
    echo "  Frontend:   $FRONTEND_STATUS"
    echo "  MongoDB:    $MONGO_STATUS"
    echo "  Redis:      $REDIS_STATUS"
    echo "  Ollama:     $OLLAMA_STATUS"
    echo "  Whisper:    $WHISPER_STATUS"
    echo "  Piper:      $PIPER_STATUS"
    echo ""
    
    echo "📈 Platform Metrics:"
    echo "  Total Users:     $TOTAL_USERS"
    echo "  Total Scenarios: $TOTAL_SCENARIOS"
    echo "  Total Quizzes:   $TOTAL_QUIZZES"
    echo ""
    
    if [ -n "$DOCKER_STATS" ]; then
        echo "💻 Resource Usage:"
        echo "$DOCKER_STATS"
        echo ""
    fi
    
    echo "Press Ctrl+C to exit | Refreshing every 5 seconds..."
}

# Main monitoring loop
main() {
    while true; do
        get_metrics
        display_dashboard
        sleep 5
    done
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n\n👋 Monitoring stopped"; exit 0' INT

# Run main loop
main
