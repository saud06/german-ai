"""
Seed script for 10 advanced life simulation scenarios
Phase 4 - Week 7
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import get_db
from app.models.scenario import (
    Scenario, Character, Objective, PersonalityTrait, Emotion,
    DialogueBranch, DecisionPoint
)
from datetime import datetime

async def seed_advanced_scenarios():
    """Seed 10 new advanced scenarios"""
    db = await get_db()
    scenarios_collection = db.scenarios
    
    print("🎮 Seeding 10 Advanced Scenarios...")
    
    scenarios = [
        # 1. Doctor Visit
        {
            "name": "Beim Arzt",
            "title_en": "Doctor Visit",
            "description": "Sie fühlen sich krank und besuchen einen Arzt. Beschreiben Sie Ihre Symptome und verstehen Sie die Diagnose.",
            "description_en": "You're feeling sick and visiting a doctor. Describe your symptoms and understand the diagnosis.",
            "difficulty": "intermediate",
            "category": "medical",
            "estimated_duration": 12,
            "icon": "🏥",
            "characters": [{
                "name": "Dr. Weber",
                "role": "doctor",
                "personality": "professional and caring",
                "personality_traits": {
                    "friendliness": 8,
                    "formality": 9,
                    "patience": 9,
                    "helpfulness": 10,
                    "chattiness": 6
                },
                "emotion": {
                    "current": "professional",
                    "intensity": 7,
                    "triggers": {
                        "patient_worried": "reassuring",
                        "symptoms_serious": "concerned"
                    }
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Erfahrener Hausarzt, der sich Zeit für seine Patienten nimmt",
                "greeting": "Guten Tag! Setzen Sie sich bitte. Was führt Sie heute zu mir?",
                "remembers_user": True,
                "memory": {}
            }],
            "objectives": [
                {
                    "description": "Beschreiben Sie Ihre Symptome",
                    "keywords": ["kopfschmerzen", "fieber", "husten", "halsschmerzen", "schmerzen"],
                    "required": True,
                    "hint": "Sagen Sie: 'Ich habe...' oder 'Mir tut... weh'",
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "description": "Beantworten Sie Fragen des Arztes",
                    "keywords": ["seit", "tage", "gestern", "heute", "woche"],
                    "required": True,
                    "hint": "Der Arzt fragt: 'Seit wann haben Sie die Beschwerden?'",
                    "xp_reward": 40,
                    "difficulty_level": 2
                },
                {
                    "description": "Verstehen Sie die Diagnose",
                    "keywords": ["verstehe", "okay", "danke", "rezept", "medikament"],
                    "required": True,
                    "hint": "Fragen Sie: 'Was soll ich tun?' oder 'Brauche ich Medikamente?'",
                    "xp_reward": 60,
                    "difficulty_level": 3
                }
            ],
            "context": "Patient visits doctor with flu-like symptoms. Doctor asks about symptoms, duration, and prescribes medication.",
            "system_prompt": "Du bist Dr. Weber, ein erfahrener und geduldiger Hausarzt. Frage nach Symptomen, stelle Diagnose und verschreibe Medikamente. Sei professionell aber freundlich.",
            "xp_reward": 150,
            "bonus_xp": 75,
            "tags": ["medical", "health", "intermediate"]
        },
        
        # 2. Job Interview
        {
            "name": "Vorstellungsgespräch",
            "title_en": "Job Interview",
            "description": "Sie haben ein Vorstellungsgespräch für eine neue Position. Präsentieren Sie sich professionell.",
            "description_en": "You have a job interview for a new position. Present yourself professionally.",
            "difficulty": "advanced",
            "category": "professional",
            "estimated_duration": 18,
            "icon": "💼",
            "characters": [{
                "name": "Frau Schmidt",
                "role": "hr_manager",
                "personality": "formal and evaluative",
                "personality_traits": {
                    "friendliness": 6,
                    "formality": 10,
                    "patience": 7,
                    "helpfulness": 6,
                    "chattiness": 5
                },
                "emotion": {
                    "current": "professional",
                    "intensity": 8,
                    "triggers": {
                        "good_answer": "impressed",
                        "poor_answer": "skeptical"
                    }
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Personalmanagerin mit hohen Standards",
                "greeting": "Guten Tag! Schön, dass Sie da sind. Bitte nehmen Sie Platz. Erzählen Sie mir etwas über sich.",
                "remembers_user": False,
                "memory": {}
            }],
            "objectives": [
                {
                    "description": "Stellen Sie sich vor",
                    "keywords": ["name", "studiert", "erfahrung", "arbeit", "qualifikation"],
                    "required": True,
                    "hint": "Beginnen Sie mit: 'Mein Name ist... Ich habe... studiert'",
                    "xp_reward": 60,
                    "difficulty_level": 4
                },
                {
                    "description": "Beschreiben Sie Ihre Qualifikationen",
                    "keywords": ["fähigkeiten", "können", "erfahrung", "projekt", "erfolg"],
                    "required": True,
                    "hint": "Sprechen Sie über Ihre Stärken und Erfahrungen",
                    "xp_reward": 70,
                    "difficulty_level": 4
                },
                {
                    "description": "Stellen Sie Fragen zur Position",
                    "keywords": ["aufgaben", "team", "arbeitszeit", "gehalt", "benefits"],
                    "required": False,
                    "hint": "Fragen Sie: 'Können Sie mir mehr über... erzählen?'",
                    "xp_reward": 50,
                    "difficulty_level": 3
                }
            ],
            "context": "Professional job interview. Candidate must present qualifications, answer questions, and ask about the position.",
            "system_prompt": "Du bist Frau Schmidt, eine professionelle Personalmanagerin. Stelle Fragen zu Qualifikationen, Erfahrung und Motivation. Sei formal aber fair.",
            "xp_reward": 200,
            "bonus_xp": 100,
            "tags": ["professional", "career", "advanced"]
        },
        
        # 3. Making Friends
        {
            "name": "Neue Freunde finden",
            "title_en": "Making Friends",
            "description": "Sie treffen jemanden Neues und möchten Freundschaft schließen. Finden Sie gemeinsame Interessen.",
            "description_en": "You meet someone new and want to make friends. Find common interests.",
            "difficulty": "beginner",
            "category": "social",
            "estimated_duration": 10,
            "icon": "👥",
            "characters": [{
                "name": "Emma",
                "role": "student",
                "personality": "friendly and casual",
                "personality_traits": {
                    "friendliness": 10,
                    "formality": 3,
                    "patience": 8,
                    "helpfulness": 9,
                    "chattiness": 9
                },
                "emotion": {
                    "current": "happy",
                    "intensity": 8,
                    "triggers": {
                        "common_interest": "excited",
                        "friendly_response": "pleased"
                    }
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Freundliche Studentin, die gerne neue Leute kennenlernt",
                "greeting": "Hey! Ich bin Emma. Bist du auch neu hier?",
                "remembers_user": True,
                "memory": {}
            }],
            "objectives": [
                {
                    "description": "Stellen Sie sich vor",
                    "keywords": ["name", "heiße", "bin", "komme"],
                    "required": True,
                    "hint": "Sagen Sie: 'Ich heiße...' oder 'Ich bin...'",
                    "xp_reward": 30,
                    "difficulty_level": 1
                },
                {
                    "description": "Sprechen Sie über Hobbys",
                    "keywords": ["hobby", "gerne", "mag", "sport", "musik", "lesen"],
                    "required": True,
                    "hint": "Fragen Sie: 'Was machst du gerne?' oder 'Hast du Hobbys?'",
                    "xp_reward": 40,
                    "difficulty_level": 1
                },
                {
                    "description": "Machen Sie Pläne zusammen",
                    "keywords": ["treffen", "zusammen", "wann", "morgen", "kaffee"],
                    "required": False,
                    "hint": "Schlagen Sie vor: 'Wollen wir zusammen... ?'",
                    "xp_reward": 50,
                    "difficulty_level": 2
                }
            ],
            "context": "Meeting a new person and trying to make friends. Casual conversation about interests and hobbies.",
            "system_prompt": "Du bist Emma, eine freundliche und offene Studentin. Sei interessiert an der anderen Person, stelle Fragen und teile deine Interessen.",
            "xp_reward": 100,
            "bonus_xp": 50,
            "tags": ["social", "friends", "beginner", "casual"]
        },
        
        # 4. Public Transport
        {
            "name": "Mit öffentlichen Verkehrsmitteln",
            "title_en": "Public Transport",
            "description": "Sie müssen ein Ticket kaufen und nach dem Weg fragen.",
            "description_en": "You need to buy a ticket and ask for directions.",
            "difficulty": "beginner",
            "category": "transport",
            "estimated_duration": 7,
            "icon": "🚇",
            "characters": [{
                "name": "Herr Müller",
                "role": "ticket_agent",
                "personality": "helpful but busy",
                "personality_traits": {
                    "friendliness": 7,
                    "formality": 6,
                    "patience": 6,
                    "helpfulness": 8,
                    "chattiness": 4
                },
                "emotion": {
                    "current": "neutral",
                    "intensity": 5,
                    "triggers": {
                        "clear_request": "helpful",
                        "confused": "patient"
                    }
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Ticketverkäufer am Bahnhof",
                "greeting": "Guten Tag! Was kann ich für Sie tun?",
                "remembers_user": False,
                "memory": {}
            }],
            "objectives": [
                {
                    "description": "Kaufen Sie ein Ticket",
                    "keywords": ["ticket", "fahrkarte", "nach", "möchte", "brauche"],
                    "required": True,
                    "hint": "Sagen Sie: 'Ich möchte ein Ticket nach...'",
                    "xp_reward": 40,
                    "difficulty_level": 1
                },
                {
                    "description": "Fragen Sie nach dem Preis",
                    "keywords": ["kostet", "preis", "euro", "bezahlen"],
                    "required": True,
                    "hint": "Fragen Sie: 'Was kostet das?' oder 'Wie viel?'",
                    "xp_reward": 30,
                    "difficulty_level": 1
                },
                {
                    "description": "Fragen Sie nach dem Gleis",
                    "keywords": ["gleis", "wo", "abfahrt", "zug", "bahn"],
                    "required": False,
                    "hint": "Fragen Sie: 'Von welchem Gleis fährt der Zug?'",
                    "xp_reward": 40,
                    "difficulty_level": 2
                }
            ],
            "context": "Buying a train ticket at the station. Need to specify destination, pay, and find the platform.",
            "system_prompt": "Du bist ein Ticketverkäufer am Bahnhof. Sei hilfsbereit aber effizient. Gib klare Informationen über Preise und Gleise.",
            "xp_reward": 90,
            "bonus_xp": 40,
            "tags": ["transport", "travel", "beginner", "practical"]
        },
        
        # 5. Bank Visit
        {
            "name": "Bei der Bank",
            "title_en": "Bank Visit",
            "description": "Sie möchten ein Konto eröffnen und Informationen über Bankdienstleistungen erhalten.",
            "description_en": "You want to open an account and get information about banking services.",
            "difficulty": "intermediate",
            "category": "financial",
            "estimated_duration": 14,
            "icon": "🏦",
            "characters": [{
                "name": "Frau Becker",
                "role": "bank_advisor",
                "personality": "professional and formal",
                "personality_traits": {
                    "friendliness": 7,
                    "formality": 9,
                    "patience": 8,
                    "helpfulness": 9,
                    "chattiness": 6
                },
                "emotion": {
                    "current": "professional",
                    "intensity": 7,
                    "triggers": {
                        "interested_customer": "pleased",
                        "questions": "helpful"
                    }
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Bankberaterin mit viel Erfahrung",
                "greeting": "Guten Tag! Willkommen bei unserer Bank. Wie kann ich Ihnen helfen?",
                "remembers_user": False,
                "memory": {}
            }],
            "objectives": [
                {
                    "description": "Sagen Sie, dass Sie ein Konto eröffnen möchten",
                    "keywords": ["konto", "eröffnen", "möchte", "brauche", "girokonto"],
                    "required": True,
                    "hint": "Sagen Sie: 'Ich möchte ein Konto eröffnen'",
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "description": "Fragen Sie nach den Konditionen",
                    "keywords": ["gebühren", "kosten", "zinsen", "konditionen", "kostenlos"],
                    "required": True,
                    "hint": "Fragen Sie: 'Welche Gebühren fallen an?'",
                    "xp_reward": 60,
                    "difficulty_level": 3
                },
                {
                    "description": "Verstehen Sie die Anforderungen",
                    "keywords": ["ausweis", "dokumente", "brauche", "mitbringen", "unterschrift"],
                    "required": True,
                    "hint": "Fragen Sie: 'Was brauche ich dafür?'",
                    "xp_reward": 50,
                    "difficulty_level": 2
                }
            ],
            "context": "Opening a bank account. Discuss account types, fees, requirements, and services.",
            "system_prompt": "Du bist Frau Becker, eine professionelle Bankberaterin. Erkläre Kontoarten, Gebühren und Anforderungen klar und verständlich.",
            "xp_reward": 160,
            "bonus_xp": 80,
            "tags": ["financial", "banking", "intermediate", "formal"]
        }
    ]
    
    # Insert first 5 scenarios
    for scenario_data in scenarios:
        scenario = Scenario(**scenario_data)
        result = await scenarios_collection.insert_one(scenario.model_dump(by_alias=True, exclude={"id"}))
        print(f"✅ Created: {scenario.name} (ID: {result.inserted_id})")
    
    print(f"\n✅ Successfully seeded 5 scenarios!")
    print("Run part 2 script for remaining 5 scenarios...")

if __name__ == "__main__":
    asyncio.run(seed_advanced_scenarios())
