#!/bin/bash

# Phase 7: Monetization & Growth - Comprehensive Test Script
# Tests: Payments, Referrals, Email Marketing, Analytics

echo "🚀 Phase 7: Monetization & Growth - Test Suite"
echo "=============================================="
echo ""

# Configuration
API_URL="http://localhost:8000/api/v1"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OGI5YjhkYWY1ZDQ4OWQwMzYyYjQ1MDYiLCJleHAiOjE3OTQ4NzM2MDB9.8rXdLxzLvJSCHWWWvVQfQqLxGEjbZyE7Kx0Yx7oCqzQ"
USER_ID="68b9b8daf5d489d0362b4506"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
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
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (Status: $status_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected: $expected_status, Got: $status_code)"
        echo "Response: $body"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "📊 1. REFERRAL PROGRAM TESTS"
echo "----------------------------"

# Create referral code
test_endpoint "Create referral code" "POST" "/referrals/code" "" "200"

# Get my referral code
test_endpoint "Get my referral code" "GET" "/referrals/code" "" "200"

# Get referral rewards
test_endpoint "Get referral rewards" "GET" "/referrals/rewards" "" "200"

# Get referral leaderboard
test_endpoint "Get referral leaderboard" "GET" "/referrals/leaderboard?limit=10" "" "200"

# Get referral stats
test_endpoint "Get referral stats" "GET" "/referrals/stats" "" "200"

echo ""
echo "💰 2. PAYMENT & SUBSCRIPTION TESTS"
echo "-----------------------------------"

# Get current subscription
test_endpoint "Get subscription" "GET" "/payments/subscription" "" "200"

# Get pricing tiers
test_endpoint "Get pricing tiers" "GET" "/payments/pricing" "" "200"

# Get invoices
test_endpoint "Get invoices" "GET" "/payments/invoices" "" "200"

# Check usage limits
test_endpoint "Check usage limits" "GET" "/payments/usage" "" "200"

echo ""
echo "📈 3. MARKETING ANALYTICS TESTS"
echo "--------------------------------"

# Track conversion event
test_endpoint "Track conversion" "POST" "/marketing/track" \
    '{"event_type":"signup","user_id":"'$USER_ID'","source":"direct"}' "200"

# Get conversion metrics
test_endpoint "Get conversion metrics" "GET" "/marketing/conversions?days=30" "" "200"

# Get conversions by source
test_endpoint "Get conversions by source" "GET" "/marketing/conversions/by-source?days=30" "" "200"

# Get conversion funnel
test_endpoint "Get conversion funnel" "GET" "/marketing/conversions/funnel?days=30" "" "200"

# Get revenue metrics
test_endpoint "Get revenue metrics" "GET" "/marketing/revenue?days=30" "" "200"

# Get retention metrics
test_endpoint "Get retention metrics" "GET" "/marketing/retention" "" "200"

# Get cohort analysis
test_endpoint "Get cohort analysis" "GET" "/marketing/cohort-analysis" "" "200"

echo ""
echo "🏢 4. ORGANIZATION TESTS (Phase 6)"
echo "-----------------------------------"

# List organizations
test_endpoint "List organizations" "GET" "/organizations/" "" "200"

# Get organization stats
ORG_ID="test-org-id"
# test_endpoint "Get org stats" "GET" "/organizations/$ORG_ID/stats" "" "200"

echo ""
echo "🔑 5. API KEY TESTS (Phase 6)"
echo "-----------------------------"

# List API keys
# test_endpoint "List API keys" "GET" "/api-keys/?organization_id=$ORG_ID" "" "200"

echo ""
echo "🪝 6. WEBHOOK TESTS (Phase 6)"
echo "-----------------------------"

# List webhook events
test_endpoint "List webhook events" "GET" "/webhooks/events/list" "" "200"

# List webhooks
# test_endpoint "List webhooks" "GET" "/webhooks/?organization_id=$ORG_ID" "" "200"

echo ""
echo "👤 7. ADMIN DASHBOARD TESTS (Phase 6)"
echo "--------------------------------------"

# Get analytics overview
# test_endpoint "Analytics overview" "GET" "/admin/analytics/overview?organization_id=$ORG_ID&days=30" "" "200"

echo ""
echo "🔒 8. GDPR COMPLIANCE TESTS (Phase 6)"
echo "--------------------------------------"

# Get consent preferences
test_endpoint "Get consent" "GET" "/gdpr/consent" "" "200"

# Get privacy policy
test_endpoint "Get privacy policy" "GET" "/gdpr/privacy-policy" "" "200"

# Get portable data
test_endpoint "Get portable data" "GET" "/gdpr/data-portability" "" "200"

echo ""
echo "📝 9. CONTENT TESTS (Phase 4 & 5)"
echo "----------------------------------"

# List scenarios
test_endpoint "List scenarios" "GET" "/scenarios/" "" "200"

# List achievements
test_endpoint "List achievements" "GET" "/achievements/" "" "200"

# Get vocabulary
test_endpoint "Get vocabulary" "GET" "/vocab/words?limit=10" "" "200"

# List grammar exercises
test_endpoint "List grammar exercises" "GET" "/grammar-exercises/categories" "" "200"

# List writing prompts
test_endpoint "List writing prompts" "GET" "/writing-practice/prompts" "" "200"

# List reading articles
test_endpoint "List reading articles" "GET" "/reading-practice/articles" "" "200"

echo ""
echo "📊 10. ANALYTICS TESTS (Phase 4)"
echo "---------------------------------"

# Get system metrics
test_endpoint "Get system metrics" "GET" "/analytics/metrics" "" "200"

# Get health check
test_endpoint "Health check" "GET" "/analytics/health" "" "200"

# Get AI features stats
test_endpoint "AI features stats" "GET" "/analytics/ai-features" "" "200"

echo ""
echo "🎯 11. SPACED REPETITION TESTS"
echo "-------------------------------"

# Get due reviews
test_endpoint "Get due reviews" "GET" "/reviews/due" "" "200"

# Get review stats
test_endpoint "Get review stats" "GET" "/reviews/stats" "" "200"

echo ""
echo "=============================================="
echo "📊 TEST SUMMARY"
echo "=============================================="
echo -e "Total Tests:  $TOTAL_TESTS"
echo -e "${GREEN}Passed:       $PASSED_TESTS${NC}"
echo -e "${RED}Failed:       $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "Phase 7 is fully functional!"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    echo "Success rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
    exit 1
fi
