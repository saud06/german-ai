"""
Seed achievement definitions into the database
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import settings
from app.models.achievement import ACHIEVEMENT_DEFINITIONS

async def seed_achievements():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]
    
    print("🏆 Seeding Achievement Definitions...")
    
    # Clear existing achievements
    await db.achievements.delete_many({})
    
    # Insert all achievement definitions
    achievements = []
    for ach_def in ACHIEVEMENT_DEFINITIONS:
        achievements.append(ach_def)
    
    if achievements:
        result = await db.achievements.insert_many(achievements)
        print(f"✅ Inserted {len(result.inserted_ids)} achievements")
    
    # Group by category
    categories = {}
    for ach in achievements:
        cat = ach['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(ach)
    
    print("\n📊 Achievement Breakdown:")
    for cat, achs in categories.items():
        print(f"   {cat.title()}: {len(achs)} achievements")
        for ach in achs:
            print(f"      {ach['icon']} {ach['name']} ({ach['tier']}) - {ach['xp_reward']} XP")
    
    print(f"\n🎯 Total: {len(achievements)} achievements")
    print(f"💰 Total XP available: {sum(a['xp_reward'] for a in achievements)} XP")
    
    print("\n✅ Achievement system ready!")

if __name__ == "__main__":
    asyncio.run(seed_achievements())
