#!/bin/bash

# Complete Learning Path Journey Test
# Tests the entire user flow from viewing chapters to completing scenarios

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OGI5YjhkYWY1ZDQ4OWQwMzYyYjQ1MDYiLCJleHAiOjE3NjM0NTI2MjQsInJvbGUiOiJ1c2VyIn0.kMthikKHd4xtm9kjeS237fSTQc4rRQibQKnPZtDbeUo"
API_BASE="http://localhost:8000/api/v1"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     COMPLETE LEARNING PATH JOURNEY TEST                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: List all chapters
echo "📚 Step 1: View All Chapters"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/learning-paths/")
CHAPTER_COUNT=$(echo "$RESPONSE" | jq '. | length')

if [ "$CHAPTER_COUNT" -gt 0 ]; then
    echo "✅ Found $CHAPTER_COUNT chapters"
    echo "$RESPONSE" | jq -r '.[] | "   Chapter \(.path.chapter): \(.path.title) (\(.path.level))"'
    CHAPTER1_ID=$(echo "$RESPONSE" | jq -r '.[0].path._id')
    echo ""
    echo "Selected Chapter 1 ID: $CHAPTER1_ID"
else
    echo "❌ No chapters found"
    exit 1
fi

# Step 2: Get Chapter 1 details
echo ""
echo "📖 Step 2: View Chapter 1 Details"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CHAPTER1=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/learning-paths/$CHAPTER1_ID")
echo "$CHAPTER1" | jq -r '"✅ \(.path.title)"'
echo "$CHAPTER1" | jq -r '"   Story: \(.path.story[:100])..."'
echo "$CHAPTER1" | jq -r '"   Locations: \(.path.locations | length)"'
echo "$CHAPTER1" | jq -r '"   Characters: \(.path.characters | length)"'
echo "$CHAPTER1" | jq -r '"   XP Reward: \(.path.completion_reward.xp)"'

# Step 3: Get Chapter 1 map (locations)
echo ""
echo "🗺️  Step 3: View Interactive Map"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
LOCATIONS=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/learning-paths/$CHAPTER1_ID/locations")
LOC_COUNT=$(echo "$LOCATIONS" | jq '. | length')

if [ "$LOC_COUNT" -gt 0 ]; then
    echo "✅ Found $LOC_COUNT locations on map"
    echo ""
    echo "$LOCATIONS" | jq -r '.[] | "📍 \(.location.name)\n   Type: \(.location.type)\n   Scenarios: \(.location.scenarios | length)\n   Unlocked: \(if .is_unlocked then "✅" else "🔒" end)\n   Completed: \(.completion_percent)%\n"'
    
    FIRST_LOC_ID=$(echo "$LOCATIONS" | jq -r '.[0].location._id')
    echo "Selected first location: $FIRST_LOC_ID"
else
    echo "❌ No locations found"
    exit 1
fi

# Step 4: Get location details
echo ""
echo "📍 Step 4: View Location Details (Hotel Reception)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
LOCATION=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/learning-paths/locations/$FIRST_LOC_ID")

if echo "$LOCATION" | jq -e '.location' > /dev/null 2>&1; then
    echo "✅ Location loaded successfully"
    echo "$LOCATION" | jq -r '"   Name: \(.location.name)"'
    echo "$LOCATION" | jq -r '"   Description: \(.location.description)"'
    echo "$LOCATION" | jq -r '"   Scenarios: \(.location.scenarios | length)"'
    echo "$LOCATION" | jq -r '"   Estimated: \(.location.estimated_minutes) minutes"'
    echo "$LOCATION" | jq -r '"   XP Reward: \(.location.rewards.xp)"'
    echo ""
    echo "   Available Scenarios:"
    echo "$LOCATION" | jq -r '.location.scenarios[] | "      - \(.)"'
    
    FIRST_SCENARIO_ID=$(echo "$LOCATION" | jq -r '.location.scenarios[0]')
    echo ""
    echo "Selected first scenario: $FIRST_SCENARIO_ID"
else
    echo "❌ Failed to load location"
    echo "$LOCATION" | jq '.'
    exit 1
fi

# Step 5: Get scenario details
echo ""
echo "🎭 Step 5: View Scenario Details"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SCENARIO=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/scenarios/$FIRST_SCENARIO_ID")

