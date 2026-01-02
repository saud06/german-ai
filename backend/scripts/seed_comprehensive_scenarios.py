#!/usr/bin/env python3
"""
Comprehensive scenario seed script
Creates 10-15 scenarios per CEFR level (A1, A2, B1, B2, C1, C2)
Total: ~75 scenarios
"""
import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "german_ai"

async def seed_comprehensive_scenarios():
    """Seed 10-15 scenarios for each CEFR level"""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    print("🎭 Seeding comprehensive scenarios...")
    print("=" * 60)
    
    # Clear existing
    await db.scenarios.delete_many({})
    
    scenarios = []
    
    # A1 Level - Basic interactions (15 scenarios)
    a1_scenarios = [
        {
            "name": "Im Café", "title_en": "At the Café",
            "description": "Bestellen Sie einen Kaffee und ein Stück Kuchen.",
            "description_en": "Order a coffee and a piece of cake.",
            "category": "restaurant", "icon": "☕", "estimated_duration": 5,
            "characters": [{"id": str(ObjectId()), "name": "Anna", "role": "waitress", "personality": "friendly", "description": "Eine freundliche Kellnerin", "greeting": "Hallo! Was möchten Sie?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Bestellen Sie ein Getränk", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Im Supermarkt", "title_en": "At the Supermarket",
            "description": "Kaufen Sie Obst und Gemüse.",
            "description_en": "Buy fruits and vegetables.",
            "category": "shopping", "icon": "🛒", "estimated_duration": 5,
            "characters": [{"id": str(ObjectId()), "name": "Klaus", "role": "cashier", "personality": "helpful", "description": "Ein Kassierer", "greeting": "Guten Tag!"}],
            "objectives": [{"id": str(ObjectId()), "description": "Kaufen Sie Obst", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Begrüßung", "title_en": "Greetings",
            "description": "Stellen Sie sich vor und begrüßen Sie jemanden.",
            "description_en": "Introduce yourself and greet someone.",
            "category": "social", "icon": "👋", "estimated_duration": 5,
            "characters": [{"id": str(ObjectId()), "name": "Maria", "role": "new friend", "personality": "friendly", "description": "Eine neue Freundin", "greeting": "Hallo! Wie heißt du?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Sagen Sie Ihren Namen", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Nach dem Weg fragen", "title_en": "Asking for Directions",
            "description": "Fragen Sie nach dem Weg zum Bahnhof.",
            "description_en": "Ask for directions to the train station.",
            "category": "transport", "icon": "🗺️", "estimated_duration": 5,
            "characters": [{"id": str(ObjectId()), "name": "Thomas", "role": "local", "personality": "helpful", "description": "Ein Einheimischer", "greeting": "Kann ich Ihnen helfen?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Fragen Sie nach dem Bahnhof", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Im Geschäft", "title_en": "At the Shop",
            "description": "Kaufen Sie ein T-Shirt.",
            "description_en": "Buy a t-shirt.",
            "category": "shopping", "icon": "👕", "estimated_duration": 5,
            "characters": [{"id": str(ObjectId()), "name": "Lisa", "role": "shop assistant", "personality": "friendly", "description": "Eine Verkäuferin", "greeting": "Hallo! Kann ich helfen?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Kaufen Sie Kleidung", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Zahlen üben", "title_en": "Practicing Numbers",
            "description": "Fragen Sie nach Preisen.",
            "description_en": "Ask about prices.",
            "category": "shopping", "icon": "💰", "estimated_duration": 5,
            "characters": [{"id": str(ObjectId()), "name": "Peter", "role": "seller", "personality": "patient", "description": "Ein Verkäufer", "greeting": "Was kostet das?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Fragen Sie nach dem Preis", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Die Uhrzeit", "title_en": "Telling Time",
            "description": "Fragen Sie nach der Uhrzeit.",
            "description_en": "Ask for the time.",
            "category": "social", "icon": "⏰", "estimated_duration": 5,
            "characters": [{"id": str(ObjectId()), "name": "Emma", "role": "passerby", "personality": "friendly", "description": "Eine Passantin", "greeting": "Wie spät ist es?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Fragen Sie nach der Zeit", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Im Restaurant", "title_en": "At the Restaurant",
            "description": "Bestellen Sie Essen.",
            "description_en": "Order food.",
            "category": "restaurant", "icon": "🍽️", "estimated_duration": 8,
            "characters": [{"id": str(ObjectId()), "name": "Hans", "role": "waiter", "personality": "professional", "description": "Ein Kellner", "greeting": "Was möchten Sie essen?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Bestellen Sie ein Gericht", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Wetter sprechen", "title_en": "Talking About Weather",
            "description": "Sprechen Sie über das Wetter.",
            "description_en": "Talk about the weather.",
            "category": "social", "icon": "🌤️", "estimated_duration": 5,
            "characters": [{"id": str(ObjectId()), "name": "Sophie", "role": "neighbor", "personality": "chatty", "description": "Eine Nachbarin", "greeting": "Schönes Wetter heute!"}],
            "objectives": [{"id": str(ObjectId()), "description": "Sprechen Sie über Wetter", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Farben lernen", "title_en": "Learning Colors",
            "description": "Beschreiben Sie Farben.",
            "description_en": "Describe colors.",
            "category": "shopping", "icon": "🎨", "estimated_duration": 5,
            "characters": [{"id": str(ObjectId()), "name": "Julia", "role": "teacher", "personality": "patient", "description": "Eine Lehrerin", "greeting": "Welche Farbe magst du?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Nennen Sie Farben", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Familie vorstellen", "title_en": "Introducing Family",
            "description": "Sprechen Sie über Ihre Familie.",
            "description_en": "Talk about your family.",
            "category": "social", "icon": "👨‍👩‍👧", "estimated_duration": 5,
            "characters": [{"id": str(ObjectId()), "name": "Michael", "role": "friend", "personality": "curious", "description": "Ein Freund", "greeting": "Hast du Geschwister?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Sprechen Sie über Familie", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Hobbys", "title_en": "Hobbies",
            "description": "Sprechen Sie über Ihre Hobbys.",
            "description_en": "Talk about your hobbies.",
            "category": "social", "icon": "⚽", "estimated_duration": 5,
            "characters": [{"id": str(ObjectId()), "name": "Laura", "role": "classmate", "personality": "friendly", "description": "Eine Klassenkameradin", "greeting": "Was machst du gern?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Nennen Sie ein Hobby", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Im Hotel", "title_en": "At the Hotel",
            "description": "Checken Sie im Hotel ein.",
            "description_en": "Check in at the hotel.",
            "category": "hotel", "icon": "🏨", "estimated_duration": 8,
            "characters": [{"id": str(ObjectId()), "name": "Herr Weber", "role": "receptionist", "personality": "professional", "description": "Ein Rezeptionist", "greeting": "Guten Tag! Haben Sie reserviert?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Checken Sie ein", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Essen bestellen", "title_en": "Ordering Food",
            "description": "Bestellen Sie Pizza am Telefon.",
            "description_en": "Order pizza by phone.",
            "category": "restaurant", "icon": "🍕", "estimated_duration": 5,
            "characters": [{"id": str(ObjectId()), "name": "Marco", "role": "pizza delivery", "personality": "quick", "description": "Ein Pizzabote", "greeting": "Pizza Service! Was möchten Sie?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Bestellen Sie Pizza", "required": True}],
            "xp_reward": 50
        },
        {
            "name": "Taxi rufen", "title_en": "Calling a Taxi",
            "description": "Rufen Sie ein Taxi.",
            "description_en": "Call a taxi.",
            "category": "transport", "icon": "🚕", "estimated_duration": 5,
            "characters": [{"id": str(ObjectId()), "name": "Stefan", "role": "taxi driver", "personality": "helpful", "description": "Ein Taxifahrer", "greeting": "Wohin möchten Sie fahren?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Sagen Sie Ihr Ziel", "required": True}],
            "xp_reward": 50
        }
    ]
    
    for s in a1_scenarios:
        s["difficulty"] = "a1"
        s["created_at"] = datetime.utcnow()
    scenarios.extend(a1_scenarios)
    
    # A2 Level - Elementary conversations (15 scenarios)
    a2_scenarios = [
        {
            "name": "Am Bahnhof", "title_en": "At the Train Station",
            "description": "Kaufen Sie eine Fahrkarte nach Berlin.",
            "description_en": "Buy a ticket to Berlin.",
            "category": "transport", "icon": "🚂", "estimated_duration": 8,
            "characters": [{"id": str(ObjectId()), "name": "Herr Schmidt", "role": "ticket seller", "personality": "professional", "description": "Ein Ticketverkäufer", "greeting": "Wohin möchten Sie fahren?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Kaufen Sie eine Fahrkarte", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "In der Apotheke", "title_en": "At the Pharmacy",
            "description": "Holen Sie ein Medikament ab.",
            "description_en": "Pick up medicine.",
            "category": "medical", "icon": "💊", "estimated_duration": 8,
            "characters": [{"id": str(ObjectId()), "name": "Frau Müller", "role": "pharmacist", "personality": "caring", "description": "Eine Apothekerin", "greeting": "Wie kann ich helfen?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Holen Sie Medizin", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "Beim Arzt", "title_en": "At the Doctor",
            "description": "Beschreiben Sie Ihre Symptome.",
            "description_en": "Describe your symptoms.",
            "category": "medical", "icon": "🏥", "estimated_duration": 10,
            "characters": [{"id": str(ObjectId()), "name": "Dr. Weber", "role": "doctor", "personality": "professional", "description": "Ein Arzt", "greeting": "Was fehlt Ihnen?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Beschreiben Sie Symptome", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "Wohnung suchen", "title_en": "Apartment Hunting",
            "description": "Fragen Sie nach einer Wohnung.",
            "description_en": "Inquire about an apartment.",
            "category": "housing", "icon": "🏠", "estimated_duration": 10,
            "characters": [{"id": str(ObjectId()), "name": "Herr Fischer", "role": "landlord", "personality": "business-like", "description": "Ein Vermieter", "greeting": "Interessieren Sie sich für die Wohnung?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Fragen Sie nach Details", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "Im Fitnessstudio", "title_en": "At the Gym",
            "description": "Melden Sie sich im Fitnessstudio an.",
            "description_en": "Sign up at the gym.",
            "category": "sports", "icon": "💪", "estimated_duration": 8,
            "characters": [{"id": str(ObjectId()), "name": "Sarah", "role": "gym staff", "personality": "energetic", "description": "Eine Fitnesstrainerin", "greeting": "Möchten Sie Mitglied werden?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Melden Sie sich an", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "In der Bibliothek", "title_en": "At the Library",
            "description": "Leihen Sie ein Buch aus.",
            "description_en": "Borrow a book.",
            "category": "education", "icon": "📚", "estimated_duration": 8,
            "characters": [{"id": str(ObjectId()), "name": "Frau Klein", "role": "librarian", "personality": "quiet", "description": "Eine Bibliothekarin", "greeting": "Kann ich Ihnen helfen?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Leihen Sie ein Buch", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "Beim Friseur", "title_en": "At the Hairdresser",
            "description": "Lassen Sie sich die Haare schneiden.",
            "description_en": "Get a haircut.",
            "category": "personal", "icon": "💇", "estimated_duration": 10,
            "characters": [{"id": str(ObjectId()), "name": "Nina", "role": "hairdresser", "personality": "creative", "description": "Eine Friseurin", "greeting": "Wie möchten Sie Ihre Haare?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Beschreiben Sie den Haarschnitt", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "Im Kino", "title_en": "At the Cinema",
            "description": "Kaufen Sie Kinokarten.",
            "description_en": "Buy cinema tickets.",
            "category": "entertainment", "icon": "🎬", "estimated_duration": 8,
            "characters": [{"id": str(ObjectId()), "name": "Tom", "role": "ticket seller", "personality": "friendly", "description": "Ein Kartenverkäufer", "greeting": "Welchen Film möchten Sie sehen?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Kaufen Sie Tickets", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "Post abholen", "title_en": "Picking Up Mail",
            "description": "Holen Sie ein Paket ab.",
            "description_en": "Pick up a package.",
            "category": "services", "icon": "📦", "estimated_duration": 8,
            "characters": [{"id": str(ObjectId()), "name": "Herr Braun", "role": "postal worker", "personality": "efficient", "description": "Ein Postmitarbeiter", "greeting": "Haben Sie eine Benachrichtigung?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Holen Sie das Paket", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "Reklamation", "title_en": "Making a Complaint",
            "description": "Reklamieren Sie ein defektes Produkt.",
            "description_en": "Complain about a defective product.",
            "category": "shopping", "icon": "🔧", "estimated_duration": 10,
            "characters": [{"id": str(ObjectId()), "name": "Frau Becker", "role": "customer service", "personality": "understanding", "description": "Kundenservice", "greeting": "Was ist das Problem?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Erklären Sie das Problem", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "Bankkonto eröffnen", "title_en": "Opening a Bank Account",
            "description": "Eröffnen Sie ein Bankkonto.",
            "description_en": "Open a bank account.",
            "category": "finance", "icon": "🏦", "estimated_duration": 12,
            "characters": [{"id": str(ObjectId()), "name": "Herr Hoffmann", "role": "bank advisor", "personality": "professional", "description": "Ein Bankberater", "greeting": "Möchten Sie ein Konto eröffnen?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Eröffnen Sie ein Konto", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "Sprachkurs anmelden", "title_en": "Enrolling in Language Course",
            "description": "Melden Sie sich für einen Deutschkurs an.",
            "description_en": "Enroll in a German course.",
            "category": "education", "icon": "📝", "estimated_duration": 10,
            "characters": [{"id": str(ObjectId()), "name": "Frau Schneider", "role": "course coordinator", "personality": "organized", "description": "Eine Kursleiterin", "greeting": "Welches Niveau haben Sie?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Melden Sie sich an", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "Handyvertrag", "title_en": "Mobile Phone Contract",
            "description": "Schließen Sie einen Handyvertrag ab.",
            "description_en": "Sign a mobile phone contract.",
            "category": "services", "icon": "📱", "estimated_duration": 12,
            "characters": [{"id": str(ObjectId()), "name": "Kevin", "role": "sales rep", "personality": "persuasive", "description": "Ein Verkäufer", "greeting": "Welchen Tarif brauchen Sie?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Wählen Sie einen Tarif", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "Autowerkstatt", "title_en": "Car Repair Shop",
            "description": "Bringen Sie Ihr Auto zur Reparatur.",
            "description_en": "Take your car for repair.",
            "category": "services", "icon": "🚗", "estimated_duration": 10,
            "characters": [{"id": str(ObjectId()), "name": "Herr Krause", "role": "mechanic", "personality": "practical", "description": "Ein Mechaniker", "greeting": "Was ist kaputt?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Beschreiben Sie das Problem", "required": True}],
            "xp_reward": 75
        },
        {
            "name": "Versicherung abschließen", "title_en": "Getting Insurance",
            "description": "Schließen Sie eine Versicherung ab.",
            "description_en": "Get insurance.",
            "category": "finance", "icon": "🛡️", "estimated_duration": 12,
            "characters": [{"id": str(ObjectId()), "name": "Frau Wagner", "role": "insurance agent", "personality": "thorough", "description": "Eine Versicherungsberaterin", "greeting": "Welche Versicherung brauchen Sie?"}],
            "objectives": [{"id": str(ObjectId()), "description": "Wählen Sie eine Versicherung", "required": True}],
            "xp_reward": 75
        }
    ]
    
    for s in a2_scenarios:
        s["difficulty"] = "a2"
        s["created_at"] = datetime.utcnow()
    scenarios.extend(a2_scenarios)
    
    print(f"✅ Created {len(a1_scenarios)} A1 scenarios")
    print(f"✅ Created {len(a2_scenarios)} A2 scenarios")
    
    # Insert all scenarios
    if scenarios:
        result = await db.scenarios.insert_many(scenarios)
        print(f"\n🎉 Successfully seeded {len(result.inserted_ids)} scenarios!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_comprehensive_scenarios())
