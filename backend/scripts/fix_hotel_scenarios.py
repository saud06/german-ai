"""
Fix Hotel Reception location by creating proper hotel scenarios
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_hotel_scenarios():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB_NAME")]
    
    print("=== FIXING HOTEL RECEPTION SCENARIOS ===\n")
    
    # Get the receptionist character
    receptionist = await db.characters.find_one({"name": "Anna Müller"})
    if not receptionist:
        print("❌ Receptionist character not found")
        return
    
    print(f"✅ Found receptionist: {receptionist['name']}")
    
    # Create 3 hotel-specific scenarios
    hotel_scenarios = [
        {
            "name": "Hotel Check-in",
            "title_en": "Hotel Check-in",
            "description": "Du kommst im Hotel an und möchtest einchecken. Gib deine Reservierung an.",
            "description_en": "You arrive at the hotel and want to check in. Provide your reservation details.",
            "difficulty": "beginner",
            "category": "hotel",
            "estimated_duration": 5,
            "characters": [{
                "id": str(receptionist["_id"]),
                "name": receptionist["name"],
                "role": "receptionist",
                "personality": "professional",
                "personality_traits": {
                    "friendliness": 5,
                    "formality": 4,
                    "patience": 5,
                    "helpfulness": 5,
                    "chattiness": 3
                },
                "emotion": {
                    "current": "neutral",
                    "intensity": 5,
                    "triggers": {}
                },
                "voice_id": receptionist.get("voice_id"),
                "description": "Anna ist eine professionelle Rezeptionistin.",
                "greeting": "Guten Tag! Willkommen in unserem Hotel. Wie kann ich Ihnen helfen?",
                "remembers_user": False,
                "memory": {}
            }],
            "objectives": [
                {
                    "id": str(ObjectId()),
                    "description": "Begrüße die Rezeptionistin",
                    "keywords": ["hallo", "guten tag", "grüß gott"],
                    "required": True,
                    "hint": "Sage 'Guten Tag'",
                    "completed": False,
                    "xp_reward": 20,
                    "difficulty_level": 1
                },
                {
                    "id": str(ObjectId()),
                    "description": "Sage, dass du eine Reservierung hast",
                    "keywords": ["reservierung", "gebucht", "zimmer", "name"],
                    "required": True,
                    "hint": "Sage 'Ich habe eine Reservierung auf den Namen...'",
                    "completed": False,
                    "xp_reward": 30,
                    "difficulty_level": 1
                },
                {
                    "id": str(ObjectId()),
                    "description": "Frage nach dem WLAN-Passwort",
                    "keywords": ["wlan", "wifi", "internet", "passwort"],
                    "required": True,
                    "hint": "Frage 'Wie ist das WLAN-Passwort?'",
                    "completed": False,
                    "xp_reward": 20,
                    "difficulty_level": 1
                }
            ],
            "dialogue_branches": [],
            "decision_points": [],
            "context": "Du bist gerade im Hotel angekommen und möchtest einchecken. Die Rezeptionistin ist freundlich und hilfsbereit.",
            "system_prompt": "Du bist Anna, eine professionelle Hotelrezeptionistin. Hilf dem Gast beim Einchecken. Sei freundlich und effizient.",
            "has_time_limit": False,
            "time_limit_minutes": None,
            "has_checkpoints": False,
            "checkpoints": [],
            "xp_reward": 100,
            "bonus_xp": 50,
            "icon": "🏨",
            "tags": ["hotel", "check-in", "basics"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "total_completions": 0,
            "total_attempts": 0,
            "average_rating": 0.0,
            "average_completion_time": 0
        },
        {
            "name": "Zimmerservice bestellen",
            "title_en": "Order Room Service",
            "description": "Du möchtest Essen auf dein Zimmer bestellen.",
            "description_en": "You want to order food to your room.",
            "difficulty": "beginner",
            "category": "hotel",
            "estimated_duration": 5,
            "characters": [{
                "id": str(receptionist["_id"]),
                "name": receptionist["name"],
                "role": "receptionist",
                "personality": "professional",
                "personality_traits": {
                    "friendliness": 5,
                    "formality": 4,
                    "patience": 5,
                    "helpfulness": 5,
                    "chattiness": 3
                },
                "emotion": {
                    "current": "neutral",
                    "intensity": 5,
                    "triggers": {}
                },
                "voice_id": receptionist.get("voice_id"),
                "description": "Anna ist eine professionelle Rezeptionistin.",
                "greeting": "Guten Tag! Möchten Sie etwas bestellen?",
                "remembers_user": False,
                "memory": {}
            }],
            "objectives": [
                {
                    "id": str(ObjectId()),
                    "description": "Sage deine Zimmernummer",
                    "keywords": ["zimmer", "nummer", "raum"],
                    "required": True,
                    "hint": "Sage 'Ich bin in Zimmer...'",
                    "completed": False,
                    "xp_reward": 20,
                    "difficulty_level": 1
                },
                {
                    "id": str(ObjectId()),
                    "description": "Bestelle Frühstück",
                    "keywords": ["frühstück", "breakfast", "essen", "bestellen"],
                    "required": True,
                    "hint": "Sage 'Ich möchte Frühstück bestellen'",
                    "completed": False,
                    "xp_reward": 30,
                    "difficulty_level": 1
                },
                {
                    "id": str(ObjectId()),
                    "description": "Frage wann es kommt",
                    "keywords": ["wann", "zeit", "wie lange", "dauert"],
                    "required": True,
                    "hint": "Frage 'Wann kommt das Frühstück?'",
                    "completed": False,
                    "xp_reward": 20,
                    "difficulty_level": 1
                }
            ],
            "dialogue_branches": [],
            "decision_points": [],
            "context": "Du bist in deinem Hotelzimmer und möchtest Frühstück bestellen.",
            "system_prompt": "Du bist Anna, eine professionelle Hotelrezeptionistin. Hilf dem Gast beim Bestellen von Zimmerservice.",
            "has_time_limit": False,
            "time_limit_minutes": None,
            "has_checkpoints": False,
            "checkpoints": [],
            "xp_reward": 100,
            "bonus_xp": 50,
            "icon": "🍳",
            "tags": ["hotel", "room-service", "food"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "total_completions": 0,
            "total_attempts": 0,
            "average_rating": 0.0,
            "average_completion_time": 0
        },
        {
            "name": "Hotel Check-out",
            "title_en": "Hotel Check-out",
            "description": "Du möchtest auschecken und die Rechnung bezahlen.",
            "description_en": "You want to check out and pay the bill.",
            "difficulty": "beginner",
            "category": "hotel",
            "estimated_duration": 5,
            "characters": [{
                "id": str(receptionist["_id"]),
                "name": receptionist["name"],
                "role": "receptionist",
                "personality": "professional",
                "personality_traits": {
                    "friendliness": 5,
                    "formality": 4,
                    "patience": 5,
                    "helpfulness": 5,
                    "chattiness": 3
                },
                "emotion": {
                    "current": "neutral",
                    "intensity": 5,
                    "triggers": {}
                },
                "voice_id": receptionist.get("voice_id"),
                "description": "Anna ist eine professionelle Rezeptionistin.",
                "greeting": "Guten Tag! Möchten Sie auschecken?",
                "remembers_user": False,
                "memory": {}
            }],
            "objectives": [
                {
                    "id": str(ObjectId()),
                    "description": "Sage dass du auschecken möchtest",
                    "keywords": ["auschecken", "check-out", "abreisen", "gehen"],
                    "required": True,
                    "hint": "Sage 'Ich möchte auschecken'",
                    "completed": False,
                    "xp_reward": 20,
                    "difficulty_level": 1
                },
                {
                    "id": str(ObjectId()),
                    "description": "Gib deine Zimmernummer an",
                    "keywords": ["zimmer", "nummer", "raum"],
                    "required": True,
                    "hint": "Sage 'Zimmer Nummer...'",
                    "completed": False,
                    "xp_reward": 20,
                    "difficulty_level": 1
                },
                {
                    "id": str(ObjectId()),
                    "description": "Frage nach der Rechnung",
                    "keywords": ["rechnung", "bezahlen", "zahlen", "kosten"],
                    "required": True,
                    "hint": "Frage 'Kann ich die Rechnung haben?'",
                    "completed": False,
                    "xp_reward": 30,
                    "difficulty_level": 1
                }
            ],
            "dialogue_branches": [],
            "decision_points": [],
            "context": "Du möchtest aus dem Hotel auschecken und die Rechnung bezahlen.",
            "system_prompt": "Du bist Anna, eine professionelle Hotelrezeptionistin. Hilf dem Gast beim Auschecken.",
            "has_time_limit": False,
            "time_limit_minutes": None,
            "has_checkpoints": False,
            "checkpoints": [],
            "xp_reward": 100,
            "bonus_xp": 50,
            "icon": "🚪",
            "tags": ["hotel", "check-out", "payment"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "total_completions": 0,
            "total_attempts": 0,
            "average_rating": 0.0,
            "average_completion_time": 0
        }
    ]
    
    # Insert scenarios
    print("\n📝 Creating hotel scenarios...")
    result = await db.scenarios.insert_many(hotel_scenarios)
    scenario_ids = result.inserted_ids
    
    print(f"✅ Created {len(scenario_ids)} hotel scenarios:")
    for i, sid in enumerate(scenario_ids):
        print(f"   {i+1}. {hotel_scenarios[i]['name']} - {sid}")
    
    # Update Hotel Reception location
    print("\n🏨 Updating Hotel Reception location...")
    location_result = await db.locations.update_one(
        {"_id": ObjectId("6913148840f0bc256e922024")},
        {"$set": {"scenarios": scenario_ids}}
    )
    
    if location_result.modified_count > 0:
        print("✅ Hotel Reception location updated successfully!")
    else:
        print("⚠️  Location not updated (may already be correct)")
    
    # Verify
    print("\n🔍 Verifying update...")
    location = await db.locations.find_one({"_id": ObjectId("6913148840f0bc256e922024")})
    print(f"✅ Hotel Reception now has {len(location['scenarios'])} scenarios:")
    for sid in location['scenarios']:
        scenario = await db.scenarios.find_one({"_id": sid})
        if scenario:
            print(f"   - {scenario['name']} ({scenario['category']})")
    
    print("\n🎉 Fix complete!")

if __name__ == "__main__":
    asyncio.run(fix_hotel_scenarios())
