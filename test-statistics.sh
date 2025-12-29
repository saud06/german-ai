#!/bin/bash

echo "📊 STATISTICS & LEADERBOARD TEST"
echo "================================="
echo ""

BASE_URL="http://localhost:8000"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔐 Logging in as test user..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"saud@gmail.com","password":"password"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ Login failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Login successful${NC}"
echo ""

echo "📊 1. USER STATISTICS"
echo "===================="
echo ""

echo "Getting user stats..."
STATS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/achievements/stats")
echo "$STATS" | python3 -m json.tool

echo ""
echo "---"
echo ""

echo "📈 2. LEADERBOARDS"
echo "=================="
echo ""

echo "🏆 XP Leaderboard (Top 10):"
echo "----------------------------"
XP_LEADERBOARD=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/achievements/leaderboard/xp?limit=10")
echo "$XP_LEADERBOARD" | python3 -c "
import sys, json
data = json.load(sys.stdin)
leaderboard = data.get('leaderboard', [])
for idx, entry in enumerate(leaderboard[:10], 1):
    print(f'{idx}. User {entry.get(\"user_id\", \"Unknown\")[:8]}: Level {entry.get(\"level\", 0)} - {entry.get(\"total_xp\", 0)} XP')
print(f'\nYour Rank: {data.get(\"user_rank\", \"N/A\")}')
"

echo ""
echo "---"
echo ""

echo "🔥 Streak Leaderboard (Top 10):"
echo "--------------------------------"
STREAK_LEADERBOARD=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/achievements/leaderboard/streak?limit=10")
echo "$STREAK_LEADERBOARD" | python3 -c "
import sys, json
data = json.load(sys.stdin)
leaderboard = data.get('leaderboard', [])
for idx, entry in enumerate(leaderboard[:10], 1):
    print(f'{idx}. User {entry.get(\"user_id\", \"Unknown\")[:8]}: {entry.get(\"current_streak\", 0)} day streak')
print(f'\nYour Rank: {data.get(\"user_rank\", \"N/A\")}')
"

echo ""
echo "---"
echo ""

echo "🎭 Scenarios Completed Leaderboard (Top 10):"
echo "--------------------------------------------"
SCENARIOS_LEADERBOARD=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/achievements/leaderboard/scenarios?limit=10")
echo "$SCENARIOS_LEADERBOARD" | python3 -c "
import sys, json
data = json.load(sys.stdin)
leaderboard = data.get('leaderboard', [])
for idx, entry in enumerate(leaderboard[:10], 1):
    print(f'{idx}. User {entry.get(\"user_id\", \"Unknown\")[:8]}: {entry.get(\"total_scenarios_completed\", 0)} scenarios')
print(f'\nYour Rank: {data.get(\"user_rank\", \"N/A\")}')
"

echo ""
echo "---"
echo ""

echo "🏅 3. ACHIEVEMENTS"
echo "=================="
echo ""

echo "Getting achievements list..."
ACHIEVEMENTS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/achievements/list")
echo "$ACHIEVEMENTS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
achievements = data.get('achievements', [])
unlocked = [a for a in achievements if a.get('unlocked', False)]
locked = [a for a in achievements if not a.get('unlocked', False)]

print(f'Total Achievements: {len(achievements)}')
print(f'Unlocked: {len(unlocked)}')
print(f'Locked: {len(locked)}')
print()
print('Recently Unlocked:')
for a in unlocked[:5]:
    print(f'  ✓ {a.get(\"title\", \"Unknown\")} ({a.get(\"category\", \"\")})')
"

echo ""
echo "---"
echo ""

echo "📚 4. REVIEW STATISTICS"
echo "======================="
echo ""

echo "Getting review stats..."
REVIEW_STATS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/reviews/stats")
echo "$REVIEW_STATS" | python3 -m json.tool

echo ""
echo "---"
echo ""

echo "📈 5. ANALYTICS"
echo "==============="
echo ""

echo "Getting system metrics..."
METRICS=$(curl -s "$BASE_URL/api/v1/analytics/metrics")
echo "$METRICS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('System Health:')
print(f'  CPU: {data.get(\"system\", {}).get(\"cpu_percent\", 0):.1f}%')
print(f'  Memory: {data.get(\"system\", {}).get(\"memory_percent\", 0):.1f}%')
print()
print('Database:')
print(f'  Users: {data.get(\"database\", {}).get(\"users\", 0)}')
print(f'  Scenarios: {data.get(\"database\", {}).get(\"scenarios\", 0)}')
print(f'  Vocabulary: {data.get(\"database\", {}).get(\"vocabulary\", 0)}')
print()
print('AI Models:')
ai = data.get(\"ai_models\", {})
print(f'  Ollama: {\"✓\" if ai.get(\"ollama_available\") else \"✗\"}')
print(f'  Whisper: {\"✓\" if ai.get(\"whisper_available\") else \"✗\"}')
print(f'  Piper: {\"✓\" if ai.get(\"piper_available\") else \"✗\"}')
"

echo ""
echo "================================="
echo -e "${GREEN}✓ Statistics test complete!${NC}"
echo "================================="
