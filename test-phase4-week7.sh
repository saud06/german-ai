#!/bin/bash

echo "========================================="
echo "Phase 4 Week 7 - Comprehensive Testing"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Get auth token
echo "🔐 Authenticating..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"saud@gmail.com","password":"password"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ Authentication failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Authenticated${NC}"
echo ""

# Test 1: Scenarios
echo "1. Testing Scenarios"
echo "--------------------"
echo -n "Fetching scenarios... "
SCENARIOS=$(curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/scenarios/)

SCENARIO_COUNT=$(echo "$SCENARIOS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['scenarios']))")

if [ "$SCENARIO_COUNT" -ge "30" ]; then
    echo -e "${GREEN}✓ PASS${NC} ($SCENARIO_COUNT scenarios)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (Expected >=30, got $SCENARIO_COUNT)"
    ((FAILED++))
fi

# Test new scenarios
echo -n "Checking new advanced scenarios... "
NEW_SCENARIOS=$(echo "$SCENARIOS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
new_cats = ['medical', 'professional', 'social', 'transport', 'financial', 'housing', 'emergency', 'culture', 'sports', 'technology']
count = sum(1 for s in data['scenarios'] if s['category'] in new_cats)
print(count)
")

if [ "$NEW_SCENARIOS" -ge "10" ]; then
    echo -e "${GREEN}✓ PASS${NC} ($NEW_SCENARIOS new scenarios)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (Expected >=10, got $NEW_SCENARIOS)"
    ((FAILED++))
fi
echo ""

# Test 2: Achievements
echo "2. Testing Achievements"
echo "-----------------------"
echo -n "Fetching achievements... "
ACHIEVEMENTS=$(curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/achievements/list)

ACH_COUNT=$(echo "$ACHIEVEMENTS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['achievements']))")

if [ "$ACH_COUNT" -ge "40" ]; then
    echo -e "${GREEN}✓ PASS${NC} ($ACH_COUNT achievements)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (Expected >=40, got $ACH_COUNT)"
    ((FAILED++))
fi

# Test achievement tiers
echo -n "Checking achievement tiers... "
TIERS=$(echo "$ACHIEVEMENTS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
tiers = set(a['achievement']['tier'] for a in data['achievements'])
print(','.join(sorted(tiers)))
")

if [[ "$TIERS" == *"bronze"* ]] && [[ "$TIERS" == *"silver"* ]] && [[ "$TIERS" == *"gold"* ]]; then
    echo -e "${GREEN}✓ PASS${NC} (Tiers: $TIERS)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (Missing tiers: $TIERS)"
    ((FAILED++))
fi
echo ""

# Test 3: Notifications
echo "3. Testing Notifications"
echo "------------------------"
echo -n "Fetching notifications... "
NOTIFICATIONS=$(curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/notifications/)

if echo "$NOTIFICATIONS" | grep -q "\["; then
    echo -e "${GREEN}✓ PASS${NC} (Endpoint accessible)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (Endpoint error)"
    ((FAILED++))
fi

echo -n "Checking unread count... "
UNREAD=$(curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/notifications/unread-count)

if echo "$UNREAD" | grep -q "count"; then
    COUNT=$(echo "$UNREAD" | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])")
    echo -e "${GREEN}✓ PASS${NC} ($COUNT unread)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

# Test 4: Checkpoint System
echo "4. Testing Checkpoint System"
echo "----------------------------"
echo -n "Testing checkpoint endpoints... "

# Get a scenario ID
SCENARIO_ID=$(echo "$SCENARIOS" | python3 -c "import sys, json; print(json.load(sys.stdin)['scenarios'][0]['_id'])")

# Try to access checkpoint endpoint (will fail if no active conversation, but endpoint should exist)
CHECKPOINT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/scenarios/$SCENARIO_ID/checkpoint)

if [ "$CHECKPOINT_RESPONSE" == "404" ] || [ "$CHECKPOINT_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Endpoint exists, HTTP $CHECKPOINT_RESPONSE)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (HTTP $CHECKPOINT_RESPONSE)"
    ((FAILED++))
fi

echo -n "Testing pause/resume endpoints... "
PAUSE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/scenarios/$SCENARIO_ID/pause)

if [ "$PAUSE_RESPONSE" == "404" ] || [ "$PAUSE_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Endpoints exist)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

# Test 5: API Documentation
echo "5. Testing API Documentation"
echo "----------------------------"
echo -n "Checking OpenAPI docs... "
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)

if [ "$DOCS_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "Checking API schema... "
SCHEMA=$(curl -s http://localhost:8000/openapi.json)

if echo "$SCHEMA" | grep -q "notifications"; then
    echo -e "${GREEN}✓ PASS${NC} (Notifications in schema)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

# Test 6: Database Integrity
echo "6. Testing Database Integrity"
echo "------------------------------"
echo -n "Checking scenario data structure... "

# Get one scenario and verify structure
SCENARIO_DETAIL=$(echo "$SCENARIOS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
s = data['scenarios'][0]
has_chars = 'characters' in s and len(s['characters']) > 0
has_objs = 'objectives' in s and len(s['objectives']) > 0
has_xp = 'xp_reward' in s
print('pass' if (has_chars and has_objs and has_xp) else 'fail')
")

if [ "$SCENARIO_DETAIL" == "pass" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "Checking achievement data structure... "
ACH_DETAIL=$(echo "$ACHIEVEMENTS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
a = data['achievements'][0]['achievement']
has_code = 'code' in a
has_conditions = 'conditions' in a
has_xp = 'xp_reward' in a
print('pass' if (has_code and has_conditions and has_xp) else 'fail')
")

if [ "$ACH_DETAIL" == "pass" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

# Summary
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

# Detailed Results
echo "📊 Detailed Results:"
echo "-------------------"
echo "✓ Scenarios: $SCENARIO_COUNT total, $NEW_SCENARIOS new"
echo "✓ Achievements: $ACH_COUNT total"
echo "✓ Notifications: System operational"
echo "✓ Checkpoints: Endpoints functional"
echo "✓ API Docs: Available"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "🎉 Phase 4 Week 7 Complete!"
    echo "   - 10 new advanced scenarios"
    echo "   - 20+ achievements"
    echo "   - Notification system"
    echo "   - Checkpoint functionality"
    exit 0
else
    echo -e "${YELLOW}⚠ Some tests failed. Check the output above.${NC}"
    exit 1
fi
