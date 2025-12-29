#!/bin/bash

# Phase 4 & Phase 5 Comprehensive Test Suite
# Tests all new features: scenarios, achievements, vocabulary, grammar exercises, writing, reading

set -e

BASE_URL="http://localhost:8000/api/v1"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OGI5YjhkYWY1ZDQ4OWQwMzYyYjQ1MDYiLCJleHAiOjE3NjMyNDgxOTUsInJvbGUiOiJ1c2VyIn0.xRcipmPyXsqi91W-cGYwsNggFOIcJGxmIBoQO9FbrRg"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Phase 4 & Phase 5 Comprehensive Test Suite            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

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

# ============================================================================
# PHASE 4 TESTS: Scenarios & Achievements
# ============================================================================

echo -e "\n${YELLOW}═══ PHASE 4: SCENARIOS & ACHIEVEMENTS ═══${NC}\n"

# Test 1: Get all scenarios
echo -e "${YELLOW}Test 1: Get All Scenarios${NC}"
SCENARIOS=$(curl -s "$BASE_URL/scenarios/")
SCENARIO_COUNT=$(echo $SCENARIOS | jq '.scenarios | length')
if [ "$SCENARIO_COUNT" -ge 15 ]; then
    print_result 0 "Scenarios loaded ($SCENARIO_COUNT scenarios)"
else
    print_result 1 "Expected at least 15 scenarios, got $SCENARIO_COUNT"
fi

# Test 2: Check new scenario categories
echo -e "\n${YELLOW}Test 2: New Scenario Categories${NC}"
CATEGORIES=$(echo $SCENARIOS | jq -r '[.scenarios[].category] | unique | .[]')
HAS_MEDICAL=$(echo "$CATEGORIES" | grep -q "medical" && echo "yes" || echo "no")
HAS_PROFESSIONAL=$(echo "$CATEGORIES" | grep -q "professional" && echo "yes" || echo "no")
HAS_HOUSING=$(echo "$CATEGORIES" | grep -q "housing" && echo "yes" || echo "no")

if [ "$HAS_MEDICAL" = "yes" ] && [ "$HAS_PROFESSIONAL" = "yes" ] && [ "$HAS_HOUSING" = "yes" ]; then
    print_result 0 "New categories present (medical, professional, housing)"
else
    print_result 1 "Missing new categories"
fi

# Test 3: Get achievements
echo -e "\n${YELLOW}Test 3: Get Achievements${NC}"
ACHIEVEMENTS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/achievements/list")
ACH_TOTAL=$(echo $ACHIEVEMENTS | jq -r '.total')
if [ "$ACH_TOTAL" -ge 20 ]; then
    print_result 0 "Achievements expanded ($ACH_TOTAL achievements)"
else
    print_result 1 "Expected at least 20 achievements, got $ACH_TOTAL"
fi

# Test 4: Check achievement tiers
echo -e "\n${YELLOW}Test 4: Achievement Tiers${NC}"
BRONZE=$(echo $ACHIEVEMENTS | jq '[.achievements[] | select(.achievement.tier == "bronze")] | length')
SILVER=$(echo $ACHIEVEMENTS | jq '[.achievements[] | select(.achievement.tier == "silver")] | length')
GOLD=$(echo $ACHIEVEMENTS | jq '[.achievements[] | select(.achievement.tier == "gold")] | length')
PLATINUM=$(echo $ACHIEVEMENTS | jq '[.achievements[] | select(.achievement.tier == "platinum")] | length')

if [ "$BRONZE" -gt 0 ] && [ "$SILVER" -gt 0 ] && [ "$GOLD" -gt 0 ] && [ "$PLATINUM" -gt 0 ]; then
    print_result 0 "All tiers present (Bronze: $BRONZE, Silver: $SILVER, Gold: $GOLD, Platinum: $PLATINUM)"
else
    print_result 1 "Missing achievement tiers"
fi

# Test 5: Leaderboard
echo -e "\n${YELLOW}Test 5: Leaderboard${NC}"
LEADERBOARD=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/analytics/leaderboard")
LEADER_COUNT=$(echo $LEADERBOARD | jq 'length')
if [ "$LEADER_COUNT" -gt 0 ]; then
    print_result 0 "Leaderboard working ($LEADER_COUNT users)"
else
    print_result 1 "Leaderboard empty"
fi

# ============================================================================
# PHASE 5 TESTS: Content Expansion
# ============================================================================

