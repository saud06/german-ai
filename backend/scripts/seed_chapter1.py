"""
Seed Chapter 1: The Arrival (A1 - Beginner)
Story-driven learning path with locations, characters, and scenarios
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import settings

async def seed_chapter1():
    # Use settings from .env
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]
    
    print("🌱 Seeding Chapter 1: The Arrival...")
    
    # ========================================================================
    # CHAPTER 1: THE ARRIVAL
    # ========================================================================
    
    chapter1_id = ObjectId()
    chapter1 = {
        "_id": chapter1_id,
        "chapter": 1,
        "level": "A1",
        "title": "The Arrival",
        "description": "You just landed in Berlin. Survive your first week in Germany.",
        "story": """Welcome to Germany! You've just stepped off the plane at Berlin Brandenburg Airport. 
        Your adventure begins now. You need to get to your hotel, find food, and start exploring this amazing city. 
        Let's see how well you can navigate your first days in Germany using only German!""",
        "image": "/images/chapters/chapter1-arrival.jpg",
        "locations": [],  # Will be filled with location IDs
        "characters": [],  # Will be filled with character IDs
        "estimated_hours": 20,
        "unlock_requirements": None,  # First chapter is always unlocked
        "completion_reward": {
            "xp": 1000,
            "badge": "Survivor",
            "unlock": "Chapter 2",
            "housing_upgrade": None,
            "career_upgrade": None
        },
        "created_at": datetime.utcnow()
    }
    
    # ========================================================================
    # CHARACTERS
    # ========================================================================
    
    # Character 1: Anna (Hotel Receptionist)
    anna_id = ObjectId()
    anna = {
        "_id": anna_id,
        "name": "Anna Müller",
        "role": "Hotel Receptionist",
        "personality": "Professional, helpful, patient with beginners",
        "age": 32,
        "occupation": "Hotel Receptionist",
        "avatar": "/images/characters/anna.jpg",
        "voice_id": "de_DE-thorsten-medium",
        "appears_in_chapters": [1],
        "relationship_levels": {
            "0": "Professional",
            "3": "Friendly",
            "5": "Helpful friend"
        },
        "conversation_topics": {
            "0": ["check-in", "hotel_services", "directions"],
            "3": ["berlin_tips", "restaurants", "attractions"],
            "5": ["personal_life", "german_culture"]
        },
        "ai_prompt": """You are Anna Müller, a 32-year-old hotel receptionist in Berlin. 
        You are professional, patient, and helpful, especially with guests who are learning German. 
        You speak clearly and use simple vocabulary for beginners. You're proud of Berlin and love 
        sharing tips about the city. Keep responses concise and encouraging.""",
        "backstory": "Anna has worked at the hotel for 5 years and loves meeting international guests.",
        "created_at": datetime.utcnow()
    }
    
    # Character 2: Hans (Café Waiter)
    hans_id = ObjectId()
    hans = {
        "_id": hans_id,
        "name": "Hans Schmidt",
        "role": "Café Waiter",
        "personality": "Friendly, casual, loves to chat",
        "age": 28,
        "occupation": "Café Waiter",
        "avatar": "/images/characters/hans.jpg",
        "voice_id": "de_DE-thorsten-medium",
        "appears_in_chapters": [1, 2],
        "relationship_levels": {
            "0": "Polite waiter",
            "3": "Friendly acquaintance",
            "5": "Friend",
            "8": "Good friend"
        },
        "conversation_topics": {
            "0": ["ordering", "menu", "payment"],
            "3": ["weather", "berlin_life", "hobbies"],
            "5": ["personal_stories", "recommendations", "events"],
            "8": ["deep_conversations", "advice", "friendship"]
        },
        "ai_prompt": """You are Hans Schmidt, a 28-year-old café waiter in Berlin. 
        You're friendly, casual, and love chatting with customers. You make learning German fun 
        by being encouraging and patient. You enjoy recommending your favorite menu items and 
        sharing stories about Berlin. Keep responses natural and conversational.""",
        "backstory": "Hans is studying music at university and works at the café part-time.",
        "created_at": datetime.utcnow()
    }
    
    # Character 3: Maria (Shop Assistant)
    maria_id = ObjectId()
    maria = {
        "_id": maria_id,
        "name": "Maria Weber",
        "role": "Shop Assistant",
        "personality": "Efficient, direct, typical Berliner",
        "age": 45,
        "occupation": "Supermarket Cashier",
        "avatar": "/images/characters/maria.jpg",
        "voice_id": "de_DE-thorsten-medium",
        "appears_in_chapters": [1],
        "relationship_levels": {
            "0": "Professional",
            "3": "Warmer",
            "5": "Helpful"
        },
        "conversation_topics": {
            "0": ["shopping", "prices", "payment"],
            "3": ["products", "recommendations"],
            "5": ["german_food", "cooking_tips"]
        },
        "ai_prompt": """You are Maria Weber, a 45-year-old supermarket cashier in Berlin. 
        You're efficient and direct (typical Berlin style), but warm up to regular customers. 
        You speak clearly but quickly. You're helpful once you get to know someone. 
        Keep responses brief and to the point.""",
        "backstory": "Maria has worked at the supermarket for 15 years and knows all the products.",
        "created_at": datetime.utcnow()
    }
    
    # Insert characters
    await db.characters.insert_many([anna, hans, maria])
    print(f"✅ Created 3 characters")
    
    # ========================================================================
    # LOCATIONS
    # ========================================================================
    
    # Location 1: Hotel Reception
    hotel_id = ObjectId()
    hotel = {
        "_id": hotel_id,
        "chapter_id": str(chapter1_id),
        "name": "Hotel Reception",
        "type": "scenario",
        "description": "Check into your hotel and get settled",
        "image": "/images/locations/hotel-reception.jpg",
        "position": {"x": 200, "y": 150},
        "scenarios": [],  # Will be filled
        "unlock_requirements": {
            "chapter_progress": 0,
            "previous_location": None
        },
        "characters": [str(anna_id)],
        "estimated_minutes": 15,
        "rewards": {
            "xp": 100,
            "badge": None,
            "unlock": "Café"
        },
        "created_at": datetime.utcnow()
    }
    
    # Location 2: Café
    cafe_id = ObjectId()
    cafe = {
        "_id": cafe_id,
        "chapter_id": str(chapter1_id),
        "name": "Café am Markt",
        "type": "scenario",
        "description": "Order your first German coffee and breakfast",
        "image": "/images/locations/cafe.jpg",
        "position": {"x": 350, "y": 200},
        "scenarios": [],  # Will be filled
        "unlock_requirements": {
            "chapter_progress": 20,
            "previous_location": str(hotel_id)
        },
        "characters": [str(hans_id)],
        "estimated_minutes": 15,
        "rewards": {
            "xp": 100,
            "badge": None,
            "unlock": "Supermarket"
        },
        "created_at": datetime.utcnow()
    }
    
    # Location 3: Supermarket
    supermarket_id = ObjectId()
    supermarket = {
        "_id": supermarket_id,
        "chapter_id": str(chapter1_id),
        "name": "REWE Supermarket",
        "type": "scenario",
        "description": "Buy groceries and essentials",
        "image": "/images/locations/supermarket.jpg",
        "position": {"x": 500, "y": 250},
        "scenarios": [],  # Will be filled
        "unlock_requirements": {
            "chapter_progress": 40,
            "previous_location": str(cafe_id)
        },
        "characters": [str(maria_id)],
        "estimated_minutes": 15,
        "rewards": {
            "xp": 100,
            "badge": None,
            "unlock": "City Center"
        },
        "created_at": datetime.utcnow()
    }
    
    # Location 4: City Center
    city_center_id = ObjectId()
    city_center = {
        "_id": city_center_id,
        "chapter_id": str(chapter1_id),
        "name": "Berlin City Center",
        "type": "scenario",
        "description": "Explore the city and ask for directions",
        "image": "/images/locations/city-center.jpg",
        "position": {"x": 300, "y": 350},
        "scenarios": [],  # Will be filled
        "unlock_requirements": {
            "chapter_progress": 60,
            "previous_location": str(supermarket_id)
        },
        "characters": [],
        "estimated_minutes": 20,
        "rewards": {
            "xp": 150,
            "badge": "Explorer",
            "unlock": "Chapter 1 Complete"
        },
        "created_at": datetime.utcnow()
    }
    
    # Insert locations
    await db.locations.insert_many([hotel, cafe, supermarket, city_center])
    print(f"✅ Created 4 locations")
    
    # ========================================================================
    # SCENARIOS (Link to existing or create new)
    # ========================================================================
    
    # Find existing hotel scenario or create new
    hotel_scenario = await db.scenarios.find_one({"title": {"$regex": "hotel", "$options": "i"}})
    if not hotel_scenario:
        hotel_scenario_id = ObjectId()
        hotel_scenario = {
            "_id": hotel_scenario_id,
            "title": "Hotel Check-in",
            "description": "Check into your hotel room",
            "difficulty": "A1",
            "character": "Anna Müller",
            "character_role": "Hotel Receptionist",
            "objectives": [
                "Greet the receptionist",
                "Provide your booking details",
                "Ask for WiFi password",
                "Thank and say goodbye"
            ],
            "conversation_starters": [
                "Guten Tag! Ich habe eine Reservierung.",
                "Hallo! Mein Name ist..."
            ],
            "success_criteria": {
                "min_turns": 4,
                "required_phrases": ["Guten Tag", "Reservierung", "WiFi"],
                "min_score": 70
            },
            "rewards": {
                "xp": 50,
                "vocabulary_learned": 10
            },
            "created_at": datetime.utcnow()
        }
        await db.scenarios.insert_one(hotel_scenario)
    
    # Update hotel location with scenario
    await db.locations.update_one(
        {"_id": hotel_id},
        {"$push": {"scenarios": str(hotel_scenario["_id"])}}
    )
    
    # Find or create café scenario
    cafe_scenario = await db.scenarios.find_one({"title": {"$regex": "café|coffee", "$options": "i"}})
    if not cafe_scenario:
        cafe_scenario_id = ObjectId()
        cafe_scenario = {
            "_id": cafe_scenario_id,
            "title": "Ordering at a Café",
            "description": "Order coffee and breakfast",
            "difficulty": "A1",
            "character": "Hans Schmidt",
            "character_role": "Waiter",
            "objectives": [
                "Greet the waiter",
                "Order a coffee",
                "Order food",
                "Ask for the bill"
            ],
            "conversation_starters": [
                "Guten Morgen! Ich möchte einen Kaffee, bitte.",
                "Hallo! Was empfehlen Sie?"
            ],
            "success_criteria": {
                "min_turns": 4,
                "required_phrases": ["Kaffee", "bitte", "Rechnung"],
                "min_score": 70
            },
            "rewards": {
                "xp": 50,
                "vocabulary_learned": 15
            },
            "created_at": datetime.utcnow()
        }
        await db.scenarios.insert_one(cafe_scenario)
    
    # Update café location
    await db.locations.update_one(
        {"_id": cafe_id},
        {"$push": {"scenarios": str(cafe_scenario["_id"])}}
    )
    
    print(f"✅ Linked scenarios to locations")
    
    # ========================================================================
    # UPDATE CHAPTER WITH LOCATIONS AND CHARACTERS
    # ========================================================================
    
    chapter1["locations"] = [str(hotel_id), str(cafe_id), str(supermarket_id), str(city_center_id)]
    chapter1["characters"] = [str(anna_id), str(hans_id), str(maria_id)]
    
    # Insert chapter
    await db.learning_paths.insert_one(chapter1)
    print(f"✅ Created Chapter 1: The Arrival")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print("\n" + "="*60)
    print("🎉 CHAPTER 1 SEEDING COMPLETE!")
    print("="*60)
    print(f"📖 Chapter: The Arrival (A1)")
    print(f"📍 Locations: 4 (Hotel, Café, Supermarket, City Center)")
    print(f"👥 Characters: 3 (Anna, Hans, Maria)")
    print(f"🎭 Scenarios: 2+ (linked to existing)")
    print(f"⏱️  Estimated Time: 20 hours")
    print(f"🎯 XP Reward: 1000")
    print("="*60)
    print("\n✅ Users can now start their German learning journey!")
    print("🗺️  Interactive map with 4 locations")
    print("💬 AI conversations with 3 characters")
    print("🎮 Story-driven progression")
    print("\n🚀 Next: Create frontend to display the learning path!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_chapter1())
