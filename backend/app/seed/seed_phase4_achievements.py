"""
Seed 12 new achievements for Phase 4 (total 20+)
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "german_ai"

async def seed_phase4_achievements():
    """Seed 12 new achievements"""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    print("🏆 Seeding Phase 4 Achievements...")
    
    achievements = [
        # Beginner Tier (Bronze)
        {
            "code": "first_voice",
            "name": "First Words",
            "description": "Complete your first voice conversation",
            "icon": "🎤",
            "category": "scenarios",
            "tier": "bronze",
            "xp_reward": 50,
            "conditions": [{"type": "voice_conversations", "target": 1, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 9
        },
        {
            "code": "bookworm",
            "name": "Bookworm",
            "description": "Review 10 vocabulary cards",
            "icon": "📖",
            "category": "vocabulary",
            "tier": "bronze",
            "xp_reward": 50,
            "conditions": [{"type": "cards_reviewed", "target": 10, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 10
        },
        {
            "code": "sharp_shooter",
            "name": "Sharp Shooter",
            "description": "Get 5 quiz questions correct in a row",
            "icon": "🎯",
            "category": "quiz",
            "tier": "bronze",
            "xp_reward": 75,
            "conditions": [{"type": "quiz_streak", "target": 5, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 11
        },
        {
            "code": "early_bird",
            "name": "Early Bird",
            "description": "Complete a lesson before 9 AM",
            "icon": "🌅",
            "category": "special",
            "tier": "bronze",
            "xp_reward": 50,
            "conditions": [{"type": "early_lesson", "target": 1, "current": 0, "metadata": {"time": "09:00"}}],
            "secret": False,
            "order": 12
        },
        
        # Intermediate Tier (Silver)
        {
            "code": "conversationalist",
            "name": "Conversationalist",
            "description": "Complete 10 scenarios",
            "icon": "🗣️",
            "category": "scenarios",
            "tier": "silver",
            "xp_reward": 150,
            "conditions": [{"type": "scenarios_completed", "target": 10, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 13
        },
        {
            "code": "vocabulary_master",
            "name": "Vocabulary Master",
            "description": "Learn 200 words",
            "icon": "📚",
            "category": "vocabulary",
            "tier": "silver",
            "xp_reward": 200,
            "conditions": [{"type": "words_learned", "target": 200, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 14
        },
        {
            "code": "grammar_expert",
            "name": "Grammar Expert",
            "description": "Fix 100 grammar errors",
            "icon": "📝",
            "category": "grammar",
            "tier": "silver",
            "xp_reward": 200,
            "conditions": [{"type": "grammar_errors_fixed", "target": 100, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 15
        },
        {
            "code": "fire_starter",
            "name": "Fire Starter",
            "description": "Reach a 30-day streak",
            "icon": "🔥",
            "category": "streak",
            "tier": "silver",
            "xp_reward": 250,
            "conditions": [{"type": "current_streak", "target": 30, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 16
        },
        
        # Advanced Tier (Gold)
        {
            "code": "scenario_expert",
            "name": "Scenario Expert",
            "description": "Complete all available scenarios",
            "icon": "🎭",
            "category": "scenarios",
            "tier": "gold",
            "xp_reward": 300,
            "conditions": [{"type": "all_scenarios", "target": 24, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 17
        },
        {
            "code": "perfectionist",
            "name": "Perfectionist",
            "description": "Get 100% on 10 quizzes",
            "icon": "💯",
            "category": "quiz",
            "tier": "gold",
            "xp_reward": 250,
            "conditions": [{"type": "perfect_quizzes", "target": 10, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 18
        },
        {
            "code": "champion",
            "name": "Champion",
            "description": "Reach Level 15",
            "icon": "🏆",
            "category": "special",
            "tier": "gold",
            "xp_reward": 300,
            "conditions": [{"type": "level", "target": 15, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 19
        },
        {
            "code": "all_star",
            "name": "All-Star",
            "description": "Unlock all bronze and silver achievements",
            "icon": "🌟",
            "category": "special",
            "tier": "gold",
            "xp_reward": 400,
            "conditions": [{"type": "achievements_unlocked", "target": 16, "current": 0, "metadata": {"tiers": ["bronze", "silver"]}}],
            "secret": False,
            "order": 20
        },
        
        # Special Tier (Platinum/Diamond)
        {
            "code": "diamond_mind",
            "name": "Diamond Mind",
            "description": "Reach Level 25",
            "icon": "💎",
            "category": "special",
            "tier": "platinum",
            "xp_reward": 500,
            "conditions": [{"type": "level", "target": 25, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 21
        },
        {
            "code": "speed_demon",
            "name": "Speed Demon",
            "description": "Complete a scenario in under 5 minutes",
            "icon": "🚀",
            "category": "scenarios",
            "tier": "platinum",
            "xp_reward": 300,
            "conditions": [{"type": "scenario_speed", "target": 300, "current": 0, "metadata": {"seconds": 300}}],
            "secret": False,
            "order": 22
        },
        {
            "code": "creative_writer",
            "name": "Creative Writer",
            "description": "Write 50 practice essays",
            "icon": "🎨",
            "category": "special",
            "tier": "platinum",
            "xp_reward": 400,
            "conditions": [{"type": "essays_written", "target": 50, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 23
        },
        {
            "code": "world_traveler",
            "name": "World Traveler",
            "description": "Complete scenarios in all categories",
            "icon": "🌍",
            "category": "scenarios",
            "tier": "platinum",
            "xp_reward": 500,
            "conditions": [{"type": "all_categories", "target": 10, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 24
        },
        
        # Hidden/Secret Achievements
        {
            "code": "night_owl",
            "name": "Night Owl",
            "description": "Complete a lesson after midnight",
            "icon": "🦉",
            "category": "special",
            "tier": "bronze",
            "xp_reward": 75,
            "conditions": [{"type": "late_lesson", "target": 1, "current": 0, "metadata": {"time": "00:00"}}],
            "secret": True,
            "order": 25
        },
        {
            "code": "polyglot",
            "name": "Polyglot",
            "description": "Learn 500 words",
            "icon": "🗣️",
            "category": "vocabulary",
            "tier": "diamond",
            "xp_reward": 1000,
            "conditions": [{"type": "words_learned", "target": 500, "current": 0, "metadata": {}}],
            "secret": True,
            "order": 26
        },
        {
            "code": "unstoppable",
            "name": "Unstoppable",
            "description": "Reach a 100-day streak",
            "icon": "⚡",
            "category": "streak",
            "tier": "diamond",
            "xp_reward": 1000,
            "conditions": [{"type": "current_streak", "target": 100, "current": 0, "metadata": {}}],
            "secret": True,
            "order": 27
        },
        {
            "code": "legend",
            "name": "Legend",
            "description": "Reach Level 50",
            "icon": "👑",
            "category": "special",
            "tier": "diamond",
            "xp_reward": 2000,
            "conditions": [{"type": "level", "target": 50, "current": 0, "metadata": {}}],
            "secret": True,
            "order": 28
        }
    ]
    
    # Insert achievements
    for ach in achievements:
        await db["achievements"].update_one(
            {"code": ach["code"]},
            {"$set": ach},
            upsert=True
        )
        secret_indicator = "🔒" if ach.get("secret") else ""
        print(f"  ✅ {ach['icon']} {ach['name']} ({ach['tier']}) {secret_indicator}")
    
    print(f"\n✅ Seeded {len(achievements)} new achievements")
    
    # Get total achievement count
    total = await db["achievements"].count_documents({})
    print(f"\n📈 Total achievements in database: {total}")
    
    # Count by tier
    bronze = await db["achievements"].count_documents({"tier": "bronze"})
    silver = await db["achievements"].count_documents({"tier": "silver"})
    gold = await db["achievements"].count_documents({"tier": "gold"})
    platinum = await db["achievements"].count_documents({"tier": "platinum"})
    diamond = await db["achievements"].count_documents({"tier": "diamond"})
    
    print(f"\n📊 Breakdown by tier:")
    print(f"  - Bronze: {bronze}")
    print(f"  - Silver: {silver}")
    print(f"  - Gold: {gold}")
    print(f"  - Platinum: {platinum}")
    print(f"  - Diamond: {diamond}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_phase4_achievements())
