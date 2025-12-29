#!/bin/bash

echo "========================================="
echo "Testing UI/UX Improvements"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    echo -n "Testing $name... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$response" -eq "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response, expected $expected_code)"
        ((FAILED++))
    fi
}

echo "1. Testing Frontend Pages"
echo "-------------------------"
test_endpoint "Home Page" "http://localhost:3000"
test_endpoint "Dashboard" "http://localhost:3000/dashboard"
test_endpoint "Vocab" "http://localhost:3000/vocab"
test_endpoint "Grammar" "http://localhost:3000/grammar"
test_endpoint "Quiz" "http://localhost:3000/quiz"
test_endpoint "Speech" "http://localhost:3000/speech"
test_endpoint "Scenarios" "http://localhost:3000/scenarios"
test_endpoint "Reviews" "http://localhost:3000/reviews"
test_endpoint "Achievements" "http://localhost:3000/achievements"
test_endpoint "Voice Chat" "http://localhost:3000/voice-chat"
test_endpoint "Friends" "http://localhost:3000/friends"
test_endpoint "Account (New)" "http://localhost:3000/account"
test_endpoint "Test AI (Enhanced)" "http://localhost:3000/test-ai"
test_endpoint "Test WebSocket" "http://localhost:3000/test-websocket"
echo ""

echo "2. Testing Redirects"
echo "--------------------"
echo -n "Testing /pricing redirect... "
redirect=$(curl -s -o /dev/null -w "%{redirect_url}" -L "http://localhost:3000/pricing")
if [[ "$redirect" == *"/account"* ]] || curl -s "http://localhost:3000/pricing" | grep -q "Redirecting"; then
    echo -e "${GREEN}✓ PASS${NC} (redirects to /account)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "Testing /subscription redirect... "
if curl -s "http://localhost:3000/subscription" | grep -q "Redirecting"; then
    echo -e "${GREEN}✓ PASS${NC} (redirects to /account)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "Testing /referrals redirect... "
if curl -s "http://localhost:3000/referrals" | grep -q "Redirecting"; then
    echo -e "${GREEN}✓ PASS${NC} (redirects to /account)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

echo "3. Testing Backend APIs"
echo "-----------------------"
test_endpoint "AI Status" "http://localhost:8000/api/v1/ai/status"
test_endpoint "Voice Status" "http://localhost:8000/api/v1/voice/status"
test_endpoint "Health Check" "http://localhost:8000/api/v1/analytics/health"
test_endpoint "API Docs" "http://localhost:8000/docs"
echo ""

echo "4. Testing Service Status"
echo "-------------------------"
echo -n "Checking Ollama... "
if curl -s "http://localhost:8000/api/v1/ai/status" | grep -q '"ollama_available":true'; then
    echo -e "${GREEN}✓ Available${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ Unavailable${NC} (optional)"
fi

echo -n "Checking Whisper... "
if curl -s "http://localhost:8000/api/v1/voice/status" | grep -q '"whisper_available":true'; then
    echo -e "${GREEN}✓ Available${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ Unavailable${NC} (optional)"
fi

echo -n "Checking Piper... "
if curl -s "http://localhost:8000/api/v1/voice/status" | grep -q '"piper_available":true'; then
    echo -e "${GREEN}✓ Available${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ Unavailable${NC} (optional)"
fi
echo ""

echo "5. Checking Navigation Structure"
echo "--------------------------------"
echo -n "Checking main navigation items... "
nav_count=$(curl -s "http://localhost:3000/dashboard" | grep -o "starts=\"/" | wc -l | tr -d ' ')
if [ "$nav_count" -ge "8" ]; then
    echo -e "${GREEN}✓ PASS${NC} ($nav_count items found)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (expected ~10 items, found $nav_count)"
    ((FAILED++))
fi
echo ""

echo "========================================="
echo "Test Summary"
echo "========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    PERCENTAGE=$((PASSED * 100 / TOTAL))
    echo "Success Rate: $PERCENTAGE%"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ Some tests failed. Check the output above.${NC}"
    exit 1
fi
