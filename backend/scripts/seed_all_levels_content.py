"""
Seed comprehensive content at all CEFR levels (A1, A2, B1, B2, C1)
This ensures users at different journey levels get appropriate content
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "german_learning")

async def seed_vocabulary():
    """Seed vocabulary at all CEFR levels"""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    print("📚 Seeding vocabulary at all levels...")
    
    # Clear existing
    await db.seed_words.delete_many({})
    
    vocab_by_level = {
        "A1": [
            {"word": "der Tisch", "translation": "the table", "examples": ["Der Tisch ist groß."]},
            {"word": "das Haus", "translation": "the house", "examples": ["Ich gehe nach Hause."]},
            {"word": "die Katze", "translation": "the cat", "examples": ["Die Katze ist süß."]},
            {"word": "der Hund", "translation": "the dog", "examples": ["Der Hund bellt."]},
            {"word": "das Buch", "translation": "the book", "examples": ["Ich lese ein Buch."]},
            {"word": "die Tür", "translation": "the door", "examples": ["Die Tür ist offen."]},
            {"word": "das Fenster", "translation": "the window", "examples": ["Das Fenster ist groß."]},
            {"word": "der Stuhl", "translation": "the chair", "examples": ["Der Stuhl ist bequem."]},
            {"word": "das Wasser", "translation": "the water", "examples": ["Ich trinke Wasser."]},
            {"word": "das Brot", "translation": "the bread", "examples": ["Das Brot ist frisch."]},
        ],
        "A2": [
            {"word": "die Schule", "translation": "the school", "examples": ["Ich gehe zur Schule."]},
            {"word": "der Lehrer", "translation": "the teacher", "examples": ["Der Lehrer ist nett."]},
            {"word": "die Arbeit", "translation": "the work", "examples": ["Die Arbeit ist schwer."]},
            {"word": "der Freund", "translation": "the friend", "examples": ["Mein Freund kommt heute."]},
            {"word": "die Familie", "translation": "the family", "examples": ["Meine Familie ist groß."]},
            {"word": "das Auto", "translation": "the car", "examples": ["Das Auto ist schnell."]},
            {"word": "die Stadt", "translation": "the city", "examples": ["Die Stadt ist schön."]},
            {"word": "der Bahnhof", "translation": "the train station", "examples": ["Der Bahnhof ist nah."]},
            {"word": "das Restaurant", "translation": "the restaurant", "examples": ["Das Restaurant ist gut."]},
            {"word": "die Wohnung", "translation": "the apartment", "examples": ["Die Wohnung ist klein."]},
        ],
        "B1": [
            {"word": "der Vorschlag", "translation": "the proposal", "examples": ["Ich mache einen Vorschlag."]},
            {"word": "die Meinung", "translation": "the opinion", "examples": ["Das ist meine Meinung."]},
            {"word": "die Erfahrung", "translation": "the experience", "examples": ["Ich habe viel Erfahrung."]},
            {"word": "die Entscheidung", "translation": "the decision", "examples": ["Das ist eine schwere Entscheidung."]},
            {"word": "der Unterschied", "translation": "the difference", "examples": ["Was ist der Unterschied?"]},
            {"word": "die Entwicklung", "translation": "the development", "examples": ["Die Entwicklung ist positiv."]},
            {"word": "die Verantwortung", "translation": "the responsibility", "examples": ["Das ist meine Verantwortung."]},
            {"word": "die Gelegenheit", "translation": "the opportunity", "examples": ["Das ist eine gute Gelegenheit."]},
            {"word": "der Zusammenhang", "translation": "the context", "examples": ["Im Zusammenhang mit..."]},
            {"word": "die Bedingung", "translation": "the condition", "examples": ["Unter welchen Bedingungen?"]},
        ],
        "B2": [
            {"word": "die Herausforderung", "translation": "the challenge", "examples": ["Das ist eine große Herausforderung."]},
            {"word": "die Auseinandersetzung", "translation": "the debate", "examples": ["Die Auseinandersetzung war intensiv."]},
            {"word": "die Voraussetzung", "translation": "the prerequisite", "examples": ["Was sind die Voraussetzungen?"]},
            {"word": "die Beziehung", "translation": "the relationship", "examples": ["Unsere Beziehung ist gut."]},
            {"word": "die Eigenschaft", "translation": "the characteristic", "examples": ["Das ist eine wichtige Eigenschaft."]},
            {"word": "die Auswirkung", "translation": "the impact", "examples": ["Die Auswirkungen sind groß."]},
            {"word": "die Berücksichtigung", "translation": "the consideration", "examples": ["Unter Berücksichtigung von..."]},
            {"word": "die Gewährleistung", "translation": "the guarantee", "examples": ["Die Gewährleistung ist wichtig."]},
            {"word": "die Verständigung", "translation": "the communication", "examples": ["Die Verständigung war schwierig."]},
            {"word": "die Bewältigung", "translation": "the coping", "examples": ["Die Bewältigung der Krise."]},
        ],
        "C1": [
            {"word": "die Gegebenheit", "translation": "the circumstance", "examples": ["Unter den gegebenen Gegebenheiten..."]},
            {"word": "die Veranschaulichung", "translation": "the illustration", "examples": ["Zur Veranschaulichung..."]},
            {"word": "die Unabdingbarkeit", "translation": "the indispensability", "examples": ["Die Unabdingbarkeit dieser Maßnahme."]},
            {"word": "die Zweckmäßigkeit", "translation": "the expediency", "examples": ["Die Zweckmäßigkeit ist fraglich."]},
            {"word": "die Nachvollziehbarkeit", "translation": "the comprehensibility", "examples": ["Die Nachvollziehbarkeit ist wichtig."]},
            {"word": "die Unverzichtbarkeit", "translation": "the indispensability", "examples": ["Die Unverzichtbarkeit dieser Regel."]},
            {"word": "die Verhältnismäßigkeit", "translation": "the proportionality", "examples": ["Die Verhältnismäßigkeit prüfen."]},
            {"word": "die Unumgänglichkeit", "translation": "the inevitability", "examples": ["Die Unumgänglichkeit der Änderung."]},
            {"word": "die Rechtmäßigkeit", "translation": "the legality", "examples": ["Die Rechtmäßigkeit anzweifeln."]},
            {"word": "die Gesetzmäßigkeit", "translation": "the regularity", "examples": ["Die Gesetzmäßigkeit erkennen."]},
        ]
    }
    
    words_to_insert = []
    for level, words in vocab_by_level.items():
        for word_data in words:
            words_to_insert.append({
                "level": level,
                "word": word_data["word"],
                "translation": word_data["translation"],
                "examples": word_data["examples"],
                "source": "db",
                "created_at": datetime.utcnow()
            })
    
    if words_to_insert:
        await db.seed_words.insert_many(words_to_insert)
        print(f"✅ Inserted {len(words_to_insert)} vocabulary words across all levels")
    
    client.close()

async def seed_scenarios():
    """Seed scenarios at all CEFR levels"""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    print("🎭 Seeding scenarios at all levels...")
    
    # Clear existing
    await db.scenarios.delete_many({})
    
    scenarios = [
        # A1 Scenarios
        {
            "name": "Im Café",
            "title_en": "At the Café",
            "description": "Bestellen Sie einen Kaffee und ein Stück Kuchen.",
            "description_en": "Order a coffee and a piece of cake.",
            "difficulty": "A1",
            "category": "restaurant",
            "estimated_duration": 5,
            "icon": "☕",
            "characters": [{
                "id": str(ObjectId()),
                "name": "Anna",
                "role": "waitress",
                "personality": "friendly and helpful",
                "description": "Eine freundliche Kellnerin",
                "greeting": "Hallo! Was möchten Sie bestellen?"
            }],
            "objectives": [
                {"id": str(ObjectId()), "description": "Bestellen Sie ein Getränk", "required": True}
            ],
            "xp_reward": 50,
            "created_at": datetime.utcnow()
        },
        {
            "name": "Im Supermarkt",
            "title_en": "At the Supermarket",
            "description": "Kaufen Sie Obst und Gemüse.",
            "description_en": "Buy fruits and vegetables.",
            "difficulty": "A1",
            "category": "shopping",
            "estimated_duration": 5,
            "icon": "🛒",
            "characters": [{
                "id": str(ObjectId()),
                "name": "Klaus",
                "role": "cashier",
                "personality": "helpful",
                "description": "Ein hilfsbereiter Kassierer",
                "greeting": "Guten Tag! Haben Sie alles gefunden?"
            }],
            "objectives": [
                {"id": str(ObjectId()), "description": "Kaufen Sie Obst", "required": True}
            ],
            "xp_reward": 50,
            "created_at": datetime.utcnow()
        },
        # A2 Scenarios
        {
            "name": "Am Bahnhof",
            "title_en": "At the Train Station",
            "description": "Kaufen Sie eine Fahrkarte nach Berlin.",
            "description_en": "Buy a ticket to Berlin.",
            "difficulty": "A2",
            "category": "transport",
            "estimated_duration": 8,
            "icon": "🚂",
            "characters": [{
                "id": str(ObjectId()),
                "name": "Herr Schmidt",
                "role": "ticket seller",
                "personality": "professional",
                "description": "Ein professioneller Ticketverkäufer",
                "greeting": "Guten Tag! Wohin möchten Sie fahren?"
            }],
            "objectives": [
                {"id": str(ObjectId()), "description": "Kaufen Sie eine Fahrkarte", "required": True}
            ],
            "xp_reward": 75,
            "created_at": datetime.utcnow()
        },
        {
            "name": "In der Apotheke",
            "title_en": "At the Pharmacy",
            "description": "Holen Sie ein Medikament ab.",
            "description_en": "Pick up medicine.",
            "difficulty": "A2",
            "category": "medical",
            "estimated_duration": 8,
            "icon": "💊",
            "characters": [{
                "id": str(ObjectId()),
                "name": "Frau Müller",
                "role": "pharmacist",
                "personality": "caring",
                "description": "Eine fürsorgliche Apothekerin",
                "greeting": "Guten Tag! Wie kann ich Ihnen helfen?"
            }],
            "objectives": [
                {"id": str(ObjectId()), "description": "Holen Sie Ihr Medikament ab", "required": True}
            ],
            "xp_reward": 75,
            "created_at": datetime.utcnow()
        },
        # B1 Scenarios
        {
            "name": "Beim Arzt",
            "title_en": "At the Doctor",
            "description": "Beschreiben Sie Ihre Symptome beim Arzt.",
            "description_en": "Describe your symptoms to the doctor.",
            "difficulty": "B1",
            "category": "medical",
            "estimated_duration": 12,
            "icon": "🏥",
            "characters": [{
                "id": str(ObjectId()),
                "name": "Dr. Weber",
                "role": "doctor",
                "personality": "professional and caring",
                "description": "Ein erfahrener Arzt",
                "greeting": "Guten Tag! Was führt Sie heute zu mir?"
            }],
            "objectives": [
                {"id": str(ObjectId()), "description": "Beschreiben Sie Ihre Symptome", "required": True}
            ],
            "xp_reward": 100,
            "created_at": datetime.utcnow()
        },
        {
            "name": "Wohnungssuche",
            "title_en": "Apartment Hunting",
            "description": "Besichtigen Sie eine Wohnung und stellen Sie Fragen.",
            "description_en": "View an apartment and ask questions.",
            "difficulty": "B1",
            "category": "housing",
            "estimated_duration": 12,
            "icon": "🏠",
            "characters": [{
                "id": str(ObjectId()),
                "name": "Herr Fischer",
                "role": "landlord",
                "personality": "business-like",
                "description": "Ein Vermieter",
                "greeting": "Guten Tag! Möchten Sie die Wohnung sehen?"
            }],
            "objectives": [
                {"id": str(ObjectId()), "description": "Fragen Sie nach der Miete", "required": True}
            ],
            "xp_reward": 100,
            "created_at": datetime.utcnow()
        },
        # B2 Scenarios
        {
            "name": "Vorstellungsgespräch",
            "title_en": "Job Interview",
            "description": "Führen Sie ein Vorstellungsgespräch für eine Stelle.",
            "description_en": "Conduct a job interview.",
            "difficulty": "B2",
            "category": "professional",
            "estimated_duration": 15,
            "icon": "💼",
            "characters": [{
                "id": str(ObjectId()),
                "name": "Frau Schneider",
                "role": "HR manager",
                "personality": "professional and evaluative",
                "description": "Eine Personalleiterin",
                "greeting": "Guten Tag! Erzählen Sie mir etwas über sich."
            }],
            "objectives": [
                {"id": str(ObjectId()), "description": "Stellen Sie sich vor", "required": True}
            ],
            "xp_reward": 150,
            "created_at": datetime.utcnow()
        },
        {
            "name": "Geschäftsverhandlung",
            "title_en": "Business Negotiation",
            "description": "Verhandeln Sie einen Vertrag.",
            "description_en": "Negotiate a contract.",
            "difficulty": "B2",
            "category": "professional",
            "estimated_duration": 15,
            "icon": "📊",
            "characters": [{
                "id": str(ObjectId()),
                "name": "Herr Bauer",
                "role": "business partner",
                "personality": "strategic",
                "description": "Ein Geschäftspartner",
                "greeting": "Guten Tag! Lassen Sie uns über den Vertrag sprechen."
            }],
            "objectives": [
                {"id": str(ObjectId()), "description": "Verhandeln Sie die Konditionen", "required": True}
            ],
            "xp_reward": 150,
            "created_at": datetime.utcnow()
        },
        # C1 Scenarios
        {
            "name": "Akademische Diskussion",
            "title_en": "Academic Discussion",
            "description": "Diskutieren Sie ein komplexes Thema.",
            "description_en": "Discuss a complex topic.",
            "difficulty": "C1",
            "category": "academic",
            "estimated_duration": 20,
            "icon": "🎓",
            "characters": [{
                "id": str(ObjectId()),
                "name": "Prof. Dr. Hoffmann",
                "role": "professor",
                "personality": "intellectual and challenging",
                "description": "Ein Professor",
                "greeting": "Guten Tag! Lassen Sie uns über Ihre Forschung sprechen."
            }],
            "objectives": [
                {"id": str(ObjectId()), "description": "Präsentieren Sie Ihre Argumente", "required": True}
            ],
            "xp_reward": 200,
            "created_at": datetime.utcnow()
        },
        {
            "name": "Politische Debatte",
            "title_en": "Political Debate",
            "description": "Nehmen Sie an einer politischen Debatte teil.",
            "description_en": "Participate in a political debate.",
            "difficulty": "C1",
            "category": "politics",
            "estimated_duration": 20,
            "icon": "🏛️",
            "characters": [{
                "id": str(ObjectId()),
                "name": "Dr. Lehmann",
                "role": "politician",
                "personality": "persuasive and analytical",
                "description": "Ein Politiker",
                "greeting": "Guten Tag! Lassen Sie uns über die aktuellen Themen diskutieren."
            }],
            "objectives": [
                {"id": str(ObjectId()), "description": "Verteidigen Sie Ihre Position", "required": True}
            ],
            "xp_reward": 200,
            "created_at": datetime.utcnow()
        }
    ]
    
    if scenarios:
        await db.scenarios.insert_many(scenarios)
        print(f"✅ Inserted {len(scenarios)} scenarios across all levels")
    
    client.close()

async def main():
    """Run all seed functions"""
    print("🌱 Starting comprehensive content seeding...")
    print("=" * 60)
    
    await seed_vocabulary()
    await seed_scenarios()
    
    print("=" * 60)
    print("✅ All content seeded successfully!")
    print("\nContent summary:")
    print("  📚 Vocabulary: 50 words (10 per level: A1, A2, B1, B2, C1)")
    print("  🎭 Scenarios: 10 scenarios (2 per level: A1, A2, B1, B2, C1)")
    print("\nUsers will now see content appropriate to their journey level!")

if __name__ == "__main__":
    asyncio.run(main())
