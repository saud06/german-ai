"""
Seed remaining 5 scenarios for Phase 4 (Part 2)
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from bson import ObjectId

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "german_ai"

async def seed_phase4_scenarios_part2():
    """Seed remaining 5 advanced scenarios"""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    print("🎭 Seeding Phase 4 Scenarios (Part 2)...")
    
    scenarios = [
        # 6. Apartment Hunting
        {
            "name": "Wohnungssuche",
            "title_en": "Apartment Hunting",
            "description": "Sie suchen eine Wohnung und besichtigen eine Mietwohnung. Verhandeln Sie mit dem Vermieter.",
            "description_en": "You're looking for an apartment and viewing a rental. Negotiate with the landlord.",
            "difficulty": "intermediate",
            "category": "housing",
            "estimated_duration": 15,
            "icon": "🏠",
            "tags": ["housing", "rent", "apartment", "negotiation"],
            
            "characters": [{
                "id": str(ObjectId()),
                "name": "Herr Müller",
                "role": "landlord",
                "personality": "business-like but negotiable",
                "personality_traits": {
                    "friendliness": 6,
                    "formality": 7,
                    "patience": 6,
                    "helpfulness": 7,
                    "chattiness": 5
                },
                "emotion": {
                    "current": "neutral",
                    "intensity": 5,
                    "triggers": {}
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Ein Vermieter, der eine Wohnung vermieten möchte. Geschäftlich aber fair.",
                "greeting": "Guten Tag! Willkommen. Möchten Sie die Wohnung besichtigen?",
                "remembers_user": False,
                "memory": {}
            }],
            
            "objectives": [
                {
                    "id": str(ObjectId()),
                    "description": "Fragen Sie nach der Wohnung",
                    "keywords": ["zimmer", "größe", "quadratmeter", "balkon", "küche"],
                    "required": True,
                    "hint": "Fragen Sie: 'Wie viele Zimmer hat die Wohnung?'",
                    "completed": False,
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "id": str(ObjectId()),
                    "description": "Fragen Sie nach der Miete",
                    "keywords": ["miete", "kosten", "nebenkosten", "kaution", "preis"],
                    "required": True,
                    "hint": "Fragen Sie: 'Wie hoch ist die Miete?'",
                    "completed": False,
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "id": str(ObjectId()),
                    "description": "Verhandeln Sie die Konditionen",
                    "keywords": ["verhandeln", "möglich", "flexibel", "einzug", "vertrag"],
                    "required": False,
                    "hint": "Fragen Sie: 'Ist der Preis verhandelbar?'",
                    "completed": False,
                    "xp_reward": 40,
                    "difficulty_level": 3
                }
            ],
            
            "context": "You are Herr Müller, a landlord showing an apartment. Describe the apartment, answer questions about rent and utilities, and be open to reasonable negotiation. Be professional but friendly.",
            "system_prompt": "Du bist Herr Müller, ein Vermieter. Zeige die Wohnung, beantworte Fragen über Miete und Nebenkosten. Sei professionell und verhandlungsbereit.",
            
            "xp_reward": 150,
            "bonus_xp": 75,
            "has_time_limit": False,
            "has_checkpoints": False
        },
        
        # 7. Emergency Situations
        {
            "name": "Notfall",
            "title_en": "Emergency",
            "description": "Ein Notfall! Rufen Sie die Notrufzentrale an und beschreiben Sie die Situation.",
            "description_en": "An emergency! Call the emergency center and describe the situation.",
            "difficulty": "advanced",
            "category": "emergency",
            "estimated_duration": 8,
            "icon": "🚨",
            "tags": ["emergency", "help", "urgent", "safety"],
            
            "characters": [{
                "id": str(ObjectId()),
                "name": "Operator Schmidt",
                "role": "emergency_operator",
                "personality": "calm and directive",
                "personality_traits": {
                    "friendliness": 7,
                    "formality": 8,
                    "patience": 9,
                    "helpfulness": 10,
                    "chattiness": 4
                },
                "emotion": {
                    "current": "calm",
                    "intensity": 8,
                    "triggers": {}
                },
                "voice_id": "de_DE-eva_k-x_low",
                "description": "Eine professionelle Notruf-Disponentin, die ruhig und effizient hilft.",
                "greeting": "Notruf 112, was ist passiert?",
                "remembers_user": False,
                "memory": {}
            }],
            
            "objectives": [
                {
                    "id": str(ObjectId()),
                    "description": "Beschreiben Sie den Notfall",
                    "keywords": ["unfall", "verletzt", "feuer", "hilfe", "notfall", "passiert"],
                    "required": True,
                    "hint": "Sagen Sie: 'Es gibt einen Unfall' oder 'Jemand ist verletzt'",
                    "completed": False,
                    "xp_reward": 60,
                    "difficulty_level": 3
                },
                {
                    "id": str(ObjectId()),
                    "description": "Geben Sie den Standort an",
                    "keywords": ["adresse", "straße", "wo", "standort", "ort"],
                    "required": True,
                    "hint": "Sagen Sie: 'Ich bin in der... Straße'",
                    "completed": False,
                    "xp_reward": 60,
                    "difficulty_level": 3
                },
                {
                    "id": str(ObjectId()),
                    "description": "Folgen Sie den Anweisungen",
                    "keywords": ["ja", "okay", "verstanden", "mache ich"],
                    "required": True,
                    "hint": "Bestätigen Sie: 'Ja, verstanden'",
                    "completed": False,
                    "xp_reward": 40,
                    "difficulty_level": 3
                }
            ],
            
            "context": "You are an emergency operator. Stay calm, get essential information (what happened, location, injuries), and provide clear instructions. Be efficient and reassuring.",
            "system_prompt": "Du bist eine Notruf-Disponentin. Bleibe ruhig, hole wichtige Informationen ein (was, wo, Verletzungen) und gib klare Anweisungen. Sei effizient und beruhigend.",
            
            "xp_reward": 180,
            "bonus_xp": 90,
            "has_time_limit": True,
            "time_limit_minutes": 5,
            "has_checkpoints": False
        },
        
        # 8. Cultural Events
        {
            "name": "Kulturveranstaltung",
            "title_en": "Cultural Event",
            "description": "Sie möchten Tickets für eine Theateraufführung kaufen und mehr über die Veranstaltung erfahren.",
            "description_en": "You want to buy tickets for a theater performance and learn more about the event.",
            "difficulty": "intermediate",
            "category": "culture",
            "estimated_duration": 12,
            "icon": "🎭",
            "tags": ["culture", "theater", "events", "entertainment"],
            
            "characters": [{
                "id": str(ObjectId()),
                "name": "Frau Klein",
                "role": "theater_attendant",
                "personality": "enthusiastic and knowledgeable",
                "personality_traits": {
                    "friendliness": 9,
                    "formality": 5,
                    "patience": 8,
                    "helpfulness": 9,
                    "chattiness": 8
                },
                "emotion": {
                    "current": "enthusiastic",
                    "intensity": 7,
                    "triggers": {}
                },
                "voice_id": "de_DE-eva_k-x_low",
                "description": "Eine begeisterte Theatermitarbeiterin, die gerne über Kultur spricht.",
                "greeting": "Guten Abend! Willkommen im Deutschen Theater. Wie kann ich Ihnen helfen?",
                "remembers_user": False,
                "memory": {}
            }],
            
            "objectives": [
                {
                    "id": str(ObjectId()),
                    "description": "Fragen Sie nach Veranstaltungen",
                    "keywords": ["aufführung", "stück", "programm", "heute", "wann"],
                    "required": True,
                    "hint": "Fragen Sie: 'Welche Aufführungen gibt es heute?'",
                    "completed": False,
                    "xp_reward": 40,
                    "difficulty_level": 2
                },
                {
                    "id": str(ObjectId()),
                    "description": "Kaufen Sie Tickets",
                    "keywords": ["tickets", "karten", "kaufen", "plätze", "reservieren"],
                    "required": True,
                    "hint": "Sagen Sie: 'Ich möchte zwei Tickets kaufen'",
                    "completed": False,
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "id": str(ObjectId()),
                    "description": "Sprechen Sie über Kultur",
                    "keywords": ["interessant", "kultur", "künstler", "geschichte", "bedeutung"],
                    "required": False,
                    "hint": "Fragen Sie: 'Worum geht es in dem Stück?'",
                    "completed": False,
                    "xp_reward": 40,
                    "difficulty_level": 2
                }
            ],
            
            "context": "You are Frau Klein, an enthusiastic theater attendant. Help customers find performances, buy tickets, and share your passion for culture. Be friendly and informative.",
            "system_prompt": "Du bist Frau Klein, eine begeisterte Theatermitarbeiterin. Hilf Kunden bei der Auswahl, verkaufe Tickets und teile deine Leidenschaft für Kultur. Sei freundlich und informativ.",
            
            "xp_reward": 140,
            "bonus_xp": 70,
            "has_time_limit": False,
            "has_checkpoints": False
        },
        
        # 9. Sports/Fitness
        {
            "name": "Im Fitnessstudio",
            "title_en": "At the Gym",
            "description": "Sie möchten sich im Fitnessstudio anmelden und Informationen über Kurse erhalten.",
            "description_en": "You want to join a gym and get information about classes.",
            "difficulty": "beginner",
            "category": "sports",
            "estimated_duration": 10,
            "icon": "⚽",
            "tags": ["sports", "fitness", "health", "gym"],
            
            "characters": [{
                "id": str(ObjectId()),
                "name": "Max",
                "role": "fitness_trainer",
                "personality": "energetic and motivating",
                "personality_traits": {
                    "friendliness": 9,
                    "formality": 3,
                    "patience": 8,
                    "helpfulness": 9,
                    "chattiness": 8
                },
                "emotion": {
                    "current": "energetic",
                    "intensity": 8,
                    "triggers": {}
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Ein energiegeladener Fitnesstrainer, der Menschen motiviert.",
                "greeting": "Hey! Willkommen im FitLife! Bist du bereit, fit zu werden?",
                "remembers_user": True,
                "memory": {}
            }],
            
            "objectives": [
                {
                    "id": str(ObjectId()),
                    "description": "Fragen Sie nach Mitgliedschaft",
                    "keywords": ["mitgliedschaft", "anmelden", "beitritt", "kosten", "preis"],
                    "required": True,
                    "hint": "Fragen Sie: 'Wie kann ich Mitglied werden?'",
                    "completed": False,
                    "xp_reward": 40,
                    "difficulty_level": 1
                },
                {
                    "id": str(ObjectId()),
                    "description": "Fragen Sie nach Kursen",
                    "keywords": ["kurse", "training", "yoga", "spinning", "klassen"],
                    "required": True,
                    "hint": "Fragen Sie: 'Welche Kurse bieten Sie an?'",
                    "completed": False,
                    "xp_reward": 40,
                    "difficulty_level": 1
                },
                {
                    "id": str(ObjectId()),
                    "description": "Sprechen Sie über Fitnessziele",
                    "keywords": ["ziel", "abnehmen", "muskeln", "fit", "gesund"],
                    "required": False,
                    "hint": "Sagen Sie: 'Ich möchte fit werden' oder 'Mein Ziel ist...'",
                    "completed": False,
                    "xp_reward": 30,
                    "difficulty_level": 1
                }
            ],
            
            "context": "You are Max, an energetic fitness trainer. Help new members join the gym, explain classes and equipment, and motivate them to reach their fitness goals. Be enthusiastic and supportive. Use informal language (du).",
            "system_prompt": "Du bist Max, ein energiegeladener Fitnesstrainer. Hilf neuen Mitgliedern, erkläre Kurse und motiviere sie. Sei enthusiastisch und unterstützend. Benutze 'du'.",
            
            "xp_reward": 110,
            "bonus_xp": 55,
            "has_time_limit": False,
            "has_checkpoints": False
        },
        
        # 10. Technology Support
        {
            "name": "Technischer Support",
            "title_en": "Tech Support",
            "description": "Ihr Computer hat ein Problem. Rufen Sie den technischen Support an und beschreiben Sie das Problem.",
            "description_en": "Your computer has a problem. Call tech support and describe the issue.",
            "difficulty": "intermediate",
            "category": "technology",
            "estimated_duration": 12,
            "icon": "💻",
            "tags": ["technology", "computer", "support", "problem-solving"],
            
            "characters": [{
                "id": str(ObjectId()),
                "name": "Herr Wagner",
                "role": "tech_support",
                "personality": "patient and technical",
                "personality_traits": {
                    "friendliness": 7,
                    "formality": 6,
                    "patience": 10,
                    "helpfulness": 9,
                    "chattiness": 6
                },
                "emotion": {
                    "current": "helpful",
                    "intensity": 6,
                    "triggers": {}
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Ein geduldiger IT-Support-Mitarbeiter, der technische Probleme löst.",
                "greeting": "Guten Tag, IT-Support. Mein Name ist Wagner. Wie kann ich Ihnen helfen?",
                "remembers_user": False,
                "memory": {}
            }],
            
            "objectives": [
                {
                    "id": str(ObjectId()),
                    "description": "Beschreiben Sie das Problem",
                    "keywords": ["problem", "funktioniert nicht", "fehler", "geht nicht", "kaputt"],
                    "required": True,
                    "hint": "Sagen Sie: 'Mein Computer funktioniert nicht' oder 'Ich habe ein Problem mit...'",
                    "completed": False,
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "id": str(ObjectId()),
                    "description": "Folgen Sie den Anweisungen",
                    "keywords": ["versuche", "gemacht", "klicke", "drücke", "okay"],
                    "required": True,
                    "hint": "Bestätigen Sie: 'Ich habe es versucht' oder 'Was soll ich tun?'",
                    "completed": False,
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "id": str(ObjectId()),
                    "description": "Verstehen Sie die Lösung",
                    "keywords": ["verstehe", "funktioniert", "danke", "gelöst", "jetzt"],
                    "required": False,
                    "hint": "Sagen Sie: 'Jetzt funktioniert es' oder 'Vielen Dank'",
                    "completed": False,
                    "xp_reward": 30,
                    "difficulty_level": 2
                }
            ],
            
            "context": "You are Herr Wagner, a patient tech support specialist. Listen to the problem, ask clarifying questions, provide step-by-step solutions, and ensure the customer understands. Use technical terms but explain them clearly.",
            "system_prompt": "Du bist Herr Wagner, ein IT-Support-Mitarbeiter. Höre das Problem an, stelle Fragen, gib Schritt-für-Schritt-Lösungen und stelle sicher, dass der Kunde versteht. Erkläre technische Begriffe klar.",
            
            "xp_reward": 140,
            "bonus_xp": 70,
            "has_time_limit": False,
            "has_checkpoints": False
        }
    ]
    
    # Insert remaining 5 scenarios
    for scenario in scenarios:
        scenario["created_at"] = datetime.utcnow()
        scenario["updated_at"] = datetime.utcnow()
        scenario["total_completions"] = 0
        scenario["total_attempts"] = 0
        scenario["average_rating"] = 0.0
        scenario["average_completion_time"] = 0
        
        await db["scenarios"].update_one(
            {"name": scenario["name"]},
            {"$set": scenario},
            upsert=True
        )
        print(f"  ✅ {scenario['icon']} {scenario['name']} ({scenario['difficulty']})")
    
    print(f"\n✅ Seeded {len(scenarios)} scenarios (Part 2/2)")
    print("\n📊 Summary:")
    print(f"  - Beginner: 2 scenarios")
    print(f"  - Intermediate: 2 scenarios")
    print(f"  - Advanced: 1 scenario")
    print(f"\n🎉 All 10 Phase 4 scenarios complete!")
    
    # Get total scenario count
    total = await db["scenarios"].count_documents({})
    print(f"\n📈 Total scenarios in database: {total}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_phase4_scenarios_part2())
