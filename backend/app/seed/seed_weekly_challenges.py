"""
Seed weekly challenges for gamification
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import date, timedelta
import os


async def seed_weekly_challenges():
    """Seed initial weekly challenges"""
    
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_url)
    db = client["german_ai"]
    
    print("🎯 Seeding weekly challenges...")
    
    # Calculate this week's dates
    today = date.today()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)
    
    challenges = [
        {
            "id": "challenge_scenarios_5",
            "title": "Scenario Master",
            "description": "Complete 5 conversation scenarios this week",
            "challenge_type": "scenarios",
            "target": 5,
            "xp_reward": 200,
            "coin_reward": 100,
            "gem_reward": 5,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "active": True
        },
        {
            "id": "challenge_quizzes_10",
            "title": "Quiz Champion",
            "description": "Complete 10 quizzes this week",
            "challenge_type": "quizzes",
            "target": 10,
            "xp_reward": 250,
            "coin_reward": 150,
            "gem_reward": 10,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "active": True
        },
        {
            "id": "challenge_reviews_20",
            "title": "Review Warrior",
            "description": "Complete 20 vocabulary reviews this week",
            "challenge_type": "reviews",
            "target": 20,
            "xp_reward": 150,
            "coin_reward": 75,
            "gem_reward": 3,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "active": True
        },
        {
            "id": "challenge_lessons_15",
            "title": "Dedicated Learner",
            "description": "Complete 15 lessons this week",
            "challenge_type": "lessons",
            "target": 15,
            "xp_reward": 300,
            "coin_reward": 200,
            "gem_reward": 15,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "active": True
        },
        {
            "id": "challenge_words_50",
            "title": "Vocabulary Builder",
            "description": "Learn 50 new words this week",
            "challenge_type": "words",
            "target": 50,
            "xp_reward": 400,
            "coin_reward": 250,
            "gem_reward": 20,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "active": True
        },
        {
            "id": "challenge_streak_7",
            "title": "Consistency King",
            "description": "Maintain a 7-day streak",
            "challenge_type": "streak",
            "target": 7,
            "xp_reward": 500,
            "coin_reward": 300,
            "gem_reward": 25,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "active": True
        }
    ]
    
    # Clear existing challenges for this week
    await db.weekly_challenges.delete_many({
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    })
    
    # Insert new challenges
    result = await db.weekly_challenges.insert_many(challenges)
    
    print(f"✅ Seeded {len(result.inserted_ids)} weekly challenges")
    print(f"   Week: {start_date} to {end_date}")
    
    for challenge in challenges:
        print(f"   - {challenge['title']}: {challenge['target']} {challenge['challenge_type']}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_weekly_challenges())
