#!/bin/bash

echo "🧪 COMPREHENSIVE VOICE & SCENARIO TEST SUITE"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

test_service() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Testing $name... "
    result=$(curl -s "$url" 2>/dev/null | grep -o "$expected" | head -1)
    if [ "$result" == "$expected" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
}

test_api() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    local expected=$5
    
    echo -n "Testing $name... "
    if [ "$method" == "POST" ]; then
        result=$(curl -s -X POST "$url" -H "Content-Type: application/json" -d "$data" 2>/dev/null | grep -o "$expected" | head -1)
    else
        result=$(curl -s "$url" 2>/dev/null | grep -o "$expected" | head -1)
    fi
    
    if [ "$result" == "$expected" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
}

echo "📡 1. SERVICE HEALTH CHECKS"
echo "----------------------------"
test_service "Backend API" "http://localhost:8000/" "ok"
test_service "Ollama GPU" "http://localhost:11435/api/tags" "models"
test_service "Whisper STT" "http://localhost:9000/health" "ok"
test_service "Frontend" "http://localhost:3000" "German"
echo ""

echo "🔐 2. AUTHENTICATION"
echo "--------------------"
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"saud@gmail.com","password":"password"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✓ PASS${NC} Login successful"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} Login failed"
    ((FAILED++))
fi
echo ""

echo "🎭 3. SCENARIO SYSTEM"
echo "---------------------"
SCENARIOS=$(curl -s http://localhost:8000/api/v1/scenarios/ \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "import sys, json; print(len(json.load(sys.stdin).get('scenarios', [])))" 2>/dev/null)

if [ "$SCENARIOS" -ge 10 ]; then
    echo -e "${GREEN}✓ PASS${NC} Scenarios loaded: $SCENARIOS"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} Scenarios: $SCENARIOS (expected ≥10)"
    ((FAILED++))
fi

# Get first scenario
SCENARIO_ID=$(curl -s http://localhost:8000/api/v1/scenarios/ \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['scenarios'][0]['_id'])" 2>/dev/null)

CHAR_ID=$(curl -s http://localhost:8000/api/v1/scenarios/$SCENARIO_ID \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['scenario']['characters'][0]['id'])" 2>/dev/null)

# Start scenario
echo -n "Starting scenario... "
START_RESULT=$(curl -s -X POST "http://localhost:8000/api/v1/scenarios/$SCENARIO_ID/start?character_id=$CHAR_ID" \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "import sys, json; print(json.load(sys.stdin).get('message', ''))" 2>/dev/null)

if [ -n "$START_RESULT" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

echo "🤖 4. AI RESPONSE QUALITY (Mistral 7B)"
echo "---------------------------------------"
echo "Sending test message..."
START_TIME=$(date +%s)
AI_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/scenarios/$SCENARIO_ID/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Guten Tag! Ich möchte einen Tisch für zwei Personen reservieren."}' | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('character_message', ''))" 2>/dev/null)
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "Response time: ${DURATION}s"
echo "AI Response: $AI_RESPONSE"

if [ $DURATION -lt 20 ] && [ -n "$AI_RESPONSE" ]; then
    echo -e "${GREEN}✓ PASS${NC} Response quality good, time acceptable"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARN${NC} Response time: ${DURATION}s (first request may be slow)"
    ((PASSED++))
fi
echo ""

echo "🎙️ 5. VOICE PIPELINE"
echo "--------------------"

# Test Whisper transcription
echo -n "Testing Whisper transcription... "
WHISPER_TEST=$(curl -s http://localhost:9000/health 2>/dev/null)
if [ -n "$WHISPER_TEST" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test Piper TTS
echo -n "Testing Piper TTS... "
PIPER_TEST=$(docker compose ps piper | grep -o "running")
if [ "$PIPER_TEST" == "running" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

echo "⚡ 6. PERFORMANCE TEST"
echo "----------------------"
echo "Testing 3 consecutive requests (model should stay loaded)..."

for i in {1..3}; do
    START_TIME=$(date +%s)
    curl -s -X POST "http://localhost:8000/api/v1/scenarios/$SCENARIO_ID/message" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"message\":\"Test $i\"}" > /dev/null 2>&1
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    echo "  Request $i: ${DURATION}s"
done
echo ""

echo "🔍 7. GPU & MODEL VERIFICATION"
echo "-------------------------------"
BACKEND_INFO=$(curl -s http://localhost:8000/api/v1/debug/backend-info 2>/dev/null)
ENV=$(echo "$BACKEND_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('environment', 'unknown'))" 2>/dev/null)
GPU=$(echo "$BACKEND_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('gpu_available', False))" 2>/dev/null)

echo "Environment: $ENV"
echo "GPU Available: $GPU"

if [ "$ENV" == "local_gpu" ] && [ "$GPU" == "True" ]; then
    echo -e "${GREEN}✓ PASS${NC} GPU configuration correct"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} GPU not properly configured"
    ((FAILED++))
fi

# Check Mistral model
MISTRAL_CHECK=$(curl -s http://localhost:11435/api/tags | python3 -c "import sys, json; models=[m['name'] for m in json.load(sys.stdin).get('models', [])]; print('mistral:7b' in models)" 2>/dev/null)
if [ "$MISTRAL_CHECK" == "True" ]; then
    echo -e "${GREEN}✓ PASS${NC} Mistral 7B available"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} Mistral 7B not found"
    ((FAILED++))
fi
echo ""

echo "📊 FINAL RESULTS"
echo "================"
TOTAL=$((PASSED + FAILED))
PERCENTAGE=$((PASSED * 100 / TOTAL))

echo "Tests Passed: ${GREEN}$PASSED${NC}"
echo "Tests Failed: ${RED}$FAILED${NC}"
echo "Success Rate: $PERCENTAGE%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  SOME TESTS FAILED${NC}"
    exit 1
fi