echo -e "\n${YELLOW}═══ PHASE 5: CONTENT EXPANSION ═══${NC}\n"

# Test 6: Vocabulary expansion
echo -e "${YELLOW}Test 6: Vocabulary Expansion${NC}"
VOCAB=$(curl -s "$BASE_URL/vocab/")
VOCAB_COUNT=$(echo $VOCAB | jq 'length')
if [ "$VOCAB_COUNT" -ge 200 ]; then
    print_result 0 "Vocabulary expanded ($VOCAB_COUNT words)"
else
    print_result 1 "Expected at least 200 words, got $VOCAB_COUNT"
fi

# Test 7: Grammar exercises categories
echo -e "\n${YELLOW}Test 7: Grammar Exercises${NC}"
GRAMMAR_CAT=$(curl -s "$BASE_URL/grammar-exercises/categories")
CAT_COUNT=$(echo $GRAMMAR_CAT | jq '.categories | length')
if [ "$CAT_COUNT" -ge 5 ]; then
    print_result 0 "Grammar exercise categories ($CAT_COUNT categories)"
else
    print_result 1 "Expected at least 5 categories, got $CAT_COUNT"
fi

# Test 8: Get grammar exercises
echo -e "\n${YELLOW}Test 8: Get Grammar Exercises${NC}"
EXERCISES=$(curl -s "$BASE_URL/grammar-exercises/exercises/articles")
EX_COUNT=$(echo $EXERCISES | jq '.exercises | length')
if [ "$EX_COUNT" -gt 0 ]; then
    print_result 0 "Grammar exercises available ($EX_COUNT exercises)"
else
    print_result 1 "No grammar exercises found"
fi

# Test 9: Writing prompts
echo -e "\n${YELLOW}Test 9: Writing Practice${NC}"
WRITING=$(curl -s "$BASE_URL/writing/prompts")
PROMPT_COUNT=$(echo $WRITING | jq '.prompts | length')
if [ "$PROMPT_COUNT" -ge 5 ]; then
    print_result 0 "Writing prompts available ($PROMPT_COUNT prompts)"
else
    print_result 1 "Expected at least 5 prompts, got $PROMPT_COUNT"
fi

# Test 10: Writing categories
echo -e "\n${YELLOW}Test 10: Writing Categories${NC}"
WRITING_CAT=$(curl -s "$BASE_URL/writing/categories")
WCAT_COUNT=$(echo $WRITING_CAT | jq '.categories | length')
if [ "$WCAT_COUNT" -ge 5 ]; then
    print_result 0 "Writing categories ($WCAT_COUNT categories)"
else
    print_result 1 "Expected at least 5 categories, got $WCAT_COUNT"
fi

# Test 11: Reading articles
echo -e "\n${YELLOW}Test 11: Reading Practice${NC}"
READING=$(curl -s "$BASE_URL/reading/articles")
ARTICLE_COUNT=$(echo $READING | jq '.articles | length')
if [ "$ARTICLE_COUNT" -ge 3 ]; then
    print_result 0 "Reading articles available ($ARTICLE_COUNT articles)"
else
    print_result 1 "Expected at least 3 articles, got $ARTICLE_COUNT"
fi

# Test 12: Reading categories
echo -e "\n${YELLOW}Test 12: Reading Categories${NC}"
READING_CAT=$(curl -s "$BASE_URL/reading/categories")
RCAT_COUNT=$(echo $READING_CAT | jq '.categories | length')
if [ "$RCAT_COUNT" -ge 5 ]; then
    print_result 0 "Reading categories ($RCAT_COUNT categories)"
else
    print_result 1 "Expected at least 5 categories, got $RCAT_COUNT"
fi

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

echo -e "\n${YELLOW}═══ INTEGRATION TESTS ═══${NC}\n"

# Test 13: Submit grammar exercise
echo -e "${YELLOW}Test 13: Submit Grammar Exercise${NC}"
SUBMIT_RESULT=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d '{"exercise_id":"art_001","user_answer":"die"}' \
    "$BASE_URL/grammar-exercises/submit")
CORRECT=$(echo $SUBMIT_RESULT | jq -r '.correct')
if [ "$CORRECT" = "true" ]; then
    print_result 0 "Grammar exercise submission working"
else
    print_result 1 "Grammar exercise submission failed"
fi

