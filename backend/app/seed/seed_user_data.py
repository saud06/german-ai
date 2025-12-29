"""
Seed realistic user data for dashboard display
"""
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "german_ai"

async def seed_user_data():
    """Seed comprehensive user data"""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    # Use existing test user
    user_id = "68b9b8daf5d489d0362b4506"
    
    print("🌱 Seeding user data...")
    
    # 1. Update user stats with realistic data
    print("📊 Updating user statistics...")
    await db["user_stats"].update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "total_xp": 4250,
                "level": 8,
                "xp_to_next_level": 150,
                "current_streak": 13,
                "longest_streak": 36,
                "last_activity_date": datetime.utcnow().isoformat(),
                
                # Scenarios
                "scenarios_completed": 7,
                "scenarios_started": 10,
                "total_scenario_time": 3420,  # 57 minutes
                
                # Vocabulary
                "words_learned": 145,
                "words_reviewed": 423,
                
                # Quizzes
                "quizzes_completed": 28,
                "quiz_accuracy": 82.5,
                "perfect_quizzes": 8,
                
                # Grammar
                "grammar_checks": 56,
                "grammar_errors_fixed": 34,
                
                # Social (for later)
                "friends_count": 0,
                "challenges_won": 0,
                
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    # 2. Seed achievements
    print("🏆 Seeding achievements...")
    
    achievements = [
        {
            "code": "first_steps",
            "name": "First Steps",
            "description": "Complete your first lesson",
            "icon": "🎯",
            "category": "scenarios",
            "tier": "bronze",
            "xp_reward": 50,
            "conditions": [{"type": "scenarios_completed", "target": 1, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 1
        },
        {
            "code": "word_collector",
            "name": "Word Collector",
            "description": "Learn 100 new words",
            "icon": "📚",
            "category": "vocabulary",
            "tier": "silver",
            "xp_reward": 200,
            "conditions": [{"type": "words_learned", "target": 100, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 2
        },
        {
            "code": "scenario_master",
            "name": "Scenario Master",
            "description": "Complete 5 scenarios",
            "icon": "🎭",
            "category": "scenarios",
            "tier": "gold",
            "xp_reward": 300,
            "conditions": [{"type": "scenarios_completed", "target": 5, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 3
        },
        {
            "code": "quiz_champion",
            "name": "Quiz Champion",
            "description": "Complete 20 quizzes",
            "icon": "🧠",
            "category": "quiz",
            "tier": "silver",
            "xp_reward": 250,
            "conditions": [{"type": "quizzes_completed", "target": 20, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 4
        },
        {
            "code": "perfect_score",
            "name": "Perfect Score",
            "description": "Get 100% on a quiz",
            "icon": "⭐",
            "category": "quiz",
            "tier": "bronze",
            "xp_reward": 100,
            "conditions": [{"type": "perfect_quizzes", "target": 1, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 5
        },
        {
            "code": "week_warrior",
            "name": "Week Warrior",
            "description": "Maintain a 7-day streak",
            "icon": "🔥",
            "category": "streak",
            "tier": "gold",
            "xp_reward": 150,
            "conditions": [{"type": "current_streak", "target": 7, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 6
        },
        {
            "code": "grammar_guru",
            "name": "Grammar Guru",
            "description": "Fix 50 grammar errors",
            "icon": "✍️",
            "category": "grammar",
            "tier": "platinum",
            "xp_reward": 200,
            "conditions": [{"type": "grammar_errors_fixed", "target": 50, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 7
        },
        {
            "code": "conversation_starter",
            "name": "Conversation Starter",
            "description": "Complete your first AI conversation",
            "icon": "💬",
            "category": "scenarios",
            "tier": "bronze",
            "xp_reward": 100,
            "conditions": [{"type": "scenarios_completed", "target": 1, "current": 0, "metadata": {}}],
            "secret": False,
            "order": 8
        }
    ]
    
    # Insert achievements
    for ach in achievements:
        await db["achievements"].update_one(
            {"code": ach["code"]},
            {"$set": ach},
            upsert=True
        )
    
    # 3. Unlock some achievements for the user
    print("🎖️ Unlocking user achievements...")
    
    unlocked_achievements = [
        {
            "user_id": user_id,
            "achievement_code": "first_steps",
            "code": "first_steps",
            "unlocked": True,
            "progress": 1,
            "unlocked_at": (datetime.utcnow() - timedelta(days=30)).isoformat()
        },
        {
            "user_id": user_id,
            "achievement_code": "word_collector",
            "code": "word_collector",
            "unlocked": True,
            "progress": 145,
            "unlocked_at": (datetime.utcnow() - timedelta(days=15)).isoformat()
        },
        {
            "user_id": user_id,
            "achievement_code": "scenario_master",
            "code": "scenario_master",
            "unlocked": True,
            "progress": 7,
            "unlocked_at": (datetime.utcnow() - timedelta(days=5)).isoformat()
        },
        {
            "user_id": user_id,
            "achievement_code": "quiz_champion",
            "code": "quiz_champion",
            "unlocked": True,
            "progress": 28,
            "unlocked_at": (datetime.utcnow() - timedelta(days=3)).isoformat()
        },
        {
            "user_id": user_id,
            "achievement_code": "perfect_score",
            "code": "perfect_score",
            "unlocked": True,
            "progress": 8,
            "unlocked_at": (datetime.utcnow() - timedelta(days=10)).isoformat()
        },
        {
            "user_id": user_id,
            "achievement_code": "week_warrior",
            "code": "week_warrior",
            "unlocked": True,
            "progress": 13,
            "unlocked_at": (datetime.utcnow() - timedelta(days=6)).isoformat()
        },
        {
            "user_id": user_id,
            "achievement_code": "conversation_starter",
            "code": "conversation_starter",
            "unlocked": True,
            "progress": 7,
            "unlocked_at": (datetime.utcnow() - timedelta(days=25)).isoformat()
        },
        # In progress
        {
            "user_id": user_id,
            "achievement_code": "grammar_guru",
            "code": "grammar_guru",
            "unlocked": False,
            "progress": 34,
            "unlocked_at": None
        }
    ]
    
    for ach in unlocked_achievements:
        await db["user_achievements"].update_one(
            {"user_id": user_id, "achievement_code": ach["achievement_code"]},
            {"$set": ach},
            upsert=True
        )
    
    # 4. Create some leaderboard entries
    print("🏅 Creating leaderboard data...")
    
    # Create some dummy users for leaderboard
    leaderboard_users = [
        {"user_id": user_id, "name": "Saud", "total_xp": 4250, "level": 8, "current_streak": 13},
        {"user_id": "user_2", "name": "Anna Schmidt", "total_xp": 5120, "level": 9, "current_streak": 21},
        {"user_id": "user_3", "name": "Max Müller", "total_xp": 3890, "level": 7, "current_streak": 8},
        {"user_id": "user_4", "name": "Sophie Weber", "total_xp": 4680, "level": 8, "current_streak": 15},
        {"user_id": "user_5", "name": "Leon Fischer", "total_xp": 3200, "level": 6, "current_streak": 5},
        {"user_id": "user_6", "name": "Emma Wagner", "total_xp": 4950, "level": 9, "current_streak": 18},
        {"user_id": "user_7", "name": "Noah Becker", "total_xp": 2850, "level": 5, "current_streak": 3},
        {"user_id": "user_8", "name": "Mia Hoffmann", "total_xp": 4100, "level": 7, "current_streak": 12},
    ]
    
    for user in leaderboard_users:
        await db["user_stats"].update_one(
            {"user_id": user["user_id"]},
            {
                "$set": {
                    "user_id": user["user_id"],
                    "total_xp": user["total_xp"],
                    "level": user["level"],
                    "current_streak": user["current_streak"],
                    "longest_streak": user["current_streak"] + random.randint(5, 20),
                    "scenarios_completed": random.randint(3, 15),
                    "words_learned": random.randint(50, 200),
                    "quizzes_completed": random.randint(10, 40),
                    "quiz_accuracy": round(random.uniform(70, 95), 1),
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        # Also create user profile
        if user["user_id"] != user_id:
            await db["users"].update_one(
                {"_id": user["user_id"]},
                {
                    "$set": {
                        "_id": user["user_id"],
                        "name": user["name"],
                        "email": f"{user['name'].lower().replace(' ', '.')}@example.com",
                        "level": "A1",
                        "created_at": datetime.utcnow() - timedelta(days=random.randint(10, 60))
                    }
                },
                upsert=True
            )
    
    print("✅ User data seeded successfully!")
    print(f"\n📊 Summary:")
    print(f"  - User stats updated")
    print(f"  - {len(achievements)} achievements created")
    print(f"  - {len(unlocked_achievements)} achievements unlocked for user")
    print(f"  - {len(leaderboard_users)} leaderboard entries created")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_user_data())
