"""
Seed script for remaining 5 advanced scenarios (6-10)
Phase 4 - Week 7
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import get_db
from app.models.scenario import Scenario

async def seed_remaining_scenarios():
    """Seed scenarios 6-10"""
    db = await get_db()
    scenarios_collection = db.scenarios
    
    print("🎮 Seeding Remaining 5 Advanced Scenarios...")
    
    scenarios = [
        # 6. Apartment Hunting
        {
            "name": "Wohnungssuche",
            "title_en": "Apartment Hunting",
            "description": "Sie besichtigen eine Wohnung und verhandeln mit dem Vermieter.",
            "description_en": "You're viewing an apartment and negotiating with the landlord.",
            "difficulty": "intermediate",
            "category": "housing",
            "estimated_duration": 15,
            "icon": "🏠",
            "characters": [{
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
                    "triggers": {
                        "interested_tenant": "pleased",
                        "negotiation": "business"
                    }
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Vermieter mit mehreren Wohnungen",
                "greeting": "Guten Tag! Kommen Sie herein. Hier ist die Wohnung.",
                "remembers_user": False,
                "memory": {}
            }],
            "objectives": [
                {
                    "description": "Fragen Sie nach der Miete",
                    "keywords": ["miete", "kostet", "monat", "kaltmiete", "nebenkosten"],
                    "required": True,
                    "hint": "Fragen Sie: 'Wie hoch ist die Miete?'",
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "description": "Fragen Sie nach den Nebenkosten",
                    "keywords": ["nebenkosten", "strom", "heizung", "wasser", "internet"],
                    "required": True,
                    "hint": "Fragen Sie: 'Was ist in den Nebenkosten enthalten?'",
                    "xp_reward": 60,
                    "difficulty_level": 3
                },
                {
                    "description": "Verhandeln Sie die Konditionen",
                    "keywords": ["kaution", "vertrag", "einzug", "wann", "möglich"],
                    "required": False,
                    "hint": "Fragen Sie: 'Wann kann ich einziehen?'",
                    "xp_reward": 60,
                    "difficulty_level": 3
                }
            ],
            "context": "Viewing an apartment and discussing rent, utilities, deposit, and move-in date with landlord.",
            "system_prompt": "Du bist Herr Müller, ein Vermieter. Zeige die Wohnung, beantworte Fragen zu Miete und Nebenkosten. Sei geschäftlich aber fair.",
            "xp_reward": 170,
            "bonus_xp": 85,
            "tags": ["housing", "rental", "intermediate", "negotiation"]
        },
        
        # 7. Emergency Situations
        {
            "name": "Notfall",
            "title_en": "Emergency Situation",
            "description": "Sie müssen einen Notfall melden und wichtige Informationen geben.",
            "description_en": "You need to report an emergency and provide important information.",
            "difficulty": "advanced",
            "category": "emergency",
            "estimated_duration": 8,
            "icon": "🚨",
            "characters": [{
                "name": "Notrufzentrale",
                "role": "emergency_operator",
                "personality": "calm and directive",
                "personality_traits": {
                    "friendliness": 7,
                    "formality": 8,
                    "patience": 9,
                    "helpfulness": 10,
                    "chattiness": 3
                },
                "emotion": {
                    "current": "calm",
                    "intensity": 8,
                    "triggers": {
                        "panic": "reassuring",
                        "clear_info": "efficient"
                    }
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Professioneller Notfall-Operator",
                "greeting": "Notruf 112, was ist passiert?",
                "remembers_user": False,
                "memory": {}
            }],
            "objectives": [
                {
                    "description": "Beschreiben Sie den Notfall",
                    "keywords": ["unfall", "verletzt", "feuer", "hilfe", "notfall"],
                    "required": True,
                    "hint": "Sagen Sie klar: 'Es gibt einen...' oder 'Jemand ist...'",
                    "xp_reward": 70,
                    "difficulty_level": 4
                },
                {
                    "description": "Geben Sie den Ort an",
                    "keywords": ["adresse", "straße", "wo", "ort", "hier"],
                    "required": True,
                    "hint": "Sagen Sie: 'Ich bin in der... Straße'",
                    "xp_reward": 60,
                    "difficulty_level": 4
                },
                {
                    "description": "Folgen Sie den Anweisungen",
                    "keywords": ["ja", "okay", "verstanden", "mache", "warte"],
                    "required": True,
                    "hint": "Hören Sie zu und bestätigen Sie: 'Ja, verstanden'",
                    "xp_reward": 50,
                    "difficulty_level": 3
                }
            ],
            "context": "Emergency call. Must clearly describe situation, give location, and follow operator's instructions.",
            "system_prompt": "Du bist ein Notfall-Operator. Bleibe ruhig, stelle klare Fragen, gib Anweisungen. Priorität: Ort, Art des Notfalls, Anzahl der Betroffenen.",
            "xp_reward": 180,
            "bonus_xp": 90,
            "tags": ["emergency", "critical", "advanced", "important"]
        },
        
        # 8. Cultural Events
        {
            "name": "Kulturveranstaltung",
            "title_en": "Cultural Event",
            "description": "Sie kaufen Tickets für ein Theater oder Konzert und erfahren mehr über die Veranstaltung.",
            "description_en": "You're buying tickets for a theater or concert and learning about the event.",
            "difficulty": "intermediate",
            "category": "culture",
            "estimated_duration": 12,
            "icon": "🎭",
            "characters": [{
                "name": "Frau Wagner",
                "role": "theater_attendant",
                "personality": "enthusiastic and knowledgeable",
                "personality_traits": {
                    "friendliness": 9,
                    "formality": 6,
                    "patience": 8,
                    "helpfulness": 9,
                    "chattiness": 8
                },
                "emotion": {
                    "current": "enthusiastic",
                    "intensity": 8,
                    "triggers": {
                        "interest_in_culture": "excited",
                        "questions": "helpful"
                    }
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Theaterkartenverkäuferin mit Leidenschaft für Kultur",
                "greeting": "Guten Tag! Willkommen im Theater. Interessieren Sie sich für eine bestimmte Vorstellung?",
                "remembers_user": False,
                "memory": {}
            }],
            "objectives": [
                {
                    "description": "Fragen Sie nach Veranstaltungen",
                    "keywords": ["vorstellung", "programm", "heute", "wann", "was"],
                    "required": True,
                    "hint": "Fragen Sie: 'Was gibt es heute?' oder 'Welche Vorstellungen haben Sie?'",
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "description": "Kaufen Sie Tickets",
                    "keywords": ["karten", "tickets", "zwei", "plätze", "möchte"],
                    "required": True,
                    "hint": "Sagen Sie: 'Ich möchte zwei Karten für...'",
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "description": "Fragen Sie nach Details",
                    "keywords": ["dauer", "pause", "beginn", "ende", "inhalt"],
                    "required": False,
                    "hint": "Fragen Sie: 'Wann beginnt die Vorstellung?' oder 'Wie lange dauert es?'",
                    "xp_reward": 50,
                    "difficulty_level": 3
                }
            ],
            "context": "Buying theater tickets. Discuss available shows, times, prices, and seating.",
            "system_prompt": "Du bist Frau Wagner, eine begeisterte Theaterkartenverkäuferin. Empfehle Vorstellungen, erkläre Inhalte, verkaufe Karten.",
            "xp_reward": 150,
            "bonus_xp": 75,
            "tags": ["culture", "entertainment", "intermediate", "leisure"]
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
            "characters": [{
                "name": "Max",
                "role": "fitness_trainer",
                "personality": "energetic and motivating",
                "personality_traits": {
                    "friendliness": 10,
                    "formality": 4,
                    "patience": 8,
                    "helpfulness": 9,
                    "chattiness": 9
                },
                "emotion": {
                    "current": "energetic",
                    "intensity": 9,
                    "triggers": {
                        "interest_in_fitness": "excited",
                        "goals": "motivating"
                    }
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Motivierender Fitnesstrainer",
                "greeting": "Hey! Willkommen im Gym! Bist du neu hier?",
                "remembers_user": True,
                "memory": {}
            }],
            "objectives": [
                {
                    "description": "Sagen Sie, dass Sie sich anmelden möchten",
                    "keywords": ["anmelden", "mitglied", "werden", "möchte", "mitgliedschaft"],
                    "required": True,
                    "hint": "Sagen Sie: 'Ich möchte mich anmelden'",
                    "xp_reward": 40,
                    "difficulty_level": 1
                },
                {
                    "description": "Fragen Sie nach Kursen",
                    "keywords": ["kurse", "yoga", "zumba", "training", "angebot"],
                    "required": True,
                    "hint": "Fragen Sie: 'Welche Kurse bieten Sie an?'",
                    "xp_reward": 40,
                    "difficulty_level": 1
                },
                {
                    "description": "Besprechen Sie Ihre Fitnessziele",
                    "keywords": ["abnehmen", "muskeln", "fit", "gesund", "ziel"],
                    "required": False,
                    "hint": "Sagen Sie: 'Ich möchte...' oder 'Mein Ziel ist...'",
                    "xp_reward": 50,
                    "difficulty_level": 2
                }
            ],
            "context": "Joining a gym. Discuss membership, available classes, equipment, and fitness goals.",
            "system_prompt": "Du bist Max, ein energischer Fitnesstrainer. Sei motivierend, erkläre Kurse und Mitgliedschaftsoptionen, frage nach Fitnesszielen.",
            "xp_reward": 110,
            "bonus_xp": 55,
            "tags": ["sports", "fitness", "health", "beginner", "casual"]
        },
        
        # 10. Technology Support
        {
            "name": "Technischer Support",
            "title_en": "Tech Support",
            "description": "Ihr Computer hat ein Problem. Beschreiben Sie das Problem und verstehen Sie die Lösung.",
            "description_en": "Your computer has a problem. Describe the issue and understand the solution.",
            "difficulty": "intermediate",
            "category": "technology",
            "estimated_duration": 13,
            "icon": "💻",
            "characters": [{
                "name": "Herr Klein",
                "role": "tech_support",
                "personality": "patient and technical",
                "personality_traits": {
                    "friendliness": 7,
                    "formality": 6,
                    "patience": 10,
                    "helpfulness": 10,
                    "chattiness": 6
                },
                "emotion": {
                    "current": "helpful",
                    "intensity": 7,
                    "triggers": {
                        "frustrated_user": "patient",
                        "clear_description": "efficient"
                    }
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Geduldiger IT-Support-Mitarbeiter",
                "greeting": "Guten Tag! IT-Support, Herr Klein. Was kann ich für Sie tun?",
                "remembers_user": False,
                "memory": {}
            }],
            "objectives": [
                {
                    "description": "Beschreiben Sie das Problem",
                    "keywords": ["funktioniert", "nicht", "problem", "fehler", "geht"],
                    "required": True,
                    "hint": "Sagen Sie: 'Mein Computer funktioniert nicht' oder 'Ich habe ein Problem mit...'",
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "description": "Beantworten Sie technische Fragen",
                    "keywords": ["fehlermeldung", "wann", "passiert", "version", "update"],
                    "required": True,
                    "hint": "Der Techniker fragt nach Details. Antworten Sie so genau wie möglich.",
                    "xp_reward": 60,
                    "difficulty_level": 3
                },
                {
                    "description": "Folgen Sie den Anweisungen",
                    "keywords": ["klicken", "öffnen", "neustart", "versuchen", "okay"],
                    "required": True,
                    "hint": "Hören Sie zu und bestätigen Sie: 'Okay, ich versuche es'",
                    "xp_reward": 50,
                    "difficulty_level": 2
                }
            ],
            "context": "Tech support call. Describe computer problem, answer technical questions, follow troubleshooting steps.",
            "system_prompt": "Du bist Herr Klein, ein geduldiger IT-Support-Mitarbeiter. Stelle klare Fragen, gib Schritt-für-Schritt-Anweisungen, sei verständnisvoll.",
            "xp_reward": 160,
            "bonus_xp": 80,
            "tags": ["technology", "support", "intermediate", "practical"]
        }
    ]
    
    # Insert remaining 5 scenarios
    for scenario_data in scenarios:
        scenario = Scenario(**scenario_data)
        result = await scenarios_collection.insert_one(scenario.model_dump(by_alias=True, exclude={"id"}))
        print(f"✅ Created: {scenario.name} (ID: {result.inserted_id})")
    
    print(f"\n✅ Successfully seeded all 5 remaining scenarios!")
    print(f"🎉 Total: 10 advanced scenarios complete!")

if __name__ == "__main__":
    asyncio.run(seed_remaining_scenarios())
