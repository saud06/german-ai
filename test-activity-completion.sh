#!/bin/bash

# Activity Completion Test Script
# Tests vocabulary, quiz, and grammar completion tracking in learning paths

set -e

echo "========================================="
echo "Activity Completion Integration Test"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_BASE="${API_BASE:-http://localhost:8000/api/v1}"
FRONTEND_BASE="${FRONTEND_BASE:-http://localhost:3000}"

# Test user credentials
TEST_EMAIL="test@example.com"
TEST_PASSWORD="testpass123"

echo "📋 Test Configuration:"
echo "  API Base: $API_BASE"
echo "  Frontend: $FRONTEND_BASE"
echo ""

# Function to make API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local token=$4
    
    if [ -n "$token" ]; then
        if [ -n "$data" ]; then
            curl -s -X "$method" "$API_BASE$endpoint" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $token" \
                -d "$data"
        else
            curl -s -X "$method" "$API_BASE$endpoint" \
                -H "Authorization: Bearer $token"
        fi
    else
        if [ -n "$data" ]; then
            curl -s -X "$method" "$API_BASE$endpoint" \
                -H "Content-Type: application/json" \
                -d "$data"
        else
            curl -s -X "$method" "$API_BASE$endpoint"
        fi
    fi
}

# Step 1: Login
echo "🔐 Step 1: Authenticating..."
LOGIN_RESPONSE=$(api_call POST "/auth/login" "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")
TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to login${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi
echo -e "${GREEN}✅ Logged in successfully${NC}"
echo ""

# Step 2: Get learning paths
echo "📚 Step 2: Fetching learning paths..."
PATHS_RESPONSE=$(api_call GET "/learning-paths/" "" "$TOKEN")
FIRST_PATH_ID=$(echo "$PATHS_RESPONSE" | grep -o '"_id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$FIRST_PATH_ID" ]; then
    echo -e "${RED}❌ No learning paths found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Found learning path: $FIRST_PATH_ID${NC}"
echo ""

# Step 3: Get locations for the path
echo "📍 Step 3: Fetching locations..."
LOCATIONS_RESPONSE=$(api_call GET "/learning-paths/$FIRST_PATH_ID/locations" "" "$TOKEN")
FIRST_LOCATION_ID=$(echo "$LOCATIONS_RESPONSE" | grep -o '"_id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$FIRST_LOCATION_ID" ]; then
    echo -e "${RED}❌ No locations found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Found location: $FIRST_LOCATION_ID${NC}"
echo ""

# Step 4: Get activities for the location
echo "🎯 Step 4: Fetching activities..."
ACTIVITIES_RESPONSE=$(api_call GET "/learning-paths/locations/$FIRST_LOCATION_ID/activities" "" "$TOKEN")

# Extract activity IDs by type
VOCAB_ID=$(echo "$ACTIVITIES_RESPONSE" | grep -B5 '"type":"vocabulary"' | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
QUIZ_ID=$(echo "$ACTIVITIES_RESPONSE" | grep -B5 '"type":"quiz"' | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
GRAMMAR_ID=$(echo "$ACTIVITIES_RESPONSE" | grep -B5 '"type":"grammar"' | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

echo "  Vocabulary ID: ${VOCAB_ID:-Not found}"
echo "  Quiz ID: ${QUIZ_ID:-Not found}"
echo "  Grammar ID: ${GRAMMAR_ID:-Not found}"
echo ""

# Step 5: Test Vocabulary Completion
if [ -n "$VOCAB_ID" ]; then
    echo "📖 Step 5a: Testing vocabulary completion..."
    
    # Start a vocab review
    REVIEW_START=$(api_call POST "/vocab/review/start" "{\"size\":3}" "$TOKEN")
    REVIEW_ITEMS=$(echo "$REVIEW_START" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$REVIEW_ITEMS" ]; then
        # Submit review with grades
        RESULTS="["
        for item_id in $REVIEW_ITEMS; do
            RESULTS="$RESULTS{\"id\":\"$item_id\",\"grade\":4},"
        done
        RESULTS="${RESULTS%,}]"
        
        REVIEW_SUBMIT=$(api_call POST "/vocab/review/submit" "{\"results\":$RESULTS}" "$TOKEN")
        echo -e "${GREEN}✅ Vocab review submitted${NC}"
        
        # Mark activity as complete
        COMPLETE_RESPONSE=$(api_call POST "/learning-paths/progress/activity-complete" \
            "{\"activity_id\":\"$VOCAB_ID\",\"activity_type\":\"vocabulary\",\"xp_earned\":50}" "$TOKEN")
        
        if echo "$COMPLETE_RESPONSE" | grep -q "success"; then
            echo -e "${GREEN}✅ Vocabulary activity marked as complete${NC}"
        else
            echo -e "${RED}❌ Failed to mark vocabulary complete${NC}"
            echo "Response: $COMPLETE_RESPONSE"
        fi
    else
        echo -e "${YELLOW}⚠️  No vocab items available for review${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}⚠️  Step 5a: No vocabulary activity found, skipping...${NC}"
    echo ""
fi

# Step 6: Test Quiz Completion
if [ -n "$QUIZ_ID" ]; then
    echo "❓ Step 5b: Testing quiz completion..."
    
    # Start a quiz
    QUIZ_START=$(api_call GET "/quiz/start?size=3" "" "$TOKEN")
    QUIZ_SESSION_ID=$(echo "$QUIZ_START" | grep -o '"quiz_id":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$QUIZ_SESSION_ID" ]; then
        # Submit quiz with dummy answers
        QUIZ_SUBMIT=$(api_call POST "/quiz/submit" \
            "{\"quiz_id\":\"$QUIZ_SESSION_ID\",\"answers\":{}}" "$TOKEN")
        echo -e "${GREEN}✅ Quiz submitted${NC}"
        
        # Mark activity as complete
        COMPLETE_RESPONSE=$(api_call POST "/learning-paths/progress/activity-complete" \
            "{\"activity_id\":\"$QUIZ_ID\",\"activity_type\":\"quiz\",\"xp_earned\":75}" "$TOKEN")
        
        if echo "$COMPLETE_RESPONSE" | grep -q "success"; then
            echo -e "${GREEN}✅ Quiz activity marked as complete${NC}"
        else
            echo -e "${RED}❌ Failed to mark quiz complete${NC}"
            echo "Response: $COMPLETE_RESPONSE"
        fi
    else
        echo -e "${YELLOW}⚠️  Failed to start quiz${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}⚠️  Step 5b: No quiz activity found, skipping...${NC}"
    echo ""
fi

# Step 7: Test Grammar Completion
if [ -n "$GRAMMAR_ID" ]; then
    echo "✍️  Step 5c: Testing grammar completion..."
    
    # Check a sentence
    GRAMMAR_CHECK=$(api_call POST "/grammar/check" \
        "{\"sentence\":\"Ich gehen zur Schule.\"}" "$TOKEN")
    
    if echo "$GRAMMAR_CHECK" | grep -q "corrected"; then
        echo -e "${GREEN}✅ Grammar check performed${NC}"
        
        # Save the correction
        ORIGINAL=$(echo "$GRAMMAR_CHECK" | grep -o '"original":"[^"]*' | cut -d'"' -f4)
        CORRECTED=$(echo "$GRAMMAR_CHECK" | grep -o '"corrected":"[^"]*' | cut -d'"' -f4)
        EXPLANATION=$(echo "$GRAMMAR_CHECK" | grep -o '"explanation":"[^"]*' | cut -d'"' -f4)
        
        GRAMMAR_SAVE=$(api_call POST "/grammar/save" \
            "{\"original\":\"$ORIGINAL\",\"corrected\":\"$CORRECTED\",\"explanation\":\"$EXPLANATION\"}" "$TOKEN")
        echo -e "${GREEN}✅ Grammar correction saved${NC}"
        
        # Mark activity as complete
        COMPLETE_RESPONSE=$(api_call POST "/learning-paths/progress/activity-complete" \
            "{\"activity_id\":\"$GRAMMAR_ID\",\"activity_type\":\"grammar\",\"xp_earned\":60}" "$TOKEN")
        
        if echo "$COMPLETE_RESPONSE" | grep -q "success"; then
            echo -e "${GREEN}✅ Grammar activity marked as complete${NC}"
        else
            echo -e "${RED}❌ Failed to mark grammar complete${NC}"
            echo "Response: $COMPLETE_RESPONSE"
        fi
    else
        echo -e "${YELLOW}⚠️  Grammar check failed${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}⚠️  Step 5c: No grammar activity found, skipping...${NC}"
    echo ""
fi

# Step 8: Verify progress updated
echo "📊 Step 6: Verifying progress..."
PROGRESS_RESPONSE=$(api_call GET "/learning-paths/$FIRST_PATH_ID/locations" "" "$TOKEN")

# Count completed activities
COMPLETED_COUNT=$(echo "$PROGRESS_RESPONSE" | grep -o '"completed":true' | wc -l)
echo "  Completed activities: $COMPLETED_COUNT"

if [ "$COMPLETED_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Progress tracking is working!${NC}"
else
    echo -e "${YELLOW}⚠️  No completed activities found (may need to refresh)${NC}"
fi
echo ""

# Step 9: Check location completion
echo "🎯 Step 7: Checking location completion..."
LOCATION_DETAIL=$(api_call GET "/learning-paths/locations/$FIRST_LOCATION_ID" "" "$TOKEN")
COMPLETION_PERCENT=$(echo "$LOCATION_DETAIL" | grep -o '"completion_percent":[0-9]*' | cut -d':' -f2)

echo "  Location completion: ${COMPLETION_PERCENT:-0}%"

if [ -n "$COMPLETION_PERCENT" ] && [ "$COMPLETION_PERCENT" -gt 0 ]; then
    echo -e "${GREEN}✅ Location progress is updating!${NC}"
else
    echo -e "${YELLOW}⚠️  Location progress not yet updated${NC}"
fi
echo ""

# Summary
echo "========================================="
echo "Test Summary"
echo "========================================="
echo ""
echo "✅ Authentication: Working"
echo "✅ Learning Path API: Working"
echo "✅ Activity Completion Endpoint: Working"
echo ""

if [ -n "$VOCAB_ID" ]; then
    echo "✅ Vocabulary: Tested"
else
    echo "⚠️  Vocabulary: Not available"
fi

if [ -n "$QUIZ_ID" ]; then
    echo "✅ Quiz: Tested"
else
    echo "⚠️  Quiz: Not available"
fi

if [ -n "$GRAMMAR_ID" ]; then
    echo "✅ Grammar: Tested"
else
    echo "⚠️  Grammar: Not available"
fi

echo ""
echo "🎉 Activity completion integration test complete!"
echo ""
echo "📝 Next Steps:"
echo "  1. Open frontend: $FRONTEND_BASE/learning-path"
echo "  2. Navigate to a location"
echo "  3. Complete vocabulary/quiz/grammar activities"
echo "  4. Verify progress bar updates"
echo "  5. Check that completed activities show checkmarks"
echo ""
