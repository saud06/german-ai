#!/bin/bash

# Deploy Vocabulary System Fix
# This script seeds the vocabulary sets and restarts the backend

set -e

echo "========================================="
echo "Vocabulary System Fix - Deployment"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

cd "$(dirname "$0")"

echo "📦 Step 1: Seeding vocabulary sets..."
cd backend
source venv/bin/activate
python scripts/seed_vocab_sets.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Vocabulary sets seeded successfully${NC}"
else
    echo "❌ Failed to seed vocabulary sets"
    exit 1
fi

echo ""
echo "🔄 Step 2: Restarting backend..."
# Kill existing backend process
pkill -f "uvicorn app.main:app" || true
sleep 2

# Start backend
nohup uvicorn app.main:app --reload --port 8000 > /tmp/backend-native.log 2>&1 &
BACKEND_PID=$!

echo "  Backend PID: $BACKEND_PID"
echo "  Logs: tail -f /tmp/backend-native.log"

# Wait for backend to start
echo "  Waiting for backend to start..."
sleep 5

# Test backend health
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo "❌ Backend failed to start"
    echo "Check logs: tail -f /tmp/backend-native.log"
    exit 1
fi

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "✅ Vocabulary sets created and linked to locations"
echo "✅ 115+ words seeded across A1-C2 levels"
echo "✅ Backend restarted with new endpoints"
echo ""
echo "📝 Next Steps:"
echo "  1. Frontend changes still needed (see VOCABULARY_FIX_SUMMARY.md)"
echo "  2. Test vocabulary sets: http://localhost:8000/api/v1/vocab/sets/{id}"
echo "  3. Check backend logs: tail -f /tmp/backend-native.log"
echo ""
echo "📚 Documentation:"
echo "  - VOCABULARY_SYSTEM_REDESIGN.md - Complete redesign plan"
echo "  - VOCABULARY_FIX_SUMMARY.md - Implementation summary"
echo ""
