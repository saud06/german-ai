"""
Seed Chapters 4, 5, 6 for Learning Path
Chapter 4: Work Life (B1)
Chapter 5: Social Life (B1)
Chapter 6: Professional Life (B2)
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import settings

async def seed_advanced_chapters():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]
    
    print("🌱 Seeding Chapters 4, 5, 6...")
    
    # Get existing scenarios
    scenarios = await db.scenarios.find().to_list(length=100)
    intermediate = [s for s in scenarios if s.get('difficulty') == 'intermediate']
    advanced = [s for s in scenarios if s.get('difficulty') == 'advanced']
    
    # ========================================================================
    # CHAPTER 4: WORK LIFE (B1)
    # ========================================================================
    
    chapter4_id = ObjectId()
    chapter4 = {
        "_id": chapter4_id,
        "chapter": 4,
        "level": "B1",
        "title": "Work Life",
        "description": "Start your career in Germany and navigate the professional world.",
        "story": """Congratulations! You got the job! Now it's time to prove yourself.
        Learn professional German, understand workplace culture, and build your career.
        From your first day to important meetings, you'll master professional communication.""",
        "image": "/images/chapters/chapter4-work-life.jpg",
        "locations": [],
        "characters": [],
        "estimated_hours": 35,
        "unlock_requirements": {
            "chapter_progress": 100,
            "min_xp": 3500,
            "min_level": 4
        },
        "completion_reward": {
            "xp": 2500,
            "badge": "Professional",
            "unlock": "Chapter 5",
            "housing_upgrade": None,
            "career_upgrade": "employee",
            "relationship_boost": None
        },
        "created_at": datetime.utcnow()
    }
    
    # Chapter 4 Characters
    chapter4_characters = [
        {
            "_id": ObjectId(),
            "name": "Herr Müller",
            "role": "Boss",
            "personality": "Professional and demanding",
            "age": 52,
            "occupation": "Department Manager",
            "avatar": "/images/characters/herr-mueller.jpg",
            "voice_id": "de_DE-thorsten-low",
            "appears_in_chapters": [4, 5, 6],
            "relationship_levels": {
                "0": "New employee",
                "3": "Trusted colleague",
                "5": "Valued team member",
                "8": "Mentee"
            },
            "conversation_topics": {
                "0": ["work_tasks", "deadlines", "procedures"],
                "3": ["projects", "career_advice", "company_culture"],
                "5": ["leadership", "strategy", "personal_development"],
                "8": ["career_planning", "promotions", "mentorship"]
            },
            "ai_prompt": "You are Herr Müller, a 52-year-old department manager. You're professional, demanding but fair, and value hard work and punctuality. You speak formal German.",
            "backstory": "Herr Müller has been with the company for 25 years and knows everything about German business culture.",
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Julia",
            "role": "Colleague",
            "personality": "Helpful and friendly",
            "age": 29,
            "occupation": "Team Lead",
            "avatar": "/images/characters/julia.jpg",
            "voice_id": "de_DE-eva_k-x_low",
            "appears_in_chapters": [4, 5, 6],
            "relationship_levels": {
                "0": "Coworker",
                "3": "Work friend",
                "5": "Close colleague",
                "8": "Best work friend"
            },
            "conversation_topics": {
                "0": ["work", "office", "tasks"],
                "3": ["projects", "team", "lunch_plans"],
                "5": ["career", "life", "after_work"],
                "8": ["personal_life", "dreams", "support"]
            },
            "ai_prompt": "You are Julia, a friendly 29-year-old team lead. You help new employees settle in and explain German workplace culture. You're approachable and patient.",
            "backstory": "Julia started as an intern and worked her way up. She understands the challenges of being new.",
            "created_at": datetime.utcnow()
        }
    ]
    
    await db.characters.insert_many(chapter4_characters)
    chapter4["characters"] = [str(c["_id"]) for c in chapter4_characters]
    
    # Chapter 4 Locations
    chapter4_locations = [
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter4_id),
            "name": "First Day at Work",
            "type": "scenario",
            "description": "Navigate your first day at your new job.",
            "image": "/images/locations/first-day.jpg",
            "position": {"x": 150, "y": 100},
            "scenarios": [intermediate[i % len(intermediate)]["_id"] for i in range(3)],
            "unlock_requirements": {
                "chapter_progress": 0,
                "previous_location": None,
                "min_xp": 0,
                "min_level": 0,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [chapter4_characters[0]["_id"], chapter4_characters[1]["_id"]],
            "estimated_minutes": 30,
            "rewards": {
                "xp": 300,
                "badge": None,
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": {"mueller": 1, "julia": 2}
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter4_id),
            "name": "Team Meeting",
            "type": "scenario",
            "description": "Participate in your first team meeting.",
            "image": "/images/locations/meeting.jpg",
            "position": {"x": 300, "y": 150},
            "scenarios": [intermediate[i % len(intermediate)]["_id"] for i in range(3, 6)],
            "unlock_requirements": {
                "chapter_progress": 20,
                "previous_location": None,
                "min_xp": 300,
                "min_level": 4,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [chapter4_characters[0]["_id"]],
            "estimated_minutes": 35,
            "rewards": {
                "xp": 350,
                "badge": None,
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": {"mueller": 2}
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter4_id),
            "name": "Client Presentation",
            "type": "scenario",
            "description": "Present to an important client in German.",
            "image": "/images/locations/presentation.jpg",
            "position": {"x": 200, "y": 250},
            "scenarios": [advanced[i % len(advanced)]["_id"] for i in range(3)] if advanced else [intermediate[0]["_id"]],
            "unlock_requirements": {
                "chapter_progress": 40,
                "previous_location": None,
                "min_xp": 700,
                "min_level": 5,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [],
            "estimated_minutes": 40,
            "rewards": {
                "xp": 400,
                "badge": "Presenter",
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": None
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter4_id),
            "name": "Performance Review",
            "type": "scenario",
            "description": "Discuss your performance with your boss.",
            "image": "/images/locations/review.jpg",
            "position": {"x": 400, "y": 200},
            "scenarios": [advanced[i % len(advanced)]["_id"] for i in range(3, 6)] if advanced else [intermediate[1]["_id"]],
            "unlock_requirements": {
                "chapter_progress": 60,
                "previous_location": None,
                "min_xp": 1200,
                "min_level": 5,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [chapter4_characters[0]["_id"]],
            "estimated_minutes": 35,
            "rewards": {
                "xp": 450,
                "badge": None,
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": "employee",
                "relationship_boost": {"mueller": 3}
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter4_id),
            "name": "Salary Negotiation",
            "type": "scenario",
            "description": "Negotiate your salary increase.",
            "image": "/images/locations/negotiation.jpg",
            "position": {"x": 250, "y": 350},
            "scenarios": [advanced[i % len(advanced)]["_id"] for i in range(6, 9)] if advanced else [intermediate[2]["_id"]],
            "unlock_requirements": {
                "chapter_progress": 80,
                "previous_location": None,
                "min_xp": 1800,
                "min_level": 6,
                "required_scenarios": [],
                "relationship_level": {"mueller": 5}
            },
            "characters": [chapter4_characters[0]["_id"]],
            "estimated_minutes": 40,
            "rewards": {
                "xp": 500,
                "badge": "Negotiator",
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": {"mueller": 2}
            },
            "created_at": datetime.utcnow()
        }
    ]
    
    await db.locations.insert_many(chapter4_locations)
    chapter4["locations"] = [str(loc["_id"]) for loc in chapter4_locations]
    await db.learning_paths.insert_one(chapter4)
    print(f"✅ Created Chapter 4: {chapter4['title']} with {len(chapter4_locations)} locations")
    
    # ========================================================================
    # CHAPTER 5: SOCIAL LIFE (B1)
    # ========================================================================
    
    chapter5_id = ObjectId()
    chapter5 = {
        "_id": chapter5_id,
        "chapter": 5,
        "level": "B1",
        "title": "Social Life",
        "description": "Build a rich social life and explore German culture.",
        "story": """You're not just surviving anymore—you're thriving!
        Time to build a real social life. Join clubs, attend events, make lasting friendships.
        Experience German culture from the inside and feel truly at home.""",
        "image": "/images/chapters/chapter5-social-life.jpg",
        "locations": [],
        "characters": [],
        "estimated_hours": 30,
        "unlock_requirements": {
            "chapter_progress": 100,
            "min_xp": 6000,
            "min_level": 6
        },
        "completion_reward": {
            "xp": 2500,
            "badge": "Social Butterfly",
            "unlock": "Chapter 6",
            "housing_upgrade": "house",
            "career_upgrade": None,
            "relationship_boost": None
        },
        "created_at": datetime.utcnow()
    }
    
    # Chapter 5 Characters
    chapter5_characters = [
        {
            "_id": ObjectId(),
            "name": "Sophie",
            "role": "Best Friend",
            "personality": "Outgoing and fun",
            "age": 27,
            "occupation": "Event Planner",
            "avatar": "/images/characters/sophie.jpg",
            "voice_id": "de_DE-eva_k-x_low",
            "appears_in_chapters": [5, 6],
            "relationship_levels": {
                "0": "New acquaintance",
                "3": "Friend",
                "5": "Good friend",
                "8": "Best friend"
            },
            "conversation_topics": {
                "0": ["events", "parties", "fun"],
                "3": ["hobbies", "interests", "weekend"],
                "5": ["life", "relationships", "dreams"],
                "8": ["everything", "secrets", "deep_talks"]
            },
            "ai_prompt": "You are Sophie, an outgoing 27-year-old event planner. You love introducing people to German culture and organizing fun activities. You're energetic and friendly.",
            "backstory": "Sophie knows everyone in Berlin and loves bringing people together.",
            "created_at": datetime.utcnow()
        }
    ]
    
    await db.characters.insert_many(chapter5_characters)
    chapter5["characters"] = [str(c["_id"]) for c in chapter5_characters]
    
    # Chapter 5 Locations (4 locations)
    chapter5_locations = [
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter5_id),
            "name": "Stammtisch (Regular's Table)",
            "type": "scenario",
            "description": "Join a weekly meeting at a local pub.",
            "image": "/images/locations/stammtisch.jpg",
            "position": {"x": 150, "y": 100},
            "scenarios": [intermediate[i % len(intermediate)]["_id"] for i in range(6, 9)],
            "unlock_requirements": {
                "chapter_progress": 0,
                "previous_location": None,
                "min_xp": 0,
                "min_level": 0,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [chapter5_characters[0]["_id"]],
            "estimated_minutes": 30,
            "rewards": {
                "xp": 300,
                "badge": None,
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": {"sophie": 2}
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter5_id),
            "name": "Volksfest (Folk Festival)",
            "type": "scenario",
            "description": "Experience a traditional German festival.",
            "image": "/images/locations/volksfest.jpg",
            "position": {"x": 300, "y": 150},
            "scenarios": [intermediate[i % len(intermediate)]["_id"] for i in range(9, 12)],
            "unlock_requirements": {
                "chapter_progress": 25,
                "previous_location": None,
                "min_xp": 500,
                "min_level": 6,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [chapter5_characters[0]["_id"]],
            "estimated_minutes": 35,
            "rewards": {
                "xp": 350,
                "badge": "Culture Explorer",
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": {"sophie": 2}
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter5_id),
            "name": "Sportverein (Sports Club)",
            "type": "scenario",
            "description": "Join a local sports club and make friends.",
            "image": "/images/locations/sports-club.jpg",
            "position": {"x": 200, "y": 250},
            "scenarios": [intermediate[i % len(intermediate)]["_id"] for i in range(12, 15)],
            "unlock_requirements": {
                "chapter_progress": 50,
                "previous_location": None,
                "min_xp": 1000,
                "min_level": 6,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [],
            "estimated_minutes": 30,
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
            "chapter_id": str(chapter5_id),
            "name": "Housewarming Party",
            "type": "scenario",
            "description": "Host your first party in your new home.",
            "image": "/images/locations/party.jpg",
            "position": {"x": 400, "y": 200},
            "scenarios": [advanced[i % len(advanced)]["_id"] for i in range(9, 12)] if advanced else [intermediate[3]["_id"]],
            "unlock_requirements": {
                "chapter_progress": 75,
                "previous_location": None,
                "min_xp": 1500,
                "min_level": 7,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [chapter5_characters[0]["_id"]],
            "estimated_minutes": 40,
            "rewards": {
                "xp": 400,
                "badge": "Host",
                "unlock": None,
                "housing_upgrade": "house",
                "career_upgrade": None,
                "relationship_boost": {"sophie": 3}
            },
            "created_at": datetime.utcnow()
        }
    ]
    
    await db.locations.insert_many(chapter5_locations)
    chapter5["locations"] = [str(loc["_id"]) for loc in chapter5_locations]
    await db.learning_paths.insert_one(chapter5)
    print(f"✅ Created Chapter 5: {chapter5['title']} with {len(chapter5_locations)} locations")
    
    # ========================================================================
    # CHAPTER 6: PROFESSIONAL LIFE (B2)
    # ========================================================================
    
    chapter6_id = ObjectId()
    chapter6 = {
        "_id": chapter6_id,
        "chapter": 6,
        "level": "B2",
        "title": "Professional Life",
        "description": "Master advanced German and reach professional fluency.",
        "story": """You've come so far! Now it's time to reach true fluency.
        Handle complex business situations, lead teams, and communicate like a native.
        This is where you become truly professional in German.""",
        "image": "/images/chapters/chapter6-professional.jpg",
        "locations": [],
        "characters": [],
        "estimated_hours": 40,
        "unlock_requirements": {
            "chapter_progress": 100,
            "min_xp": 8500,
            "min_level": 7
        },
        "completion_reward": {
            "xp": 3000,
            "badge": "Master",
            "unlock": None,
            "housing_upgrade": None,
            "career_upgrade": "manager",
            "relationship_boost": None
        },
        "created_at": datetime.utcnow()
    }
    
    # Chapter 6 uses existing characters
    chapter6["characters"] = [str(chapter4_characters[0]["_id"]), str(chapter4_characters[1]["_id"])]
    
    # Chapter 6 Locations (4 locations)
    chapter6_locations = [
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter6_id),
            "name": "Leading a Project",
            "type": "scenario",
            "description": "Take charge of an important project.",
            "image": "/images/locations/project-lead.jpg",
            "position": {"x": 150, "y": 100},
            "scenarios": [advanced[i % len(advanced)]["_id"] for i in range(12, 15)] if advanced else [intermediate[4]["_id"]],
            "unlock_requirements": {
                "chapter_progress": 0,
                "previous_location": None,
                "min_xp": 0,
                "min_level": 0,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [chapter4_characters[0]["_id"], chapter4_characters[1]["_id"]],
            "estimated_minutes": 45,
            "rewards": {
                "xp": 450,
                "badge": None,
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": {"mueller": 2, "julia": 2}
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter6_id),
            "name": "Conference Presentation",
            "type": "scenario",
            "description": "Present at a professional conference.",
            "image": "/images/locations/conference.jpg",
            "position": {"x": 300, "y": 150},
            "scenarios": [advanced[i % len(advanced)]["_id"] for i in range(15, 18)] if advanced else [intermediate[5]["_id"]],
            "unlock_requirements": {
                "chapter_progress": 30,
                "previous_location": None,
                "min_xp": 700,
                "min_level": 7,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [],
            "estimated_minutes": 50,
            "rewards": {
                "xp": 500,
                "badge": "Speaker",
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": None
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter6_id),
            "name": "Promotion Interview",
            "type": "scenario",
            "description": "Interview for a management position.",
            "image": "/images/locations/promotion.jpg",
            "position": {"x": 200, "y": 250},
            "scenarios": [advanced[i % len(advanced)]["_id"] for i in range(18, 21)] if advanced else [intermediate[6]["_id"]],
            "unlock_requirements": {
                "chapter_progress": 60,
                "previous_location": None,
                "min_xp": 1500,
                "min_level": 8,
                "required_scenarios": [],
                "relationship_level": {"mueller": 7}
            },
            "characters": [chapter4_characters[0]["_id"]],
            "estimated_minutes": 45,
            "rewards": {
                "xp": 600,
                "badge": None,
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": "manager",
                "relationship_boost": {"mueller": 3}
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "chapter_id": str(chapter6_id),
            "name": "Mastery Achievement",
            "type": "review",
            "description": "Demonstrate your complete mastery of German.",
            "image": "/images/locations/mastery.jpg",
            "position": {"x": 400, "y": 200},
            "scenarios": [advanced[i % len(advanced)]["_id"] for i in range(21, 24)] if advanced else [intermediate[7]["_id"]],
            "unlock_requirements": {
                "chapter_progress": 90,
                "previous_location": None,
                "min_xp": 2500,
                "min_level": 9,
                "required_scenarios": [],
                "relationship_level": None
            },
            "characters": [],
            "estimated_minutes": 60,
            "rewards": {
                "xp": 1000,
                "badge": "German Master",
                "unlock": None,
                "housing_upgrade": None,
                "career_upgrade": None,
                "relationship_boost": None
            },
            "created_at": datetime.utcnow()
        }
    ]
    
    await db.locations.insert_many(chapter6_locations)
    chapter6["locations"] = [str(loc["_id"]) for loc in chapter6_locations]
    await db.learning_paths.insert_one(chapter6)
    print(f"✅ Created Chapter 6: {chapter6['title']} with {len(chapter6_locations)} locations")
    
    print("\n" + "="*60)
    print("🎉 CHAPTERS 4, 5, 6 SEEDING COMPLETE!")
    print("="*60)
    print(f"📖 Chapter 4: {chapter4['title']} ({chapter4['level']})")
    print(f"   📍 Locations: {len(chapter4_locations)}")
    print(f"   👥 Characters: {len(chapter4_characters)}")
    print(f"   ⏱️  Estimated Time: {chapter4['estimated_hours']} hours")
    print(f"   🎯 XP Reward: {chapter4['completion_reward']['xp']}")
    print()
    print(f"📖 Chapter 5: {chapter5['title']} ({chapter5['level']})")
    print(f"   📍 Locations: {len(chapter5_locations)}")
    print(f"   👥 Characters: {len(chapter5_characters)}")
    print(f"   ⏱️  Estimated Time: {chapter5['estimated_hours']} hours")
    print(f"   🎯 XP Reward: {chapter5['completion_reward']['xp']}")
    print()
    print(f"📖 Chapter 6: {chapter6['title']} ({chapter6['level']})")
    print(f"   📍 Locations: {len(chapter6_locations)}")
    print(f"   👥 Characters: 2 (reused)")
    print(f"   ⏱️  Estimated Time: {chapter6['estimated_hours']} hours")
    print(f"   🎯 XP Reward: {chapter6['completion_reward']['xp']}")
    print("="*60)
    print("\n📊 TOTAL LEARNING PATH:")
    print(f"   Chapters: 6 (A1 → B2)")
    print(f"   Locations: {4 + 5 + 6 + 5 + 4 + 4} = 28")
    print(f"   Total Hours: {20 + 25 + 30 + 35 + 30 + 40} = 180 hours")
    print(f"   Total XP: {1000 + 1500 + 2000 + 2500 + 2500 + 3000} = 12,500")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(seed_advanced_chapters())
