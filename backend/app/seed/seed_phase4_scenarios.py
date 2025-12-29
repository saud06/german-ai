"""
Seed 10 new advanced scenarios for Phase 4
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

async def seed_phase4_scenarios():
    """Seed 10 new advanced scenarios"""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    print("🎭 Seeding Phase 4 Scenarios...")
    
    scenarios = [
        # 1. Doctor Visit
        {
            "name": "Beim Arzt",
            "title_en": "At the Doctor",
            "description": "Sie fühlen sich nicht gut und gehen zum Arzt. Beschreiben Sie Ihre Symptome und verstehen Sie die Diagnose.",
            "description_en": "You're not feeling well and visit the doctor. Describe your symptoms and understand the diagnosis.",
            "difficulty": "intermediate",
            "category": "medical",
            "estimated_duration": 12,
            "icon": "🏥",
            "tags": ["medical", "health", "symptoms", "diagnosis"],
            
            "characters": [{
                "id": str(ObjectId()),
                "name": "Dr. Weber",
                "role": "doctor",
                "personality": "caring and professional",
                "personality_traits": {
                    "friendliness": 8,
                    "formality": 7,
                    "patience": 9,
                    "helpfulness": 9,
                    "chattiness": 6
                },
                "emotion": {
                    "current": "professional",
                    "intensity": 5,
                    "triggers": {}
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Ein erfahrener Arzt, der sich Zeit nimmt, um Patienten zuzuhören.",
                "greeting": "Guten Tag! Setzen Sie sich bitte. Was führt Sie heute zu mir?",
                "remembers_user": True,
                "memory": {}
            }],
            
            "objectives": [
                {
                    "id": str(ObjectId()),
                    "description": "Beschreiben Sie Ihre Symptome",
                    "keywords": ["schmerzen", "kopfschmerzen", "fieber", "husten", "krank", "weh"],
                    "required": True,
                    "hint": "Sagen Sie: 'Ich habe...' oder 'Mir tut... weh'",
                    "completed": False,
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "id": str(ObjectId()),
                    "description": "Verstehen Sie die Diagnose",
                    "keywords": ["verstehe", "bedeutet", "was ist", "diagnose"],
                    "required": True,
                    "hint": "Fragen Sie: 'Was bedeutet das?' oder 'Ist es ernst?'",
                    "completed": False,
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "id": str(ObjectId()),
                    "description": "Fragen Sie nach der Behandlung",
                    "keywords": ["medikament", "behandlung", "therapie", "nehmen", "wie lange"],
                    "required": False,
                    "hint": "Fragen Sie: 'Welche Medikamente soll ich nehmen?'",
                    "completed": False,
                    "xp_reward": 30,
                    "difficulty_level": 2
                }
            ],
            
            "context": "You are Dr. Weber, a caring and professional doctor in Germany. The patient has come to you with health concerns. Listen carefully to their symptoms, ask relevant questions, provide a diagnosis, and explain treatment options. Use medical terminology but explain it clearly. Be empathetic and patient.",
            "system_prompt": "Du bist Dr. Weber, ein erfahrener und fürsorglicher Arzt. Höre dir die Symptome des Patienten an, stelle relevante Fragen, gib eine Diagnose und erkläre die Behandlung. Sei professionell aber freundlich.",
            
            "xp_reward": 150,
            "bonus_xp": 75,
            "has_time_limit": False,
            "has_checkpoints": False
        },
        
        # 2. Job Interview
        {
            "name": "Vorstellungsgespräch",
            "title_en": "Job Interview",
            "description": "Sie haben ein Vorstellungsgespräch für eine neue Stelle. Präsentieren Sie sich professionell.",
            "description_en": "You have a job interview for a new position. Present yourself professionally.",
            "difficulty": "advanced",
            "category": "professional",
            "estimated_duration": 18,
            "icon": "💼",
            "tags": ["job", "interview", "professional", "career"],
            
            "characters": [{
                "id": str(ObjectId()),
                "name": "Frau Schmidt",
                "role": "hr_manager",
                "personality": "formal and evaluative",
                "personality_traits": {
                    "friendliness": 6,
                    "formality": 9,
                    "patience": 7,
                    "helpfulness": 6,
                    "chattiness": 5
                },
                "emotion": {
                    "current": "professional",
                    "intensity": 6,
                    "triggers": {}
                },
                "voice_id": "de_DE-eva_k-x_low",
                "description": "Eine professionelle HR-Managerin, die Kandidaten sorgfältig bewertet.",
                "greeting": "Guten Tag! Schön, dass Sie da sind. Bitte nehmen Sie Platz. Erzählen Sie mir etwas über sich.",
                "remembers_user": False,
                "memory": {}
            }],
            
            "objectives": [
                {
                    "id": str(ObjectId()),
                    "description": "Stellen Sie sich vor",
                    "keywords": ["name", "ich bin", "komme aus", "studiert", "erfahrung"],
                    "required": True,
                    "hint": "Beginnen Sie mit: 'Mein Name ist...' und erzählen Sie über Ihre Ausbildung",
                    "completed": False,
                    "xp_reward": 60,
                    "difficulty_level": 3
                },
                {
                    "id": str(ObjectId()),
                    "description": "Beschreiben Sie Ihre Qualifikationen",
                    "keywords": ["qualifikation", "fähigkeiten", "erfahrung", "kompetenz", "kann"],
                    "required": True,
                    "hint": "Sagen Sie: 'Ich habe Erfahrung in...' oder 'Ich kann...'",
                    "completed": False,
                    "xp_reward": 60,
                    "difficulty_level": 3
                },
                {
                    "id": str(ObjectId()),
                    "description": "Stellen Sie Fragen über die Position",
                    "keywords": ["aufgaben", "team", "arbeitszeit", "gehalt", "urlaub"],
                    "required": False,
                    "hint": "Fragen Sie: 'Wie sieht ein typischer Arbeitstag aus?'",
                    "completed": False,
                    "xp_reward": 40,
                    "difficulty_level": 3
                }
            ],
            
            "context": "You are Frau Schmidt, a professional HR manager conducting a job interview. Evaluate the candidate's qualifications, experience, and fit for the position. Ask standard interview questions, listen carefully to answers, and provide information about the role. Maintain a professional but friendly demeanor.",
            "system_prompt": "Du bist Frau Schmidt, eine HR-Managerin. Führe ein professionelles Vorstellungsgespräch. Stelle Fragen über Qualifikationen, Erfahrung und Motivation. Sei höflich aber bewertend.",
            
            "xp_reward": 200,
            "bonus_xp": 100,
            "has_time_limit": False,
            "has_checkpoints": False
        },
        
        # 3. Making Friends
        {
            "name": "Neue Freunde finden",
            "title_en": "Making Friends",
            "description": "Sie treffen jemanden Neues an der Universität. Lernen Sie sich kennen und finden Sie gemeinsame Interessen.",
            "description_en": "You meet someone new at university. Get to know each other and find common interests.",
            "difficulty": "beginner",
            "category": "social",
            "estimated_duration": 10,
            "icon": "👥",
            "tags": ["friends", "social", "hobbies", "interests"],
            
            "characters": [{
                "id": str(ObjectId()),
                "name": "Emma",
                "role": "student",
                "personality": "friendly and casual",
                "personality_traits": {
                    "friendliness": 9,
                    "formality": 3,
                    "patience": 8,
                    "helpfulness": 8,
                    "chattiness": 9
                },
                "emotion": {
                    "current": "happy",
                    "intensity": 7,
                    "triggers": {}
                },
                "voice_id": "de_DE-eva_k-x_low",
                "description": "Eine freundliche Studentin, die gerne neue Leute kennenlernt.",
                "greeting": "Hey! Bist du auch neu hier? Ich bin Emma. Wie heißt du?",
                "remembers_user": True,
                "memory": {}
            }],
            
            "objectives": [
                {
                    "id": str(ObjectId()),
                    "description": "Stellen Sie sich vor",
                    "keywords": ["name", "ich bin", "heiße", "komme"],
                    "required": True,
                    "hint": "Sagen Sie: 'Ich heiße...' oder 'Ich bin...'",
                    "completed": False,
                    "xp_reward": 30,
                    "difficulty_level": 1
                },
                {
                    "id": str(ObjectId()),
                    "description": "Sprechen Sie über Hobbys",
                    "keywords": ["hobby", "mag", "gerne", "sport", "musik", "lesen"],
                    "required": True,
                    "hint": "Fragen Sie: 'Was machst du gerne?' oder sagen Sie: 'Ich mag...'",
                    "completed": False,
                    "xp_reward": 40,
                    "difficulty_level": 1
                },
                {
                    "id": str(ObjectId()),
                    "description": "Machen Sie Pläne",
                    "keywords": ["treffen", "zusammen", "kaffee", "kino", "wann", "morgen"],
                    "required": False,
                    "hint": "Fragen Sie: 'Wollen wir zusammen Kaffee trinken?'",
                    "completed": False,
                    "xp_reward": 30,
                    "difficulty_level": 1
                }
            ],
            
            "context": "You are Emma, a friendly university student who loves meeting new people. Be casual, enthusiastic, and interested in getting to know the other person. Share your hobbies, ask about theirs, and suggest activities you could do together. Use informal language (du).",
            "system_prompt": "Du bist Emma, eine freundliche Studentin. Sei locker und enthusiastisch. Teile deine Hobbys, frage nach ihren Interessen und schlage vor, etwas zusammen zu unternehmen. Benutze 'du'.",
            
            "xp_reward": 100,
            "bonus_xp": 50,
            "has_time_limit": False,
            "has_checkpoints": False
        },
        
        # 4. Public Transport
        {
            "name": "Öffentliche Verkehrsmittel",
            "title_en": "Public Transport",
            "description": "Sie müssen eine Fahrkarte kaufen und den richtigen Zug finden.",
            "description_en": "You need to buy a ticket and find the right train.",
            "difficulty": "beginner",
            "category": "transport",
            "estimated_duration": 7,
            "icon": "🚇",
            "tags": ["transport", "ticket", "directions", "travel"],
            
            "characters": [{
                "id": str(ObjectId()),
                "name": "Herr Bauer",
                "role": "ticket_agent",
                "personality": "helpful but busy",
                "personality_traits": {
                    "friendliness": 6,
                    "formality": 6,
                    "patience": 5,
                    "helpfulness": 8,
                    "chattiness": 4
                },
                "emotion": {
                    "current": "neutral",
                    "intensity": 5,
                    "triggers": {}
                },
                "voice_id": "de_DE-thorsten-high",
                "description": "Ein Fahrkartenschalter-Mitarbeiter, der hilfsbereit ist, aber viele Kunden hat.",
                "greeting": "Guten Tag! Der Nächste bitte. Wohin möchten Sie fahren?",
                "remembers_user": False,
                "memory": {}
            }],
            
            "objectives": [
                {
                    "id": str(ObjectId()),
                    "description": "Kaufen Sie eine Fahrkarte",
                    "keywords": ["fahrkarte", "ticket", "nach", "hin und zurück", "einfach"],
                    "required": True,
                    "hint": "Sagen Sie: 'Eine Fahrkarte nach... bitte'",
                    "completed": False,
                    "xp_reward": 40,
                    "difficulty_level": 1
                },
                {
                    "id": str(ObjectId()),
                    "description": "Fragen Sie nach dem Gleis",
                    "keywords": ["gleis", "wo", "abfahrt", "wann", "zug"],
                    "required": True,
                    "hint": "Fragen Sie: 'Von welchem Gleis fährt der Zug?'",
                    "completed": False,
                    "xp_reward": 30,
                    "difficulty_level": 1
                },
                {
                    "id": str(ObjectId()),
                    "description": "Fragen Sie nach der Dauer",
                    "keywords": ["wie lange", "dauer", "minuten", "stunden"],
                    "required": False,
                    "hint": "Fragen Sie: 'Wie lange dauert die Fahrt?'",
                    "completed": False,
                    "xp_reward": 20,
                    "difficulty_level": 1
                }
            ],
            
            "context": "You are Herr Bauer, a ticket agent at a train station. You're helpful but have many customers waiting. Provide clear, concise information about tickets, platforms, and schedules. Be efficient but polite.",
            "system_prompt": "Du bist Herr Bauer, ein Fahrkartenschalter-Mitarbeiter. Sei hilfsbereit aber effizient. Gib klare Informationen über Tickets, Gleise und Fahrpläne.",
            
            "xp_reward": 90,
            "bonus_xp": 45,
            "has_time_limit": False,
            "has_checkpoints": False
        },
        
        # 5. Bank Visit
        {
            "name": "Bei der Bank",
            "title_en": "At the Bank",
            "description": "Sie möchten ein Bankkonto eröffnen und Informationen über Dienstleistungen erhalten.",
            "description_en": "You want to open a bank account and get information about services.",
            "difficulty": "intermediate",
            "category": "financial",
            "estimated_duration": 13,
            "icon": "🏦",
            "tags": ["bank", "account", "money", "financial"],
            
            "characters": [{
                "id": str(ObjectId()),
                "name": "Frau Hoffmann",
                "role": "bank_advisor",
                "personality": "professional and formal",
                "personality_traits": {
                    "friendliness": 7,
                    "formality": 9,
                    "patience": 8,
                    "helpfulness": 8,
                    "chattiness": 6
                },
                "emotion": {
                    "current": "professional",
                    "intensity": 6,
                    "triggers": {}
                },
                "voice_id": "de_DE-eva_k-x_low",
                "description": "Eine professionelle Bankberaterin, die Kunden bei Finanzfragen hilft.",
                "greeting": "Guten Tag! Willkommen bei der Deutschen Bank. Wie kann ich Ihnen helfen?",
                "remembers_user": False,
                "memory": {}
            }],
            
            "objectives": [
                {
                    "id": str(ObjectId()),
                    "description": "Sagen Sie, was Sie möchten",
                    "keywords": ["konto", "eröffnen", "girokonto", "sparkonto", "möchte"],
                    "required": True,
                    "hint": "Sagen Sie: 'Ich möchte ein Konto eröffnen'",
                    "completed": False,
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "id": str(ObjectId()),
                    "description": "Fragen Sie nach Gebühren",
                    "keywords": ["gebühren", "kosten", "kostenlos", "preis", "monatlich"],
                    "required": True,
                    "hint": "Fragen Sie: 'Welche Gebühren fallen an?'",
                    "completed": False,
                    "xp_reward": 50,
                    "difficulty_level": 2
                },
                {
                    "id": str(ObjectId()),
                    "description": "Fragen Sie nach Online-Banking",
                    "keywords": ["online", "app", "banking", "internet", "zugang"],
                    "required": False,
                    "hint": "Fragen Sie: 'Gibt es Online-Banking?'",
                    "completed": False,
                    "xp_reward": 30,
                    "difficulty_level": 2
                }
            ],
            
            "context": "You are Frau Hoffmann, a professional bank advisor. Help the customer open an account, explain fees and services, and answer questions about online banking. Be formal, clear, and thorough in your explanations.",
            "system_prompt": "Du bist Frau Hoffmann, eine Bankberaterin. Hilf dem Kunden, ein Konto zu eröffnen. Erkläre Gebühren, Dienstleistungen und Online-Banking. Sei professionell und klar.",
            
            "xp_reward": 140,
            "bonus_xp": 70,
            "has_time_limit": False,
            "has_checkpoints": False
        }
    ]
    
    # Insert first 5 scenarios
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
    
    print(f"\n✅ Seeded {len(scenarios)} scenarios (Part 1/2)")
    print("\n📊 Summary:")
    print(f"  - Beginner: 2 scenarios")
    print(f"  - Intermediate: 2 scenarios")
    print(f"  - Advanced: 1 scenario")
    print(f"\n💡 Run seed_phase4_scenarios_part2.py for remaining 5 scenarios")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_phase4_scenarios())
