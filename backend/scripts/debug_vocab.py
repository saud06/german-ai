"""
Debug vocabulary level detection
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, '/app')

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "german_learning")

async def debug():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    print("=" * 60)
    print("VOCABULARY DEBUG")
    print("=" * 60)
    
    # Clear cache
    result = await db.ai_vocab_cache.delete_many({})
    print(f"\n✅ Cleared {result.deleted_count} cached vocabulary entries")
    
    # Check seed_words by level
    print("\n📚 Seed Words by Level:")
    pipeline = [
        {"$group": {"_id": "$level", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    levels = await db.seed_words.aggregate(pipeline).to_list(100)
    for level in levels:
        print(f"   {level['_id']}: {level['count']} words")
    
    # Check a sample user's journey
    print("\n👤 Sample User Journey:")
    user = await db.users.find_one({"email": "saud@gmail.com"})
    if user:
        journeys_data = user.get("learning_journeys", {})
        active_id = journeys_data.get("active_journey_id")
        print(f"   Active Journey ID: {active_id}")
        
        if active_id:
            for journey in journeys_data.get("journeys", []):
                if journey.get("id") == active_id:
                    print(f"   Journey Type: {journey.get('type')}")
                    print(f"   Journey Level: {journey.get('level')}")
                    print(f"   Is Primary: {journey.get('is_primary')}")
    else:
        print("   User not found")
    
    # Test level detection
    print("\n🔍 Testing get_user_journey_level:")
    if user:
        from app.utils.journey_utils import get_user_journey_level
        user_id = str(user["_id"])
        level = await get_user_journey_level(db, user_id)
        print(f"   Detected Level: {level}")
    
    print("\n" + "=" * 60)
    print("✅ Debug complete - cache cleared, ready for fresh test")
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug())
