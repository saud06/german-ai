"""
Seed Chapters 2 & 3 for Learning Path
Chapter 2: Building Connections (A1)
Chapter 3: Daily Life (A2)
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import settings

async def seed_chapters():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]
    
    print("🌱 Seeding Chapters 2 & 3...")
    
    # Get existing scenarios to link
    scenarios = await db.scenarios.find().to_list(length=100)
    beginner_scenarios = [s for s in scenarios if s.get('difficulty') == 'beginner']
    intermediate_scenarios = [s for s in scenarios if s.get('difficulty') == 'intermediate']
    advanced_scenarios = [s for s in scenarios if s.get('difficulty') == 'advanced']
    
    # ========================================================================
    # CHAPTER 2: BUILDING CONNECTIONS (A1)
    # ========================================================================
    
    chapter2_id = ObjectId()
    chapter2 = {
        "_id": chapter2_id,
        "chapter": 2,
        "level": "A1",
        "title": "Building Connections",
        "description": "Make friends, explore the city, and start building your life in Germany.",
        "story": """You've survived your first week! Now it's time to make connections.
        Meet your neighbors, explore Berlin's neighborhoods, and start feeling at home.
        Your German is improving, and people are starting to understand you better!""",
        "image": "/images/chapters/chapter2-connections.jpg",
        "locations": [],  # Will add location IDs
        "characters": [],  # Will add character IDs
        "estimated_hours": 25,
        "unlock_requirements": {
            "chapter_progress": 80,  # 80% of Chapter 1
            "min_xp": 800,
            "min_level": 2
        },
        "completion_reward": {
            "xp": 1500,
            "badge": "Social Butterfly",
            "unlock": "Chapter 3",
            "housing_upgrade": "shared_flat",
            "career_upgrade": None,
            "relationship_boost": None
        },
        "created_at": datetime.utcnow()
    }
    
    # Chapter 2 Characters
    chapter2_characters = [
        {
            "_id": ObjectId(),
            "name": "Emma",
            "role": "Neighbor",
            "personality": "Friendly and outgoing",
            "age": 28,
            "occupation": "Graphic Designer",
            "avatar": "/images/characters/emma.jpg",
            "voice_id": "de_DE-eva_k-x_low",
            "appears_in_chapters": [2, 3, 4],
            "relationship_levels": {
                "0": "New neighbor",
                "3": "Friendly neighbor",
                "5": "Good friend",
                "8": "Best friend"
            },
            "conversation_topics": {
                "0": ["greetings", "weather", "neighborhood"],
                "3": ["hobbies", "work", "weekend_plans"],
                "5": ["personal_life", "advice", "deep_conversations"],
                "8": ["secrets", "life_goals", "support"]
            },
            "ai_prompt": "You are Emma, a friendly 28-year-old graphic designer living in Berlin. You're outgoing, creative, and love helping newcomers feel at home. You enjoy art, coffee, and exploring the city.",
            "backstory": "Emma moved to Berlin 5 years ago from Munich. She knows the city well and loves introducing people to hidden gems.",
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Lukas",
            "role": "Gym Buddy",
            "personality": "Energetic and motivating",
            "age": 32,
            "occupation": "Personal Trainer",
            "avatar": "/images/characters/lukas.jpg",
            "voice_id": "de_DE-thorsten-low",
            "appears_in_chapters": [2, 3, 4, 5],
            "relationship_levels": {
                "0": "Gym acquaintance",
                "3": "Workout partner",
                "5": "Friend",
                "8": "Close friend"
            },
            "conversation_topics": {
                "0": ["fitness", "gym", "health"],
                "3": ["sports", "nutrition", "lifestyle"],
                "5": ["personal_goals", "challenges", "motivation"],
                "8": ["life_philosophy", "deep_talks", "support"]
            },
            "ai_prompt": "You are Lukas, an energetic 32-year-old personal trainer. You're motivating, positive, and passionate about health and fitness. You speak clearly and encourage others.",
            "backstory": "Lukas is a Berlin native who loves helping people achieve their fitness goals. He's patient with beginners and speaks slowly to help language learners.",
            "created_at": datetime.utcnow()
        }
    ]
    
    # Insert Chapter 2 characters
    await db.characters.insert_many(chapter2_characters)
    chapter2["characters"] = [str(c["_id"]) for c in chapter2_characters]
    print(f"✅ Created {len(chapter2_characters)} characters for Chapter 2")
    
    # Chapter 2 Locations
    chapter2_locations = [
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter2_id),
            "name": "Neighbor's Apartment",
            "type": "scenario",
            "description": "Meet your friendly neighbor Emma and make your first German friend.",
            "image": "/images/locations/apartment.jpg",
            "position": {"x": 150, "y": 100},
            "scenarios": [str(beginner_scenarios[i % len(beginner_scenarios)]["_id"]) for i in range(2)],
            "unlock_requirements": {
                "chapter_progress": 0,
                "previous_location": None,
                "min_xp": 0,
                "min_level": 0,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [str(chapter2_characters[0]["_id"])],
            "estimated_minutes": 20,
            "rewards": {
                "xp": 150,
                "badge": None,
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": {"emma": 2}
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter2_id),
            "name": "Fitness Studio",
            "type": "scenario",
            "description": "Join a gym and practice German while working out.",
            "image": "/images/locations/gym.jpg",
            "position": {"x": 300, "y": 150},
            "scenarios": [str(beginner_scenarios[i % len(beginner_scenarios)]["_id"]) for i in range(2, 4)],
            "unlock_requirements": {
                "chapter_progress": 25,
                "previous_location": None,
                "min_xp": 100,
                "min_level": 0,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [str(chapter2_characters[1]["_id"])],
            "estimated_minutes": 25,
            "rewards": {
                "xp": 200,
                "badge": None,
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": {"lukas": 2}
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter2_id),
            "name": "Spätkauf (Late Night Shop)",
            "type": "scenario",
            "description": "Buy snacks and drinks at a typical Berlin corner shop.",
            "image": "/images/locations/spaetkauf.jpg",
            "position": {"x": 200, "y": 250},
            "scenarios": [str(beginner_scenarios[i % len(beginner_scenarios)]["_id"]) for i in range(4, 6)],
            "unlock_requirements": {
                "chapter_progress": 50,
                "previous_location": None,
                "min_xp": 300,
                "min_level": 0,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [],
            "estimated_minutes": 15,
            "rewards": {
                "xp": 150,
                "badge": None,
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": None
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter2_id),
            "name": "Mauerpark Flea Market",
            "type": "scenario",
            "description": "Explore Berlin's famous flea market and practice bargaining in German.",
            "image": "/images/locations/flea-market.jpg",
            "position": {"x": 400, "y": 200},
            "scenarios": [str(intermediate_scenarios[i % len(intermediate_scenarios)]["_id"]) for i in range(2)],
            "unlock_requirements": {
                "chapter_progress": 75,
                "previous_location": None,
                "min_xp": 600,
                "min_level": 2,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [],
            "estimated_minutes": 30,
            "rewards": {
                "xp": 250,
                "badge": "Bargain Hunter",
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": None
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter2_id),
            "name": "Volkshochschule (Language School)",
            "type": "practice",
            "description": "Enroll in a German course and meet other learners.",
            "image": "/images/locations/language-school.jpg",
            "position": {"x": 250, "y": 350},
            "scenarios": [str(intermediate_scenarios[i % len(intermediate_scenarios)]["_id"]) for i in range(2, 4)],
            "unlock_requirements": {
                "chapter_progress": 90,
                "previous_location": None,
                "min_xp": 800,
                "min_level": 2,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [],
            "estimated_minutes": 40,
            "rewards": {
                "xp": 300,
                "badge": "Dedicated Learner",
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": None
            },
            "created_at": datetime.utcnow()
        }
    ]
    
    await db.locations.insert_many(chapter2_locations)
    chapter2["locations"] = [str(loc["_id"]) for loc in chapter2_locations]
    print(f"✅ Created {len(chapter2_locations)} locations for Chapter 2")
    
    # Insert Chapter 2
    await db.learning_paths.insert_one(chapter2)
    print(f"✅ Created Chapter 2: {chapter2['title']}")
    
    # ========================================================================
    # CHAPTER 3: DAILY LIFE (A2)
    # ========================================================================
    
    chapter3_id = ObjectId()
    chapter3 = {
        "_id": chapter3_id,
        "chapter": 3,
        "level": "A2",
        "title": "Daily Life",
        "description": "Navigate everyday situations like banking, healthcare, and work.",
        "story": """You're settling into German life! Time to handle adult responsibilities.
        Open a bank account, visit a doctor, and maybe even look for a job.
        Your German is getting better every day!""",
        "image": "/images/chapters/chapter3-daily-life.jpg",
        "locations": [],
        "characters": [],
        "estimated_hours": 30,
        "unlock_requirements": {
            "chapter_progress": 100,  # Complete Chapter 2
            "min_xp": 2000,
            "min_level": 3
        },
        "completion_reward": {
            "xp": 2000,
            "badge": "Independent",
            "unlock": "Chapter 4",
            "housing_upgrade": "apartment",
            "career_upgrade": "intern",
            "relationship_boost": None
        },
        "created_at": datetime.utcnow()
    }
    
    # Chapter 3 Characters
    chapter3_characters = [
        {
            "_id": ObjectId(),
            "name": "Frau Schmidt",
            "role": "Bank Employee",
            "personality": "Professional and helpful",
            "age": 45,
            "occupation": "Bank Advisor",
            "avatar": "/images/characters/frau-schmidt.jpg",
            "voice_id": "de_DE-eva_k-x_low",
            "appears_in_chapters": [3],
            "relationship_levels": {
                "0": "Bank customer",
                "3": "Trusted advisor"
            },
            "conversation_topics": {
                "0": ["banking", "accounts", "services"],
                "3": ["financial_advice", "investments", "loans"]
            },
            "ai_prompt": "You are Frau Schmidt, a professional 45-year-old bank advisor. You're patient, clear, and helpful with customers, especially those learning German.",
            "backstory": "Frau Schmidt has worked at the bank for 20 years and enjoys helping international customers navigate German banking.",
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Dr. Weber",
            "role": "Doctor",
            "personality": "Caring and thorough",
            "age": 50,
            "occupation": "General Practitioner",
            "avatar": "/images/characters/dr-weber.jpg",
            "voice_id": "de_DE-thorsten-low",
            "appears_in_chapters": [3, 4, 5],
            "relationship_levels": {
                "0": "Patient",
                "3": "Regular patient"
            },
            "conversation_topics": {
                "0": ["health", "symptoms", "treatment"],
                "3": ["wellness", "prevention", "lifestyle"]
            },
            "ai_prompt": "You are Dr. Weber, a caring 50-year-old doctor. You speak clearly and patiently, especially with non-native speakers. You're thorough and caring.",
            "backstory": "Dr. Weber has many international patients and is experienced in communicating medical information clearly in German.",
            "created_at": datetime.utcnow()
        }
    ]
    
    await db.characters.insert_many(chapter3_characters)
    chapter3["characters"] = [str(c["_id"]) for c in chapter3_characters]
    print(f"✅ Created {len(chapter3_characters)} characters for Chapter 3")
    
    # Chapter 3 Locations
    chapter3_locations = [
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter3_id),
            "name": "Deutsche Bank",
            "type": "scenario",
            "description": "Open your first German bank account.",
            "image": "/images/locations/bank.jpg",
            "position": {"x": 150, "y": 100},
            "scenarios": [str(intermediate_scenarios[i % len(intermediate_scenarios)]["_id"]) for i in range(4, 6)],
            "unlock_requirements": {
                "chapter_progress": 0,
                "previous_location": None,
                "min_xp": 0,
                "min_level": 0,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [str(chapter3_characters[0]["_id"])],
            "estimated_minutes": 30,
            "rewards": {
                "xp": 250,
                "badge": None,
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": None
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter3_id),
            "name": "Arztpraxis (Doctor's Office)",
            "type": "scenario",
            "description": "Visit a doctor and describe your symptoms in German.",
            "image": "/images/locations/doctor.jpg",
            "position": {"x": 300, "y": 150},
            "scenarios": [str(intermediate_scenarios[i % len(intermediate_scenarios)]["_id"]) for i in range(6, 8)],
            "unlock_requirements": {
                "chapter_progress": 20,
                "previous_location": None,
                "min_xp": 200,
                "min_level": 0,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [str(chapter3_characters[1]["_id"])],
            "estimated_minutes": 25,
            "rewards": {
                "xp": 300,
                "badge": None,
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": None
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter3_id),
            "name": "Bürgeramt (Citizen's Office)",
            "type": "scenario",
            "description": "Register your address and handle bureaucracy.",
            "image": "/images/locations/burgeramt.jpg",
            "position": {"x": 200, "y": 250},
            "scenarios": [str(intermediate_scenarios[i % len(intermediate_scenarios)]["_id"]) for i in range(8, 10)],
            "unlock_requirements": {
                "chapter_progress": 40,
                "previous_location": None,
                "min_xp": 500,
                "min_level": 3,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [],
            "estimated_minutes": 35,
            "rewards": {
                "xp": 350,
                "badge": "Bureaucracy Master",
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": None
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter3_id),
            "name": "Apotheke (Pharmacy)",
            "type": "scenario",
            "description": "Buy medicine and understand prescriptions.",
            "image": "/images/locations/pharmacy.jpg",
            "position": {"x": 400, "y": 200},
            "scenarios": [str(intermediate_scenarios[i % len(intermediate_scenarios)]["_id"]) for i in range(10, 12)],
            "unlock_requirements": {
                "chapter_progress": 60,
                "previous_location": None,
                "min_xp": 800,
                "min_level": 3,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [],
            "estimated_minutes": 20,
            "rewards": {
                "xp": 200,
                "badge": None,
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": None
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter3_id),
            "name": "Job Interview",
            "type": "scenario",
            "description": "Interview for your first job in Germany.",
            "image": "/images/locations/office.jpg",
            "position": {"x": 250, "y": 350},
            "scenarios": [str(advanced_scenarios[i % len(advanced_scenarios)]["_id"]) for i in range(2)] if advanced_scenarios else [str(intermediate_scenarios[0]["_id"])],
            "unlock_requirements": {
                "chapter_progress": 80,
                "previous_location": None,
                "min_xp": 1500,
                "min_level": 4,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [],
            "estimated_minutes": 40,
            "rewards": {
                "xp": 500,
                "badge": "Job Seeker",
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": "intern",
                "relationship_boost": None
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter3_id),
            "name": "Wohnungsbesichtigung (Apartment Viewing)",
            "type": "scenario",
            "description": "View apartments and negotiate rent.",
            "image": "/images/locations/apartment-viewing.jpg",
            "position": {"x": 350, "y": 300},
            "scenarios": [str(intermediate_scenarios[i % len(intermediate_scenarios)]["_id"]) for i in range(12, 14)],
            "unlock_requirements": {
                "chapter_progress": 90,
                "previous_location": None,
                "min_xp": 1800,
                "min_level": 4,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [],
            "estimated_minutes": 35,
            "rewards": {
                "xp": 400,
                "badge": "Home Hunter",
                "unlock": None,
                "housing_upgrade": "apartment",
                "career_upgrade": None,
                "relationship_boost": None
            },
            "created_at": datetime.utcnow()
        }
    ]
    
    await db.locations.insert_many(chapter3_locations)
    chapter3["locations"] = [str(loc["_id"]) for loc in chapter3_locations]
    print(f"✅ Created {len(chapter3_locations)} locations for Chapter 3")
    
    # Insert Chapter 3
    await db.learning_paths.insert_one(chapter3)
    print(f"✅ Created Chapter 3: {chapter3['title']}")
    
    print("\n" + "="*60)
    print("🎉 CHAPTERS 2 & 3 SEEDING COMPLETE!")
    print("="*60)
    print(f"📖 Chapter 2: {chapter2['title']} ({chapter2['level']})")
    print(f"   📍 Locations: {len(chapter2_locations)}")
    print(f"   👥 Characters: {len(chapter2_characters)}")
    print(f"   ⏱️  Estimated Time: {chapter2['estimated_hours']} hours")
    print(f"   🎯 XP Reward: {chapter2['completion_reward']['xp']}")
    print()
    print(f"📖 Chapter 3: {chapter3['title']} ({chapter3['level']})")
    print(f"   📍 Locations: {len(chapter3_locations)}")
    print(f"   👥 Characters: {len(chapter3_characters)}")
    print(f"   ⏱️  Estimated Time: {chapter3['estimated_hours']} hours")
    print(f"   🎯 XP Reward: {chapter3['completion_reward']['xp']}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(seed_chapters())