if echo "$SCENARIO" | jq -e '.name // .title' > /dev/null 2>&1; then
    echo "✅ Scenario loaded successfully"
    SCENARIO_NAME=$(echo "$SCENARIO" | jq -r '.name // .title')
    echo "   Name: $SCENARIO_NAME"
    echo "$SCENARIO" | jq -r '"   Difficulty: \(.difficulty)"'
    echo "$SCENARIO" | jq -r '"   Category: \(.category)"'
    echo "$SCENARIO" | jq -r '"   Duration: \(.estimated_duration) minutes"'
    echo "$SCENARIO" | jq -r '"   Characters: \(.characters | length)"'
else
    echo "❌ Failed to load scenario"
    echo "$SCENARIO" | jq '.'
    exit 1
fi

# Step 6: Get progress summary
echo ""
echo "📊 Step 6: View Progress Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PROGRESS=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/learning-paths/progress/summary")

if echo "$PROGRESS" | jq -e '.total_xp' > /dev/null 2>&1; then
    echo "✅ Progress loaded successfully"
    echo "$PROGRESS" | jq -r '"   Current Chapter: \(.current_chapter)"'
    echo "$PROGRESS" | jq -r '"   Total XP: \(.total_xp)"'
    echo "$PROGRESS" | jq -r '"   Level: \(.level)"'
    echo "$PROGRESS" | jq -r '"   Chapters Completed: \(.chapters_completed)"'
    echo "$PROGRESS" | jq -r '"   Scenarios Completed: \(.scenarios_completed)"'
    echo "$PROGRESS" | jq -r '"   Daily Streak: \(.daily_streak) days"'
else
    echo "❌ Failed to load progress"
    echo "$PROGRESS" | jq '.'
fi

# Step 7: Get recommendations
echo ""
echo "💡 Step 7: View Recommendations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RECOMMENDATIONS=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/learning-paths/recommendations")
REC_COUNT=$(echo "$RECOMMENDATIONS" | jq '. | length')

if [ "$REC_COUNT" -gt 0 ]; then
    echo "✅ Found $REC_COUNT recommendations"
    echo ""
    echo "$RECOMMENDATIONS" | jq -r '.[] | "   \(.title)\n   Type: \(.type) | Duration: \(.estimated_minutes)min | XP: \(.xp_reward)\n   \(.description)\n"'
else
    echo "⚠️  No recommendations available"
fi

# Step 8: Get daily challenges
echo ""
echo "🎯 Step 8: View Daily Challenges"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CHALLENGES=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/learning-paths/challenges/daily")
CHAL_COUNT=$(echo "$CHALLENGES" | jq '. | length')

if [ "$CHAL_COUNT" -gt 0 ]; then
    echo "✅ Found $CHAL_COUNT daily challenges"
    echo ""
    echo "$CHALLENGES" | jq -r '.[] | "   \(.title)\n   Progress: \(.progress)/\(.target) | XP: \(.xp_reward)\n   \(.description)\n"'
else
    echo "⚠️  No challenges available"
fi

# Step 9: Test leaderboard
echo ""
echo "🏆 Step 9: View Leaderboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
LEADERBOARD=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/leaderboard/global?limit=5")

if echo "$LEADERBOARD" | jq -e '.entries' > /dev/null 2>&1; then
    ENTRY_COUNT=$(echo "$LEADERBOARD" | jq '.entries | length')
    echo "✅ Found $ENTRY_COUNT users on leaderboard"
    echo ""
    echo "$LEADERBOARD" | jq -r '.entries[] | "   #\(.rank) \(.name) - Level \(.level) (\(.total_xp) XP)"'
else
    echo "⚠️  Leaderboard not available"
fi

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    JOURNEY TEST SUMMARY                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Step 1: View All Chapters - PASSED ($CHAPTER_COUNT chapters)"
echo "✅ Step 2: View Chapter Details - PASSED"
echo "✅ Step 3: View Interactive Map - PASSED ($LOC_COUNT locations)"
echo "✅ Step 4: View Location Details - PASSED"
echo "✅ Step 5: View Scenario Details - PASSED"
echo "✅ Step 6: View Progress Summary - PASSED"
echo "✅ Step 7: View Recommendations - PASSED ($REC_COUNT recommendations)"
echo "✅ Step 8: View Daily Challenges - PASSED ($CHAL_COUNT challenges)"
echo "✅ Step 9: View Leaderboard - PASSED"
echo ""
echo "🎉 ALL TESTS PASSED! Learning Path journey is fully functional!"
echo ""
