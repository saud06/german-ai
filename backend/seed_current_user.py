"""
Seed achievement data for the currently logged-in user
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
import sys
from dotenv import load_dotenv

load_dotenv('backend/.env')

async def seed_for_user(user_email: str):
    # Connect to MongoDB
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongodb_uri)
    db = client['german_ai']
    
    print(f"🌱 Seeding achievement data for {user_email}...")
    
    # Find user by email
    user = await db['users'].find_one({"email": user_email})
    if not user:
        print(f"❌ User with email {user_email} not found.")
        return
    
    user_id = str(user['_id'])
    print(f"✓ Found user: {user_id}")
    
    # Create user stats with sample data
    user_stats = {
        "user_id": user_id,
        "total_xp": 1250,
        "level": 5,
        "xp_to_next_level": 500,
        "current_streak": 7,
        "longest_streak": 12,
        "last_activity_date": datetime.utcnow(),
        "scenarios_completed": 3,
        "scenarios_started": 5,
        "total_scenario_time": 45,
        "words_learned": 25,
        "words_reviewed": 50,
        "quizzes_completed": 8,
        "quiz_accuracy": 0.78,
        "perfect_quizzes": 2,
        "grammar_checks": 15,
        "grammar_errors_fixed": 12,
        "friends_count": 0,
        "challenges_won": 0,
        "created_at": datetime.utcnow() - timedelta(days=30),
        "updated_at": datetime.utcnow()
    }
    
    # Upsert user stats
    await db['user_stats'].update_one(
        {"user_id": user_id},
        {"$set": user_stats},
        upsert=True
    )
    print("✓ Created user stats")
    
    # Unlock some achievements
    achievements_to_unlock = [
        {
            "user_id": user_id,
            "achievement_code": "first_scenario",
            "unlocked": True,
            "progress": 100,
            "conditions_met": ["scenarios_completed"],
            "unlocked_at": datetime.utcnow() - timedelta(days=25),
            "created_at": datetime.utcnow() - timedelta(days=25),
            "updated_at": datetime.utcnow() - timedelta(days=25)
        },
        {
            "user_id": user_id,
            "achievement_code": "vocab_starter",
            "unlocked": True,
            "progress": 100,
            "conditions_met": ["words_learned"],
            "unlocked_at": datetime.utcnow() - timedelta(days=20),
            "created_at": datetime.utcnow() - timedelta(days=20),
            "updated_at": datetime.utcnow() - timedelta(days=20)
        },
        {
            "user_id": user_id,
            "achievement_code": "quiz_beginner",
            "unlocked": True,
            "progress": 100,
            "conditions_met": ["quizzes_completed"],
            "unlocked_at": datetime.utcnow() - timedelta(days=18),
            "created_at": datetime.utcnow() - timedelta(days=18),
            "updated_at": datetime.utcnow() - timedelta(days=18)
        },
        {
            "user_id": user_id,
            "achievement_code": "quiz_perfect",
            "unlocked": True,
            "progress": 100,
            "conditions_met": ["perfect_quizzes"],
            "unlocked_at": datetime.utcnow() - timedelta(days=15),
            "created_at": datetime.utcnow() - timedelta(days=15),
            "updated_at": datetime.utcnow() - timedelta(days=15)
        },
        {
            "user_id": user_id,
            "achievement_code": "streak_3",
            "unlocked": True,
            "progress": 100,
            "conditions_met": ["current_streak"],
            "unlocked_at": datetime.utcnow() - timedelta(days=10),
            "created_at": datetime.utcnow() - timedelta(days=10),
            "updated_at": datetime.utcnow() - timedelta(days=10)
        },
        {
            "user_id": user_id,
            "achievement_code": "streak_7",
            "unlocked": True,
            "progress": 100,
            "conditions_met": ["current_streak"],
            "unlocked_at": datetime.utcnow() - timedelta(days=3),
            "created_at": datetime.utcnow() - timedelta(days=3),
            "updated_at": datetime.utcnow() - timedelta(days=3)
        },
        {
            "user_id": user_id,
            "achievement_code": "grammar_first",
            "unlocked": True,
            "progress": 100,
            "conditions_met": ["grammar_checks"],
            "unlocked_at": datetime.utcnow() - timedelta(days=12),
            "created_at": datetime.utcnow() - timedelta(days=12),
            "updated_at": datetime.utcnow() - timedelta(days=12)
        },
        {
            "user_id": user_id,
            "achievement_code": "grammar_fixer_10",
            "unlocked": True,
            "progress": 100,
            "conditions_met": ["grammar_errors_fixed"],
            "unlocked_at": datetime.utcnow() - timedelta(days=5),
            "created_at": datetime.utcnow() - timedelta(days=5),
            "updated_at": datetime.utcnow() - timedelta(days=5)
        }
    ]
    
    for achievement in achievements_to_unlock:
        await db['user_achievements'].update_one(
            {
                "user_id": user_id,
                "achievement_code": achievement["achievement_code"]
            },
            {"$set": achievement},
            upsert=True
        )
    
    print(f"✓ Unlocked {len(achievements_to_unlock)} achievements")
    
    print("\n✅ Achievement data seeded successfully!")
    print(f"\n📊 Summary:")
    print(f"   - User: {user_email}")
    print(f"   - User ID: {user_id}")
    print(f"   - User XP: {user_stats['total_xp']}")
    print(f"   - Level: {user_stats['level']}")
    print(f"   - Current Streak: {user_stats['current_streak']} days")
    print(f"   - Scenarios Completed: {user_stats['scenarios_completed']}")
    print(f"   - Words Learned: {user_stats['words_learned']}")
    print(f"   - Quizzes Completed: {user_stats['quizzes_completed']}")
    print(f"   - Achievements Unlocked: {len(achievements_to_unlock)}")

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "saud@gmail.com"
    asyncio.run(seed_for_user(email))
