"""
Setup realistic leaderboard data with proper user profiles and achievements
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv('backend/.env')

# Realistic user profiles
REALISTIC_USERS = [
    {"name": "Emma Schmidt", "email": "emma.schmidt@example.com", "level": "B1"},
    {"name": "Lukas Müller", "email": "lukas.mueller@example.com", "level": "A2"},
    {"name": "Sophie Weber", "email": "sophie.weber@example.com", "level": "B2"},
    {"name": "Max Fischer", "email": "max.fischer@example.com", "level": "A1"},
    {"name": "Anna Becker", "email": "anna.becker@example.com", "level": "B1"},
    {"name": "Felix Wagner", "email": "felix.wagner@example.com", "level": "A2"},
    {"name": "Laura Hoffmann", "email": "laura.hoffmann@example.com", "level": "C1"},
    {"name": "Jonas Schulz", "email": "jonas.schulz@example.com", "level": "B2"},
    {"name": "Mia Zimmermann", "email": "mia.zimmermann@example.com", "level": "A2"},
    {"name": "Leon Braun", "email": "leon.braun@example.com", "level": "B1"},
]

# Realistic stats profiles (varied performance levels)
STATS_PROFILES = [
    # Top performer
    {"total_xp": 5250, "level": 10, "current_streak": 28, "longest_streak": 35, "scenarios_completed": 15, "words_learned": 180, "quizzes_completed": 45, "quiz_accuracy": 0.92},
    # High achiever
    {"total_xp": 4800, "level": 9, "current_streak": 21, "longest_streak": 25, "scenarios_completed": 12, "words_learned": 150, "quizzes_completed": 38, "quiz_accuracy": 0.88},
    # Consistent learner
    {"total_xp": 4200, "level": 8, "current_streak": 18, "longest_streak": 22, "scenarios_completed": 10, "words_learned": 120, "quizzes_completed": 32, "quiz_accuracy": 0.85},
    # Active user
    {"total_xp": 3600, "level": 7, "current_streak": 14, "longest_streak": 18, "scenarios_completed": 8, "words_learned": 95, "quizzes_completed": 28, "quiz_accuracy": 0.82},
    # Regular learner
    {"total_xp": 3100, "level": 6, "current_streak": 12, "longest_streak": 15, "scenarios_completed": 7, "words_learned": 75, "quizzes_completed": 24, "quiz_accuracy": 0.79},
    # Moderate user
    {"total_xp": 2500, "level": 5, "current_streak": 9, "longest_streak": 12, "scenarios_completed": 5, "words_learned": 60, "quizzes_completed": 20, "quiz_accuracy": 0.76},
    # Beginner+
    {"total_xp": 1900, "level": 4, "current_streak": 7, "longest_streak": 10, "scenarios_completed": 4, "words_learned": 45, "quizzes_completed": 15, "quiz_accuracy": 0.73},
    # Active beginner
    {"total_xp": 1400, "level": 3, "current_streak": 5, "longest_streak": 8, "scenarios_completed": 3, "words_learned": 35, "quizzes_completed": 12, "quiz_accuracy": 0.70},
    # New learner
    {"total_xp": 950, "level": 2, "current_streak": 4, "longest_streak": 6, "scenarios_completed": 2, "words_learned": 25, "quizzes_completed": 8, "quiz_accuracy": 0.68},
    # Starter
    {"total_xp": 500, "level": 1, "current_streak": 2, "longest_streak": 3, "scenarios_completed": 1, "words_learned": 15, "quizzes_completed": 5, "quiz_accuracy": 0.65},
]

async def setup_realistic_data():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = client['german_ai']
    
    print("🧹 Cleaning up old demo data...")
    
    # Remove old demo user_stats (keep real user stats)
    real_users = await db['users'].find({}).to_list(length=100)
    real_user_ids = [str(u['_id']) for u in real_users]
    
    # Delete stats for non-existent users
    deleted = await db['user_stats'].delete_many({
        'user_id': {'$nin': real_user_ids}
    })
    print(f"✓ Removed {deleted.deleted_count} orphaned user_stats")
    
    # Delete old demo achievements
    deleted_ach = await db['user_achievements'].delete_many({
        'user_id': {'$nin': real_user_ids}
    })
    print(f"✓ Removed {deleted_ach.deleted_count} orphaned achievements")
    
    print("\n👥 Creating realistic user profiles...")
    
    created_users = []
    for i, user_profile in enumerate(REALISTIC_USERS):
        # Check if user already exists
        existing = await db['users'].find_one({'email': user_profile['email']})
        if existing:
            user_id = str(existing['_id'])
            print(f"  ✓ User exists: {user_profile['name']}")
        else:
            # Create new user
            user_doc = {
                'name': user_profile['name'],
                'email': user_profile['email'],
                'password_hash': '$2b$12$dummy_hash_for_demo_users_only',  # Dummy hash
                'level': user_profile['level'],
                'created_at': datetime.utcnow() - timedelta(days=60-i*5),
                'updated_at': datetime.utcnow()
            }
            result = await db['users'].insert_one(user_doc)
            user_id = str(result.inserted_id)
            print(f"  ✓ Created: {user_profile['name']}")
        
        created_users.append((user_id, user_profile['name']))
    
    print("\n📊 Creating user stats and achievements...")
    
    for i, (user_id, name) in enumerate(created_users):
        stats_profile = STATS_PROFILES[i]
        
        # Calculate XP to next level
        xp_to_next = (stats_profile['level'] + 1) * 500 - stats_profile['total_xp']
        
        # Create user stats
        user_stats = {
            'user_id': user_id,
            'total_xp': stats_profile['total_xp'],
            'level': stats_profile['level'],
            'xp_to_next_level': xp_to_next,
            'current_streak': stats_profile['current_streak'],
            'longest_streak': stats_profile['longest_streak'],
            'last_activity_date': datetime.utcnow() - timedelta(hours=i),
            'scenarios_completed': stats_profile['scenarios_completed'],
            'scenarios_started': stats_profile['scenarios_completed'] + 2,
            'total_scenario_time': stats_profile['scenarios_completed'] * 15,
            'words_learned': stats_profile['words_learned'],
            'words_reviewed': stats_profile['words_learned'] * 2,
            'quizzes_completed': stats_profile['quizzes_completed'],
            'quiz_accuracy': stats_profile['quiz_accuracy'],
            'perfect_quizzes': int(stats_profile['quizzes_completed'] * 0.15),
            'grammar_checks': stats_profile['quizzes_completed'] * 2,
            'grammar_errors_fixed': int(stats_profile['quizzes_completed'] * 1.5),
            'friends_count': 0,
            'challenges_won': 0,
            'created_at': datetime.utcnow() - timedelta(days=60-i*5),
            'updated_at': datetime.utcnow()
        }
        
        await db['user_stats'].update_one(
            {'user_id': user_id},
            {'$set': user_stats},
            upsert=True
        )
        
        # Create achievements based on stats
        achievements = []
        
        # Scenario achievements
        if stats_profile['scenarios_completed'] >= 1:
            achievements.append('first_scenario')
        if stats_profile['scenarios_completed'] >= 5:
            achievements.append('scenario_explorer')
        if stats_profile['scenarios_completed'] >= 10:
            achievements.append('scenario_champion')
        
        # Vocabulary achievements
        if stats_profile['words_learned'] >= 10:
            achievements.append('vocab_starter')
        if stats_profile['words_learned'] >= 50:
            achievements.append('vocab_builder')
        if stats_profile['words_learned'] >= 100:
            achievements.append('word_master')
        
        # Quiz achievements
        if stats_profile['quizzes_completed'] >= 1:
            achievements.append('quiz_beginner')
        if stats_profile['quizzes_completed'] >= 10:
            achievements.append('quiz_master')
        if user_stats['perfect_quizzes'] >= 1:
            achievements.append('quiz_perfect')
        
        # Streak achievements
        if stats_profile['current_streak'] >= 3:
            achievements.append('streak_3')
        if stats_profile['current_streak'] >= 7:
            achievements.append('streak_7')
        if stats_profile['current_streak'] >= 14:
            achievements.append('streak_14')
        if stats_profile['current_streak'] >= 30:
            achievements.append('streak_30')
        
        # Grammar achievements
        if user_stats['grammar_checks'] >= 1:
            achievements.append('grammar_first')
        if user_stats['grammar_errors_fixed'] >= 10:
            achievements.append('grammar_fixer_10')
        
        # Create achievement records
        for ach_code in achievements:
            await db['user_achievements'].update_one(
                {'user_id': user_id, 'achievement_code': ach_code},
                {'$set': {
                    'user_id': user_id,
                    'achievement_code': ach_code,
                    'unlocked': True,
                    'progress': 100,
                    'conditions_met': ['auto_generated'],
                    'unlocked_at': datetime.utcnow() - timedelta(days=i*2),
                    'created_at': datetime.utcnow() - timedelta(days=i*2),
                    'updated_at': datetime.utcnow() - timedelta(days=i*2)
                }},
                upsert=True
            )
        
        print(f"  ✓ {name}: {stats_profile['total_xp']} XP, Level {stats_profile['level']}, {len(achievements)} achievements")
    
    print("\n📈 Leaderboard Summary:")
    
    # Get top 5 by XP
    top_xp = await db['user_stats'].find({}).sort('total_xp', -1).limit(5).to_list(length=5)
    print("\n🏆 Top 5 by XP:")
    for i, stat in enumerate(top_xp):
        user = await db['users'].find_one({'_id': stat['user_id']})
        name = user['name'] if user else 'Unknown'
        print(f"  {i+1}. {name}: {stat['total_xp']} XP")
    
    # Get top 5 by streak
    top_streak = await db['user_stats'].find({}).sort('current_streak', -1).limit(5).to_list(length=5)
    print("\n🔥 Top 5 by Streak:")
    for i, stat in enumerate(top_streak):
        user = await db['users'].find_one({'_id': stat['user_id']})
        name = user['name'] if user else 'Unknown'
        print(f"  {i+1}. {name}: {stat['current_streak']} days")
    
    # Get top 5 by scenarios
    top_scenarios = await db['user_stats'].find({}).sort('scenarios_completed', -1).limit(5).to_list(length=5)
    print("\n🎭 Top 5 by Scenarios:")
    for i, stat in enumerate(top_scenarios):
        user = await db['users'].find_one({'_id': stat['user_id']})
        name = user['name'] if user else 'Unknown'
        print(f"  {i+1}. {name}: {stat['scenarios_completed']} completed")
    
    # Count total achievements
    total_achievements = await db['user_achievements'].count_documents({})
    print(f"\n✨ Total achievements unlocked: {total_achievements}")
    
    print("\n✅ Realistic leaderboard data setup complete!")

if __name__ == "__main__":
    asyncio.run(setup_realistic_data())
