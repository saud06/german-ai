#!/bin/bash

echo "🧪 COMPREHENSIVE FEATURE TEST SUITE"
echo "===================================="
echo ""
echo "Testing all German AI Learner features..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Test function
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    local auth=$5
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        if [ -n "$auth" ]; then
            response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $auth" "$url")
        else
            response=$(curl -s -w "\n%{http_code}" "$url")
        fi
    else
        if [ -n "$auth" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -H "Authorization: Bearer $auth" -d "$data" "$url")
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$url")
        fi
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        ((FAILED++))
        return 1
    fi
}

BASE_URL="http://localhost:8000"

echo "📡 1. HEALTH CHECK"
echo "=================="
test_endpoint "Backend Health" "GET" "$BASE_URL/" "" ""
echo ""

echo "🔐 2. AUTHENTICATION"
echo "==================="
# Register new user
TIMESTAMP=$(date +%s)
EMAIL="test_$TIMESTAMP@test.com"
test_endpoint "User Registration" "POST" "$BASE_URL/api/v1/auth/register" "{\"name\":\"Test User\",\"email\":\"$EMAIL\",\"password\":\"test123\"}" ""

# Login
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"test123\"}")
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo -e "Login: ${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "Login: ${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

echo "📚 3. VOCABULARY"
echo "==============="
test_endpoint "Get Vocabulary" "GET" "$BASE_URL/api/v1/vocab" "" "$TOKEN"
test_endpoint "Word of the Day" "GET" "$BASE_URL/api/v1/vocab/word-of-day" "" "$TOKEN"
echo ""

echo "📝 4. GRAMMAR"
echo "============"
test_endpoint "Get Grammar Rules" "GET" "$BASE_URL/api/v1/grammar" "" "$TOKEN"
test_endpoint "Grammar Check (Public)" "POST" "$BASE_URL/api/v1/grammar/check-public" "{\"sentence\":\"Ich bin ein Student\"}" ""
echo ""

echo "🎯 5. QUIZ SYSTEM"
echo "================"
test_endpoint "Start Quiz (Public)" "GET" "$BASE_URL/api/v1/quiz/start-public?level=A1&size=5" "" ""
test_endpoint "AI Quiz Generation" "POST" "$BASE_URL/api/v1/quiz-ai/generate" "{\"topic\":\"articles\",\"level\":\"A1\",\"size\":3}" "$TOKEN"
echo ""

echo "🎭 6. SCENARIOS"
echo "==============="
test_endpoint "List Scenarios" "GET" "$BASE_URL/api/v1/scenarios" "" "$TOKEN"
test_endpoint "Get Scenario Details" "GET" "$BASE_URL/api/v1/scenarios/restaurant-order" "" "$TOKEN"
echo ""

echo "🧠 7. SPACED REPETITION"
echo "======================="
test_endpoint "Get Review Stats" "GET" "$BASE_URL/api/v1/reviews/stats" "" "$TOKEN"
test_endpoint "Get Due Cards" "GET" "$BASE_URL/api/v1/reviews/due?limit=5" "" "$TOKEN"
test_endpoint "Workload Prediction" "GET" "$BASE_URL/api/v1/reviews/workload?days=7" "" "$TOKEN"
echo ""

echo "📊 8. ANALYTICS"
echo "==============="
test_endpoint "System Health" "GET" "$BASE_URL/api/v1/analytics/health" "" "$TOKEN"
test_endpoint "System Metrics" "GET" "$BASE_URL/api/v1/analytics/metrics" "" "$TOKEN"
test_endpoint "AI Features Stats" "GET" "$BASE_URL/api/v1/analytics/ai-features" "" "$TOKEN"
echo ""

echo "👤 9. USER PROGRESS"
echo "==================="
USER_ID=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('user_id', ''))" 2>/dev/null)
if [ -n "$USER_ID" ]; then
    test_endpoint "User Progress" "GET" "$BASE_URL/api/v1/progress/$USER_ID" "" "$TOKEN"
    test_endpoint "Weekly Activity" "GET" "$BASE_URL/api/v1/progress/$USER_ID/weekly" "" "$TOKEN"
fi
echo ""

echo "🎤 10. VOICE SERVICES"
echo "===================="
echo -n "Testing Whisper Service... "
WHISPER_HEALTH=$(curl -s http://localhost:5001/health 2>/dev/null | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null)
if [ "$WHISPER_HEALTH" = "healthy" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ SKIP${NC} (Service not running)"
fi

echo -n "Testing Piper Service... "
PIPER_HEALTH=$(curl -s http://localhost:5002/health 2>/dev/null | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null)
if [ "$PIPER_HEALTH" = "healthy" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ SKIP${NC} (Service not running)"
fi

echo -n "Testing Ollama Service... "
OLLAMA_HEALTH=$(curl -s http://localhost:11434/api/tags 2>/dev/null)
if [ -n "$OLLAMA_HEALTH" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ SKIP${NC} (Service not running)"
fi
echo ""

echo "======================================"
echo "📊 TEST SUMMARY"
echo "======================================"
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ SOME TESTS FAILED${NC}"
    exit 1
fi
