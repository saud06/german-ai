#!/bin/bash

echo "🧪 PHASE 4 INTEGRATION TEST"
echo "============================"
echo "Testing: Life Simulation Enhancement"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
BASE_URL="http://localhost:8000"

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
        echo "  Response: $body"
        ((FAILED++))
        return 1
    fi
}

echo "🔐 1. AUTHENTICATION"
echo "==================="

# Register test user
TIMESTAMP=$(date +%s)
EMAIL="phase4_test_$TIMESTAMP@test.com"
PASSWORD="test123"

test_endpoint "User Registration" "POST" "$BASE_URL/api/v1/auth/register" "{\"name\":\"Phase 4 Tester\",\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" ""

# Login
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo -e "Login: ${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "Login: ${RED}✗ FAIL${NC}"
    ((FAILED++))
    echo "Cannot proceed without authentication"
    exit 1
fi

echo ""

echo "🎯 2. ACHIEVEMENT SYSTEM"
echo "======================="

# Initialize achievements
test_endpoint "Initialize Achievements" "POST" "$BASE_URL/api/v1/achievements/initialize" "" ""

# Get user stats
test_endpoint "Get User Stats" "GET" "$BASE_URL/api/v1/achievements/stats" "" "$TOKEN"

# Get achievements list
test_endpoint "Get Achievements List" "GET" "$BASE_URL/api/v1/achievements/list" "" "$TOKEN"

# Get leaderboard
test_endpoint "Get XP Leaderboard" "GET" "$BASE_URL/api/v1/achievements/leaderboard/xp" "" "$TOKEN"

echo ""

echo "🎭 3. ENHANCED SCENARIOS"
echo "======================="

# List all scenarios
SCENARIOS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/scenarios/")
SCENARIO_COUNT=$(echo "$SCENARIOS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total', 0))" 2>/dev/null)

echo -n "Checking scenario count... "
if [ "$SCENARIO_COUNT" -ge 20 ]; then
    echo -e "${GREEN}✓ PASS${NC} ($SCENARIO_COUNT scenarios)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (Expected 20+, got $SCENARIO_COUNT)"
    ((FAILED++))
fi

# Test specific new scenarios
echo -n "Testing Doctor scenario... "
DOCTOR_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/scenarios/" | python3 -c "import sys, json; scenarios = json.load(sys.stdin).get('scenarios', []); doctor = [s for s in scenarios if 'Arzt' in s.get('name', '')]; print('found' if doctor else 'not found')" 2>/dev/null)
if [ "$DOCTOR_RESPONSE" = "found" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "Testing Job Interview scenario... "
JOB_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/scenarios/" | python3 -c "import sys, json; scenarios = json.load(sys.stdin).get('scenarios', []); job = [s for s in scenarios if 'Vorstellungsgespräch' in s.get('name', '')]; print('found' if job else 'not found')" 2>/dev/null)
if [ "$JOB_RESPONSE" = "found" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "Testing Emergency scenario... "
EMERGENCY_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/scenarios/" | python3 -c "import sys, json; scenarios = json.load(sys.stdin).get('scenarios', []); emergency = [s for s in scenarios if 'Notfall' in s.get('name', '')]; print('found' if emergency else 'not found')" 2>/dev/null)
if [ "$EMERGENCY_RESPONSE" = "found" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo ""

echo "👤 4. CHARACTER PERSONALITY SYSTEM"
echo "================================="

# Get a scenario and check for personality traits
SCENARIO_DETAIL=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/scenarios/" | python3 -c "import sys, json; scenarios = json.load(sys.stdin).get('scenarios', []); print(scenarios[0].get('id', '') if scenarios else '')" 2>/dev/null)

if [ -n "$SCENARIO_DETAIL" ]; then
    DETAIL_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/scenarios/$SCENARIO_DETAIL")
    
    echo -n "Checking personality traits... "
    HAS_PERSONALITY=$(echo "$DETAIL_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); chars = data.get('scenario', {}).get('characters', []); print('yes' if chars and 'personality_traits' in chars[0] else 'no')" 2>/dev/null)
    
    if [ "$HAS_PERSONALITY" = "yes" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
    
    echo -n "Checking emotion system... "
    HAS_EMOTION=$(echo "$DETAIL_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); chars = data.get('scenario', {}).get('characters', []); print('yes' if chars and 'emotion' in chars[0] else 'no')" 2>/dev/null)
    
    if [ "$HAS_EMOTION" = "yes" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
fi

echo ""

echo "💰 5. XP AND REWARDS SYSTEM"
echo "==========================="

# Update streak
test_endpoint "Update Daily Streak" "POST" "$BASE_URL/api/v1/achievements/streak/update" "" "$TOKEN"

# Check stats after streak update
STATS_AFTER=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/achievements/stats")
CURRENT_STREAK=$(echo "$STATS_AFTER" | python3 -c "import sys, json; print(json.load(sys.stdin).get('current_streak', 0))" 2>/dev/null)

echo -n "Checking streak update... "
if [ "$CURRENT_STREAK" -ge 1 ]; then
    echo -e "${GREEN}✓ PASS${NC} (Streak: $CURRENT_STREAK)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo ""

echo "🤖 6. AI MODEL VERIFICATION"
echo "==========================="

# Check Ollama
echo -n "Checking Ollama service... "
OLLAMA_STATUS=$(curl -s http://localhost:11434/api/tags 2>/dev/null | grep -o "models" || echo "")
if [ -n "$OLLAMA_STATUS" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Check Mistral model
echo -n "Checking Mistral 7B model... "
MISTRAL_STATUS=$(curl -s http://localhost:11434/api/tags 2>/dev/null | grep -o "mistral:7b" || echo "")
if [ -n "$MISTRAL_STATUS" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARNING${NC} (Model not loaded)"
fi

echo ""

echo "📊 7. INTEGRATION TESTS"
echo "======================"

# Test scenario with AI
echo -n "Testing scenario conversation... "
FIRST_SCENARIO=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/scenarios/" | python3 -c "import sys, json; scenarios = json.load(sys.stdin).get('scenarios', []); print(scenarios[0].get('id', '') if scenarios else '')" 2>/dev/null)

if [ -n "$FIRST_SCENARIO" ]; then
    # Get scenario details
    SCENARIO_CHARS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/scenarios/$FIRST_SCENARIO" | python3 -c "import sys, json; chars = json.load(sys.stdin).get('scenario', {}).get('characters', []); print(chars[0].get('id', '') if chars else '')" 2>/dev/null)
    
    if [ -n "$SCENARIO_CHARS" ]; then
        # Start conversation
        START_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" "$BASE_URL/api/v1/scenarios/$FIRST_SCENARIO/start?character_id=$SCENARIO_CHARS")
        CONV_ID=$(echo "$START_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('conversation_id', ''))" 2>/dev/null)
        
        if [ -n "$CONV_ID" ]; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((PASSED++))
        else
            echo -e "${RED}✗ FAIL${NC}"
            ((FAILED++))
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (No characters)"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗ FAIL${NC} (No scenarios)"
    ((FAILED++))
fi

echo ""

echo "======================================"
echo "📊 PHASE 4 TEST SUMMARY"
echo "======================================"
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL PHASE 4 TESTS PASSED!${NC}"
    echo ""
    echo "✅ Achievement System: Working"
    echo "✅ 20 Scenarios: Created"
    echo "✅ Character Personalities: Implemented"
    echo "✅ XP & Rewards: Functional"
    echo "✅ AI Integration: Ready"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  SOME TESTS FAILED${NC}"
    echo "Please review the failures above"
    exit 1
fi
