#!/bin/bash

# Dashboard Data Test Script
# Tests all dashboard endpoints to verify data is populated

set -e

BASE_URL="http://localhost:8000/api/v1"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OGI5YjhkYWY1ZDQ4OWQwMzYyYjQ1MDYiLCJleHAiOjE3NjMyNDgxOTUsInJvbGUiOiJ1c2VyIn0.xRcipmPyXsqi91W-cGYwsNggFOIcJGxmIBoQO9FbrRg"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Dashboard Data Verification Test Suite           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

# Test 1: User Stats
echo -e "\n${YELLOW}Test 1: User Statistics${NC}"
STATS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/achievements/stats")
LEVEL=$(echo $STATS | jq -r '.level')
SCENARIOS=$(echo $STATS | jq -r '.scenarios_completed')
WORDS=$(echo $STATS | jq -r '.words_learned')
STREAK=$(echo $STATS | jq -r '.current_streak')

if [ "$LEVEL" -gt 0 ] && [ "$SCENARIOS" -gt 0 ] && [ "$WORDS" -gt 0 ]; then
    print_result 0 "User stats populated (Level: $LEVEL, Scenarios: $SCENARIOS, Words: $WORDS, Streak: $STREAK)"
else
    print_result 1 "User stats missing data"
fi

# Test 2: Achievements List
echo -e "\n${YELLOW}Test 2: Achievements List${NC}"
ACH_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/achievements/list")
ACH_TOTAL=$(echo $ACH_RESPONSE | jq -r '.total')

if [ "$ACH_TOTAL" -gt 0 ]; then
    print_result 0 "Achievements loaded ($ACH_TOTAL achievements)"
    echo "  Sample achievements:"
    echo $ACH_RESPONSE | jq -r '.achievements[:3] | .[] | "  - \(.achievement.name) (\(.achievement.tier))"'
else
    print_result 1 "No achievements found"
fi

# Test 3: Unlocked Achievements
echo -e "\n${YELLOW}Test 3: Unlocked Achievements${NC}"
UNLOCKED=$(echo $ACH_RESPONSE | jq '[.achievements[] | select(.unlocked == true)] | length')

if [ "$UNLOCKED" -gt 0 ]; then
    print_result 0 "User has unlocked achievements ($UNLOCKED unlocked)"
    echo "  Unlocked:"
    echo $ACH_RESPONSE | jq -r '.achievements[] | select(.unlocked == true) | "  - \(.achievement.name) (\(.achievement.icon))"'
else
    print_result 1 "No unlocked achievements"
fi

# Test 4: Leaderboard
echo -e "\n${YELLOW}Test 4: Leaderboard${NC}"
LEADERBOARD=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/analytics/leaderboard")
LEADER_COUNT=$(echo $LEADERBOARD | jq 'length')

if [ "$LEADER_COUNT" -gt 0 ]; then
    print_result 0 "Leaderboard populated ($LEADER_COUNT users)"
    echo "  Top 3:"
    echo $LEADERBOARD | jq -r '.[:3] | .[] | "  \(.rank). \(.name) - Level \(.level) (\(.total_xp) XP)"'
else
    print_result 1 "Leaderboard empty"
fi

# Test 5: Statistics Tab Data
echo -e "\n${YELLOW}Test 5: Statistics Tab Data${NC}"
QUIZZES=$(echo $STATS | jq -r '.quizzes_completed')
ACCURACY=$(echo $STATS | jq -r '.quiz_accuracy')

if [ "$QUIZZES" -gt 0 ]; then
    print_result 0 "Statistics data available (Quizzes: $QUIZZES, Accuracy: $ACCURACY%)"
else
    print_result 1 "Statistics data missing"
fi

# Test 6: Scenarios Data
echo -e "\n${YELLOW}Test 6: Scenarios Available${NC}"
SCENARIOS_LIST=$(curl -s "$BASE_URL/scenarios/")
SCENARIO_COUNT=$(echo $SCENARIOS_LIST | jq '.scenarios | length')

if [ "$SCENARIO_COUNT" -gt 0 ]; then
    print_result 0 "Scenarios available ($SCENARIO_COUNT scenarios)"
else
    print_result 1 "No scenarios found"
fi

# Test 7: Vocabulary Data
echo -e "\n${YELLOW}Test 7: Vocabulary Words${NC}"
VOCAB=$(curl -s "$BASE_URL/vocab/")
VOCAB_COUNT=$(echo $VOCAB | jq 'length')

if [ "$VOCAB_COUNT" -gt 0 ]; then
    print_result 0 "Vocabulary words available ($VOCAB_COUNT words)"
else
    print_result 1 "No vocabulary words found"
fi

# Test 8: Review Cards
echo -e "\n${YELLOW}Test 8: Review Cards${NC}"
REVIEW_STATS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/reviews/stats")
TOTAL_CARDS=$(echo $REVIEW_STATS | jq -r '.total_cards')

if [ "$TOTAL_CARDS" -gt 0 ]; then
    print_result 0 "Review cards available ($TOTAL_CARDS cards)"
else
    print_result 1 "No review cards found"
fi

# Test 9: Achievement Categories
echo -e "\n${YELLOW}Test 9: Achievement Categories${NC}"
CATEGORIES=$(echo $ACH_RESPONSE | jq -r '[.achievements[].achievement.category] | unique | length')

if [ "$CATEGORIES" -ge 4 ]; then
    print_result 0 "Multiple achievement categories ($CATEGORIES categories)"
    echo "  Categories:"
    echo $ACH_RESPONSE | jq -r '[.achievements[].achievement.category] | unique | .[] | "  - \(.)"'
else
    print_result 1 "Limited achievement categories"
fi

# Test 10: User Rank in Leaderboard
echo -e "\n${YELLOW}Test 10: User Rank in Leaderboard${NC}"
USER_RANK=$(echo $LEADERBOARD | jq -r '.[] | select(.user_id == "68b9b8daf5d489d0362b4506") | .rank')

if [ -n "$USER_RANK" ] && [ "$USER_RANK" -gt 0 ]; then
    print_result 0 "User appears in leaderboard (Rank #$USER_RANK)"
else
    print_result 1 "User not in leaderboard"
fi

# Summary
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    TEST SUMMARY                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All dashboard data tests passed!${NC}"
    echo ""
    echo -e "${YELLOW}Dashboard Summary:${NC}"
    echo "  - Level: $LEVEL"
    echo "  - XP: $(echo $STATS | jq -r '.total_xp')"
    echo "  - Scenarios Completed: $SCENARIOS"
    echo "  - Words Learned: $WORDS"
    echo "  - Current Streak: $STREAK days"
    echo "  - Achievements Unlocked: $UNLOCKED/$ACH_TOTAL"
    echo "  - Leaderboard Rank: #$USER_RANK"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the errors above.${NC}"
    exit 1
fi
