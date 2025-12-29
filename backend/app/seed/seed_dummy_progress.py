"""
Seed dummy progress data for testing
Creates realistic user progress, achievements, and statistics
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.append(str(Path(__file__).parent.parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


async def seed_dummy_progress():
    """Seed dummy progress data for multiple users"""
    
    print("🌱 Seeding dummy progress data...")
    
    # Connect to database
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client.german_ai
    
    # Collections
    users_collection = db.users
    user_stats_collection = db.user_stats
    achievements_collection = db.achievements
    user_achievements_collection = db.user_achievements
    reviews_collection = db.review_cards
    
    # Get existing users
    users = await users_collection.find().to_list(length=100)
    
    if len(users) < 3:
        print("⚠️  Not enough users. Creating dummy users...")
        
        # Create dummy users
        dummy_users = [
            {
                "name": "Anna Schmidt",
                "email": "anna@test.com",
                "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Bst5y2",  # password: test123
                "created_at": datetime.utcnow() - timedelta(days=30)
            },
            {
                "name": "Max Müller",
                "email": "max@test.com",
                "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Bst5y2",
                "created_at": datetime.utcnow() - timedelta(days=25)
            },
            {
                "name": "Sophie Weber",
                "email": "sophie@test.com",
                "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Bst5y2",
                "created_at": datetime.utcnow() - timedelta(days=20)
            },
            {
                "name": "Lukas Fischer",
                "email": "lukas@test.com",
                "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Bst5y2",
                "created_at": datetime.utcnow() - timedelta(days=15)
            },
            {
                "name": "Emma Wagner",
                "email": "emma@test.com",
                "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIq.Bst5y2",
                "created_at": datetime.utcnow() - timedelta(days=10)
            }
        ]
        
        result = await users_collection.insert_many(dummy_users)
        print(f"✅ Created {len(result.inserted_ids)} dummy users")
        
        # Refresh users list
        users = await users_collection.find().to_list(length=100)
    
    print(f"📊 Found {len(users)} users")
    
    # Get achievements
    achievements = await achievements_collection.find().to_list(length=100)
    if len(achievements) == 0:
        print("⚠️  No achievements found. Please seed achievements first.")
        return
    
    print(f"🏆 Found {len(achievements)} achievements")
    
    # Clear existing dummy data
    await user_stats_collection.delete_many({})
    await user_achievements_collection.delete_many({})
    await reviews_collection.delete_many({})
    
    print("\n📈 Creating user statistics...")
    
    # Create user stats with varying levels of progress
    user_stats_data = []
    
    for i, user in enumerate(users[:5]):  # Top 5 users
        user_id = str(user["_id"])
        days_active = 30 - (i * 5)
        
        # Calculate realistic stats
        total_xp = random.randint(1000, 5000) - (i * 500)
        level = min(10, total_xp // 500)
        
        stats = {
            "user_id": user_id,
            "total_xp": total_xp,
            "level": level,
            "current_streak": random.randint(1, 30 - i * 3),
            "longest_streak": random.randint(10, 40 - i * 3),
            "total_scenarios_completed": random.randint(5, 20 - i),
            "total_quizzes_completed": random.randint(10, 50 - i * 5),
            "total_words_learned": random.randint(50, 300 - i * 30),
            "total_study_time_minutes": random.randint(300, 1500 - i * 150),
            "achievements_unlocked": random.randint(3, 15 - i),
            "last_active": datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
            "created_at": user.get("created_at", datetime.utcnow())
        }
        
        user_stats_data.append(stats)
        print(f"  ✅ {user['name']}: Level {level}, {total_xp} XP, {stats['current_streak']} day streak")
    
    await user_stats_collection.insert_many(user_stats_data)
    print(f"✅ Created {len(user_stats_data)} user statistics")
    
    print("\n🏆 Unlocking achievements...")
    
    # Unlock achievements for users
    user_achievements_data = []
    
    for i, user in enumerate(users[:5]):
        user_id = str(user["_id"])
        
        # Each user unlocks different achievements based on their progress
        num_achievements = random.randint(3, min(10, len(achievements)) - i)
        unlocked_achievements = random.sample(achievements, num_achievements)
        
        for achievement in unlocked_achievements:
            user_achievement = {
                "user_id": user_id,
                "achievement_id": str(achievement["_id"]),
                "unlocked_at": datetime.utcnow() - timedelta(days=random.randint(1, 20)),
                "progress": 100,
                "notified": True
            }
            user_achievements_data.append(user_achievement)
        
        print(f"  ✅ {user['name']}: Unlocked {num_achievements} achievements")
    
    if user_achievements_data:
        await user_achievements_collection.insert_many(user_achievements_data)
        print(f"✅ Created {len(user_achievements_data)} achievement unlocks")
    
    print("\n📚 Creating review cards (SRS)...")
    
    # Create review cards for users
    review_cards_data = []
    
    for i, user in enumerate(users[:5]):
        user_id = str(user["_id"])
        
        # Each user has different number of cards
        num_cards = random.randint(20, 100 - i * 10)
        
        for j in range(num_cards):
            # Random card data
            card_type = random.choice(["vocabulary", "grammar"])
            
            if card_type == "vocabulary":
                content = {
                    "word": f"Wort{j}",
                    "translation": f"Word{j}",
                    "example": f"Beispiel {j}"
                }
            else:
                content = {
                    "rule": f"Grammar Rule {j}",
                    "example": f"Example {j}"
                }
            
            # Random review state
            reviews_count = random.randint(0, 10)
            easiness_factor = round(random.uniform(1.3, 2.5), 2)
            interval = random.randint(1, 30)
            
            # Determine if card is due
            next_review = datetime.utcnow() - timedelta(days=random.randint(-5, 10))
            
            card = {
                "user_id": user_id,
                "card_type": card_type,
                "content": content,
                "easiness_factor": easiness_factor,
                "interval": interval,
                "repetitions": reviews_count,
                "next_review": next_review,
                "last_review": datetime.utcnow() - timedelta(days=interval),
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 30))
            }
            
            review_cards_data.append(card)
        
        print(f"  ✅ {user['name']}: Created {num_cards} review cards")
    
    if review_cards_data:
        await reviews_collection.insert_many(review_cards_data)
        print(f"✅ Created {len(review_cards_data)} review cards")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("📊 DUMMY DATA SUMMARY")
    print("="*60)
    
    # Leaderboard preview
    print("\n🏆 TOP 5 LEADERBOARD:")
    leaderboard = await user_stats_collection.find().sort("total_xp", -1).limit(5).to_list(length=5)
    
    for idx, stat in enumerate(leaderboard, 1):
        user = await users_collection.find_one({"_id": stat["user_id"]})
        if user:
            print(f"  {idx}. {user['name']}: Level {stat['level']} ({stat['total_xp']} XP)")
    
    # Achievement statistics
    total_unlocks = await user_achievements_collection.count_documents({})
    print(f"\n🏅 Total Achievement Unlocks: {total_unlocks}")
    
    # Review statistics
    total_reviews = await reviews_collection.count_documents({})
    due_reviews = await reviews_collection.count_documents({"next_review": {"$lte": datetime.utcnow()}})
    print(f"\n📚 Total Review Cards: {total_reviews}")
    print(f"📚 Cards Due for Review: {due_reviews}")
    
    # User statistics
    total_users = await users_collection.count_documents({})
    active_users = await user_stats_collection.count_documents({"last_active": {"$gte": datetime.utcnow() - timedelta(days=7)}})
    print(f"\n👥 Total Users: {total_users}")
    print(f"👥 Active Users (7 days): {active_users}")
    
    client.close()
    print("\n🎉 Dummy progress data seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_dummy_progress())
