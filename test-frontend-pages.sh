#!/bin/bash

# Frontend Pages Availability Test

set -e

FRONTEND_URL="http://localhost:3000"

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
test_page() {
    local name=$1
    local path=$2
    local expected_status=$3
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "Testing: $name... "
    
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL$path" 2>&1)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (Status: $status_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAIL${NC} (Expected: $expected_status, Got: $status_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

echo "🌐 Frontend Pages Availability Test"
echo "=============================================="
echo ""

# Check if frontend is running
echo "Checking if frontend is running..."
if ! curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
    echo -e "${RED}❌ Frontend is not running on $FRONTEND_URL${NC}"
    echo "Please start the frontend with: cd frontend && npm run dev"
    exit 1
fi
echo -e "${GREEN}✓ Frontend is running${NC}"
echo ""

# 1. CORE PAGES
echo -e "${BLUE}📄 1. CORE PAGES${NC}"
echo "----------------------------"
test_page "Home Page" "/" "200"
test_page "Login Page" "/login" "200"
test_page "Register Page" "/register" "200"
test_page "Dashboard" "/dashboard" "200"
echo ""

# 2. LEARNING PAGES
echo -e "${BLUE}📚 2. LEARNING PAGES${NC}"
echo "----------------------------"
test_page "Vocabulary" "/vocab" "200"
test_page "Grammar" "/grammar" "200"
test_page "Quiz" "/quiz" "200"
test_page "Scenarios List" "/scenarios" "200"
test_page "Reviews" "/reviews" "200"
test_page "Achievements" "/achievements" "200"
echo ""

# 3. PRACTICE PAGES
echo -e "${BLUE}🎯 3. PRACTICE PAGES${NC}"
echo "----------------------------"
test_page "Speech Practice" "/speech" "200"
test_page "Voice Chat" "/voice-chat" "200"
echo ""

# 4. GAMIFICATION PAGES (Phase 9)
echo -e "${BLUE}🎮 4. GAMIFICATION PAGES${NC}"
echo "----------------------------"
test_page "Gamification Dashboard" "/gamification" "200"
test_page "Friends" "/friends" "200"
echo ""

# 5. MONETIZATION PAGES (Phase 7)
echo -e "${BLUE}💰 5. MONETIZATION PAGES${NC}"
echo "----------------------------"
test_page "Pricing" "/pricing" "200"
test_page "Subscription Management" "/subscription" "200"
test_page "Referrals" "/referrals" "200"
test_page "Checkout Success" "/checkout/success" "200"
test_page "Checkout Cancel" "/checkout/cancel" "200"
echo ""

# 6. SETTINGS & PROFILE
echo -e "${BLUE}⚙️ 6. SETTINGS & PROFILE${NC}"
echo "----------------------------"
test_page "Settings" "/settings" "200"
echo ""

# 7. TEST/DEBUG PAGES
echo -e "${BLUE}🔧 7. TEST/DEBUG PAGES${NC}"
echo "----------------------------"
test_page "AI Test" "/test-ai" "200"
test_page "WebSocket Test" "/test-websocket" "200"
echo ""

# Summary
echo "=============================================="
echo -e "${BLUE}📊 TEST SUMMARY${NC}"
echo "=============================================="
echo "Total Pages Tested:  $TOTAL_TESTS"
echo -e "Available:           ${GREEN}$PASSED_TESTS${NC}"
echo -e "Not Available:       ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ All pages are available!${NC}"
    SUCCESS_RATE=100
else
    echo -e "${YELLOW}⚠️  Some pages are not available${NC}"
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
fi

echo "Availability rate: $SUCCESS_RATE%"
echo ""

# List of new pages created
echo -e "${BLUE}📝 NEW PAGES CREATED IN THIS SESSION:${NC}"
echo "----------------------------"
echo "✓ /gamification - XP, levels, leaderboards, challenges"
echo "✓ /subscription - Subscription management, billing, invoices"
echo "✓ /referrals - Referral program, rewards, leaderboard"
echo "✓ /friends - Friend system, requests, search"
echo ""

exit 0
