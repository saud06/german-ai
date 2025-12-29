#!/bin/bash

# Phase 9: Gamification & Social Features - Test Suite

set -e

# Configuration
API_URL="http://localhost:8000/api/v1"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OGI5YjhkYWY1ZDQ4OWQwMzYyYjQ1MDYiLCJleHAiOjE3NjMzMzEyMTIsInJvbGUiOiJ1c2VyIn0.adlU9pxR24z8WEBLeayx6kXYdWZX3aqhusT5IzeRjiw"
USER_ID="68b9b8daf5d489d0362b4506"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test function
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "Testing: $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN" 2>&1)
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$API_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN" 2>&1)
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (Status: $status_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAIL${NC} (Expected: $expected_status, Got: $status_code)"
        echo "Response: $body"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

echo "🎮 Phase 9: Gamification & Social Features - Test Suite"
echo "=============================================="
echo ""

# 1. GAMIFICATION TESTS
echo -e "${BLUE}📊 1. GAMIFICATION TESTS${NC}"
echo "----------------------------"
test_endpoint "Get gamification profile" "GET" "/gamification/profile" "" "200"
test_endpoint "Update daily streak" "POST" "/gamification/streak/update" "" "200"
test_endpoint "Get streak history" "GET" "/gamification/streak/history?days=7" "" "200"
test_endpoint "Get user rank" "GET" "/gamification/rank" "" "200"
test_endpoint "Get XP history" "GET" "/gamification/xp/history?limit=10" "" "200"
test_endpoint "Get gamification stats" "GET" "/gamification/stats" "" "200"
test_endpoint "Award XP (lesson)" "POST" "/gamification/xp/award" '{"event_type":"lesson_complete"}' "200"
test_endpoint "Award XP (quiz)" "POST" "/gamification/xp/award" '{"event_type":"quiz_complete"}' "200"
test_endpoint "Award XP (scenario)" "POST" "/gamification/xp/award" '{"event_type":"scenario_complete"}' "200"
echo ""

# 2. LEADERBOARD TESTS
echo -e "${BLUE}🏆 2. LEADERBOARD TESTS${NC}"
echo "----------------------------"
test_endpoint "Get global leaderboard" "GET" "/gamification/leaderboard?limit=10" "" "200"
test_endpoint "Get public leaderboard" "GET" "/gamification/leaderboard/public?limit=10" "" "200"
echo ""

# 3. CHALLENGES TESTS
echo -e "${BLUE}🎯 3. WEEKLY CHALLENGES TESTS${NC}"
echo "----------------------------"
test_endpoint "Get active challenges" "GET" "/gamification/challenges" "" "200"
test_endpoint "Create challenge" "POST" "/gamification/challenges/create" '{"title":"Complete 10 Lessons","description":"Complete 10 lessons this week","challenge_type":"lessons","target":10,"xp_reward":200,"coin_reward":100}' "200"
echo ""

# 4. FRIEND SYSTEM TESTS
echo -e "${BLUE}👥 4. FRIEND SYSTEM TESTS${NC}"
echo "----------------------------"
test_endpoint "Get friends list" "GET" "/friends/list" "" "200"
test_endpoint "Get incoming requests" "GET" "/friends/requests/incoming" "" "200"
test_endpoint "Get outgoing requests" "GET" "/friends/requests/outgoing" "" "200"
test_endpoint "Get friends leaderboard" "GET" "/friends/leaderboard" "" "200"
test_endpoint "Search users" "GET" "/friends/search?query=test" "" "200"
echo ""

# 5. INTEGRATION TESTS (Award XP and check updates)
echo -e "${BLUE}🔄 5. INTEGRATION TESTS${NC}"
echo "----------------------------"
echo "Testing XP award flow..."

# Get initial profile
initial_profile=$(curl -s -X GET "$API_URL/gamification/profile" \
    -H "Authorization: Bearer $TOKEN")
initial_xp=$(echo $initial_profile | grep -o '"total_xp":[0-9]*' | cut -d':' -f2)
echo "Initial XP: $initial_xp"

# Award XP
curl -s -X POST "$API_URL/gamification/xp/award" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"event_type":"quiz_perfect","description":"Perfect quiz score!"}' > /dev/null

# Get updated profile
updated_profile=$(curl -s -X GET "$API_URL/gamification/profile" \
    -H "Authorization: Bearer $TOKEN")
updated_xp=$(echo $updated_profile | grep -o '"total_xp":[0-9]*' | cut -d':' -f2)
echo "Updated XP: $updated_xp"

if [ "$updated_xp" -gt "$initial_xp" ]; then
    echo -e "${GREEN}✓ XP increased successfully${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ XP did not increase${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

# 6. STREAK BONUS TESTS
echo -e "${BLUE}🔥 6. STREAK BONUS TESTS${NC}"
echo "----------------------------"
echo "Testing streak update..."

streak_result=$(curl -s -X POST "$API_URL/gamification/streak/update" \
    -H "Authorization: Bearer $TOKEN")
echo "Streak result: $streak_result"

current_streak=$(echo $streak_result | grep -o '"current_streak":[0-9]*' | cut -d':' -f2)
if [ ! -z "$current_streak" ]; then
    echo -e "${GREEN}✓ Streak updated: $current_streak days${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ Streak update failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

# Summary
echo "=============================================="
echo -e "${BLUE}📊 TEST SUMMARY${NC}"
echo "=============================================="
echo "Total Tests:  $TOTAL_TESTS"
echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    SUCCESS_RATE=100
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
fi

echo "Success rate: $SUCCESS_RATE%"
echo ""

exit 0
