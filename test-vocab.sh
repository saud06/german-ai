#!/bin/bash

# Vocabulary System Test Script
# Tests the vocab page functionality including progress persistence and daily word rotation

set -e

BASE_URL="http://localhost:8000/api/v1"
FRONTEND_URL="http://localhost:3000"

echo "================================"
echo "Vocabulary System Test"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to print test results
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

# Get auth token (using demo credentials)
echo "1. Authenticating..."
AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"saud@gmail.com","password":"password"}')

TOKEN=$(echo $AUTH_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ Authentication failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Authenticated successfully${NC}"
echo ""

# Test 1: Get today's vocabulary batch
echo "2. Testing vocabulary batch endpoint..."
VOCAB_RESPONSE=$(curl -s -X GET "$BASE_URL/vocab/today/batch?count=10&level=beginner" \
    -H "Authorization: Bearer $TOKEN")

WORD_COUNT=$(echo $VOCAB_RESPONSE | grep -o '"word"' | wc -l)
test_result $([ $WORD_COUNT -ge 5 ] && echo 0 || echo 1) "Get today's vocabulary batch (got $WORD_COUNT words)"
echo ""

# Test 2: Get vocab progress
echo "3. Testing progress tracking..."
PROGRESS_RESPONSE=$(curl -s -X GET "$BASE_URL/vocab/progress/today" \
    -H "Authorization: Bearer $TOKEN")

HAS_DATE=$(echo $PROGRESS_RESPONSE | grep -o '"date"' | wc -l)
test_result $([ $HAS_DATE -ge 1 ] && echo 0 || echo 1) "Get today's progress"
echo ""

# Test 3: Mark word as complete
echo "4. Testing word completion..."
FIRST_WORD=$(echo $VOCAB_RESPONSE | grep -o '"word":"[^"]*' | head -1 | cut -d'"' -f4)
TODAY=$(date +%Y-%m-%d)

COMPLETE_RESPONSE=$(curl -s -X POST "$BASE_URL/vocab/progress/mark-complete" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"word\":\"$FIRST_WORD\",\"date\":\"$TODAY\"}")

STATUS=$(echo $COMPLETE_RESPONSE | grep -o '"status":"ok"' | wc -l)
test_result $([ $STATUS -eq 1 ] && echo 0 || echo 1) "Mark word '$FIRST_WORD' as complete"
echo ""

# Test 4: Verify progress was saved
echo "5. Verifying progress persistence..."
PROGRESS_CHECK=$(curl -s -X GET "$BASE_URL/vocab/progress/today" \
    -H "Authorization: Bearer $TOKEN")

COMPLETED_COUNT=$(echo $PROGRESS_CHECK | grep -o '"completed_words"' | wc -l)
test_result $([ $COMPLETED_COUNT -ge 1 ] && echo 0 || echo 1) "Progress persisted in database"
echo ""

# Test 5: Browse vocabulary with difficulty filter
echo "6. Testing browse with difficulty levels..."
BROWSE_BEGINNER=$(curl -s -X GET "$BASE_URL/vocab/search?level=beginner&limit=5" \
    -H "Authorization: Bearer $TOKEN")

BROWSE_COUNT=$(echo $BROWSE_BEGINNER | grep -o '"word"' | wc -l)
test_result $([ $BROWSE_COUNT -ge 3 ] && echo 0 || echo 1) "Browse beginner vocabulary (got $BROWSE_COUNT words)"
echo ""

# Test 6: Browse intermediate level
echo "7. Testing intermediate level..."
BROWSE_INTERMEDIATE=$(curl -s -X GET "$BASE_URL/vocab/search?level=intermediate&limit=5" \
    -H "Authorization: Bearer $TOKEN")

INTER_COUNT=$(echo $BROWSE_INTERMEDIATE | grep -o '"word"' | wc -l)
test_result $([ $INTER_COUNT -ge 3 ] && echo 0 || echo 1) "Browse intermediate vocabulary (got $INTER_COUNT words)"
echo ""

# Test 7: Save word to user vocab
echo "8. Testing save word functionality..."
SAVE_RESPONSE=$(curl -s -X POST "$BASE_URL/vocab/save" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"word\":\"Wasser\",\"status\":\"learning\"}")

SAVE_STATUS=$(echo $SAVE_RESPONSE | grep -o '"status":"ok"' | wc -l)
test_result $([ $SAVE_STATUS -eq 1 ] && echo 0 || echo 1) "Save word to user vocabulary"
echo ""

# Test 8: List saved vocabulary
echo "9. Testing list saved vocabulary..."
LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/vocab/list?limit=10" \
    -H "Authorization: Bearer $TOKEN")

LIST_COUNT=$(echo $LIST_RESPONSE | grep -o '"word"' | wc -l)
test_result $([ $LIST_COUNT -ge 1 ] && echo 0 || echo 1) "List saved vocabulary (got $LIST_COUNT words)"
echo ""

# Test 9: Frontend accessibility
echo "10. Testing frontend accessibility..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/vocab")
test_result $([ $FRONTEND_STATUS -eq 200 ] && echo 0 || echo 1) "Vocab page accessible (HTTP $FRONTEND_STATUS)"
echo ""

# Summary
echo "================================"
echo "Test Summary"
echo "================================"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ Some tests failed${NC}"
    exit 1
fi