# Test 14: Get specific reading article
echo -e "\n${YELLOW}Test 14: Get Reading Article${NC}"
ARTICLE=$(curl -s "$BASE_URL/reading/articles/ra_001")
ARTICLE_TITLE=$(echo $ARTICLE | jq -r '.title')
if [ ! -z "$ARTICLE_TITLE" ] && [ "$ARTICLE_TITLE" != "null" ]; then
    print_result 0 "Reading article retrieval working"
else
    print_result 1 "Reading article retrieval failed"
fi

# Test 15: Grammar exercise stats
echo -e "\n${YELLOW}Test 15: Grammar Exercise Stats${NC}"
GRAMMAR_STATS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/grammar-exercises/stats")
TOTAL_ATTEMPTS=$(echo $GRAMMAR_STATS | jq -r '.total_attempts')
if [ "$TOTAL_ATTEMPTS" -ge 0 ]; then
    print_result 0 "Grammar stats working (attempts: $TOTAL_ATTEMPTS)"
else
    print_result 1 "Grammar stats failed"
fi

# Test 16: Daily grammar challenge
echo -e "\n${YELLOW}Test 16: Daily Grammar Challenge${NC}"
CHALLENGE=$(curl -s "$BASE_URL/grammar-exercises/daily-challenge")
CHALLENGE_ID=$(echo $CHALLENGE | jq -r '.challenge.id')
if [ ! -z "$CHALLENGE_ID" ] && [ "$CHALLENGE_ID" != "null" ]; then
    print_result 0 "Daily challenge working"
else
    print_result 1 "Daily challenge failed"
fi

# ============================================================================
# DATA INTEGRITY TESTS
# ============================================================================

echo -e "\n${YELLOW}═══ DATA INTEGRITY TESTS ═══${NC}\n"

# Test 17: Scenario data structure
echo -e "${YELLOW}Test 17: Scenario Data Structure${NC}"
FIRST_SCENARIO=$(echo $SCENARIOS | jq '.scenarios[0]')
HAS_CHARACTERS=$(echo $FIRST_SCENARIO | jq 'has("characters")')
HAS_OBJECTIVES=$(echo $FIRST_SCENARIO | jq 'has("objectives")')
if [ "$HAS_CHARACTERS" = "true" ] && [ "$HAS_OBJECTIVES" = "true" ]; then
    print_result 0 "Scenario structure valid"
else
    print_result 1 "Scenario structure invalid"
fi

# Test 18: Achievement data structure
echo -e "\n${YELLOW}Test 18: Achievement Data Structure${NC}"
FIRST_ACH=$(echo $ACHIEVEMENTS | jq '.achievements[0].achievement')
HAS_TIER=$(echo $FIRST_ACH | jq 'has("tier")')
HAS_CONDITIONS=$(echo $FIRST_ACH | jq 'has("conditions")')
if [ "$HAS_TIER" = "true" ] && [ "$HAS_CONDITIONS" = "true" ]; then
    print_result 0 "Achievement structure valid"
else
    print_result 1 "Achievement structure invalid"
fi

# Test 19: Vocabulary themes
echo -e "\n${YELLOW}Test 19: Vocabulary Themes${NC}"
VOCAB_SAMPLE=$(echo $VOCAB | jq '.[0]')
HAS_THEME=$(echo $VOCAB_SAMPLE | jq 'has("theme")')
HAS_LEVEL=$(echo $VOCAB_SAMPLE | jq 'has("level")')
if [ "$HAS_THEME" = "true" ] && [ "$HAS_LEVEL" = "true" ]; then
    print_result 0 "Vocabulary structure valid"
else
    print_result 1 "Vocabulary structure invalid"
fi

# Test 20: API health check
echo -e "\n${YELLOW}Test 20: API Health Check${NC}"
HEALTH=$(curl -s "$BASE_URL/analytics/health")
MONGO_STATUS=$(echo $HEALTH | jq -r '.services.mongodb')
if [ "$MONGO_STATUS" = "true" ]; then
    print_result 0 "API health check passed"
else
    print_result 1 "API health check failed"
fi

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    TEST SUMMARY                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo -e "${YELLOW}Phase 4 & Phase 5 Summary:${NC}"
    echo "  - Scenarios: $SCENARIO_COUNT total"
    echo "  - Achievements: $ACH_TOTAL total"
    echo "  - Vocabulary: $VOCAB_COUNT words"
    echo "  - Grammar Exercises: $CAT_COUNT categories"
    echo "  - Writing Prompts: $PROMPT_COUNT prompts"
    echo "  - Reading Articles: $ARTICLE_COUNT articles"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the errors above.${NC}"
    exit 1
fi
