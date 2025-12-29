#!/usr/bin/env python3
"""
Complete Learning System Seed Script
Seeds all interconnected data: learning paths, locations, scenarios, vocab, quizzes, grammar
"""
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from bson import ObjectId
from datetime import datetime

# Load environment variables
load_dotenv()

async def seed_learning_system():
    """Seed the complete learning system with interconnected data"""
    
    mongodb_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME", "german_ai")
    
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]
    
    print("🧹 Cleaning existing learning data...")
    
    # Clear existing data
    await db.learning_paths.delete_many({})
    await db.locations.delete_many({})
    await db.scenarios.delete_many({})
    await db.vocab_sets.delete_many({})
    await db.quizzes.delete_many({})
    await db.grammar_exercises.delete_many({})
    await db.characters.delete_many({})
    await db.user_progress.delete_many({})
    
    print("✅ Cleared existing data")
    
    # ========================================================================
    # CHAPTER 1: BASICS (A1 Level)
    # ========================================================================
    
    print("\n📚 Creating Chapter 1: German Basics...")
    
    chapter1_id = ObjectId()
    
    # Create characters for Chapter 1
    anna_id = ObjectId()
    max_id = ObjectId()
    
    characters = [
        {
            "_id": anna_id,
            "name": "Anna",
            "role": "Friendly Barista",
            "personality": "warm, patient, encouraging",
            "description": "A friendly barista who loves helping beginners practice German",
            "greeting": "Hallo! Willkommen im Café. Wie kann ich dir helfen?",
            "voice_id": "de_DE-thorsten-high",
            "personality_traits": {"patience": 10, "friendliness": 10},
            "emotion": {"current": "happy"},
            "remembers_user": True,
            "memory": {}
        },
        {
            "_id": max_id,
            "name": "Max",
            "role": "Shop Assistant",
            "personality": "helpful, clear speaker, supportive",
            "description": "A shop assistant who speaks slowly and clearly for learners",
            "greeting": "Guten Tag! Was möchtest du kaufen?",
            "voice_id": "de_DE-thorsten-high",
            "personality_traits": {"patience": 9, "helpfulness": 10},
            "emotion": {"current": "friendly"},
            "remembers_user": True,
            "memory": {}
        }
    ]
    
    await db.characters.insert_many(characters)
    print(f"  ✓ Created {len(characters)} characters")
    
    # Location 1: Café
    cafe_location_id = ObjectId()
    
    # Scenario 1: Ordering Coffee
    coffee_scenario_id = ObjectId()
    coffee_scenario = {
        "_id": coffee_scenario_id,
        "name": "Ordering Coffee",
        "description": "Learn to order drinks and snacks at a German café",
        "difficulty": "beginner",
        "category": "daily_life",
        "estimated_duration": 5,
        "xp_reward": 100,
        "icon": "☕",
        "characters": [str(anna_id)],
        "objectives": [
            {
                "id": "greet",
                "description": "Greet Anna",
                "keywords": ["hallo", "guten tag", "hi"],
                "completed": False,
                "hint": "Say 'Hallo' or 'Guten Tag'"
            },
            {
                "id": "order_drink",
                "description": "Order a drink",
                "keywords": ["kaffee", "tee", "wasser", "möchte", "hätte gern"],
                "completed": False,
                "hint": "Try 'Ich möchte einen Kaffee, bitte'"
            },
            {
                "id": "thank",
                "description": "Say thank you",
                "keywords": ["danke", "vielen dank"],
                "completed": False,
                "hint": "Say 'Danke' or 'Vielen Dank'"
            }
        ],
        "context": "You're at a cozy German café. Anna is behind the counter, ready to take your order.",
        "created_at": datetime.utcnow()
    }
    
    await db.scenarios.insert_one(coffee_scenario)
    
    # Vocab Set 1: Café Vocabulary
    cafe_vocab_id = ObjectId()
    cafe_vocab = {
        "_id": cafe_vocab_id,
        "title": "Café Basics",
        "description": "Essential vocabulary for ordering at a café",
        "level": "A1",
        "location_id": str(cafe_location_id),
        "xp_reward": 50,
        "estimated_minutes": 10,
        "words": [
            {"german": "der Kaffee", "english": "coffee", "example": "Ich möchte einen Kaffee."},
            {"german": "der Tee", "english": "tea", "example": "Ein Tee, bitte."},
            {"german": "das Wasser", "english": "water", "example": "Ein Glas Wasser, bitte."},
            {"german": "die Milch", "english": "milk", "example": "Mit Milch, bitte."},
            {"german": "der Zucker", "english": "sugar", "example": "Ohne Zucker, bitte."},
            {"german": "das Brötchen", "english": "bread roll", "example": "Ein Brötchen mit Butter."},
            {"german": "möchte", "english": "would like", "example": "Ich möchte einen Kaffee."},
            {"german": "bitte", "english": "please", "example": "Ein Kaffee, bitte."},
            {"german": "danke", "english": "thank you", "example": "Danke schön!"},
            {"german": "kosten", "english": "to cost", "example": "Was kostet das?"}
        ],
        "created_at": datetime.utcnow()
    }
    
    await db.vocab_sets.insert_one(cafe_vocab)
    
    # Quiz 1: Café Quiz
    cafe_quiz_id = ObjectId()
    cafe_quiz = {
        "_id": cafe_quiz_id,
        "title": "Café Vocabulary Quiz",
        "description": "Test your café vocabulary knowledge",
        "level": "A1",
        "location_id": str(cafe_location_id),
        "xp_reward": 30,
        "estimated_minutes": 5,
        "questions": [
            {
                "question": "How do you say 'I would like a coffee' in German?",
                "options": [
                    "Ich möchte einen Kaffee",
                    "Ich bin Kaffee",
                    "Ich habe Kaffee",
                    "Ich trinke Kaffee"
                ],
                "correct_answer": "Ich möchte einen Kaffee",
                "explanation": "'Möchte' means 'would like' and is used for polite requests."
            },
            {
                "question": "What is 'please' in German?",
                "options": ["bitte", "danke", "gern", "ja"],
                "correct_answer": "bitte",
                "explanation": "'Bitte' is used to say 'please' and also 'you're welcome'."
            },
            {
                "question": "How do you say 'thank you' in German?",
                "options": ["bitte", "hallo", "danke", "tschüss"],
                "correct_answer": "danke",
                "explanation": "'Danke' means 'thank you'. You can also say 'Danke schön' for emphasis."
            }
        ],
        "created_at": datetime.utcnow()
    }
    
    await db.quizzes.insert_one(cafe_quiz)
    
    # Create Café Location
    cafe_location = {
        "_id": cafe_location_id,
        "chapter_id": str(chapter1_id),
        "name": "Das Café",
        "description": "A cozy German café where you'll learn basic greetings and ordering",
        "type": "scenario",
        "image": "/images/locations/cafe.jpg",
        "position": {"x": 100, "y": 150},
        "estimated_minutes": 20,
        "scenarios": [str(coffee_scenario_id)],
        "characters": [str(anna_id)],
        "unlock_requirements": {},
        "rewards": {
            "xp": 150,
            "badge": "Coffee Lover"
        },
        "created_at": datetime.utcnow()
    }
    
    await db.locations.insert_one(cafe_location)
    print(f"  ✓ Created Café location with scenario, vocab, and quiz")
    
    # Location 2: Supermarket
    supermarket_location_id = ObjectId()
    
    # Scenario 2: Shopping
    shopping_scenario_id = ObjectId()
    shopping_scenario = {
        "_id": shopping_scenario_id,
        "name": "Shopping for Groceries",
        "description": "Learn to shop for basic items at a German supermarket",
        "difficulty": "beginner",
        "category": "daily_life",
        "estimated_duration": 5,
        "xp_reward": 100,
        "icon": "🛒",
        "characters": [str(max_id)],
        "objectives": [
            {
                "id": "greet",
                "description": "Greet Max",
                "keywords": ["hallo", "guten tag"],
                "completed": False,
                "hint": "Say 'Guten Tag'"
            },
            {
                "id": "ask_price",
                "description": "Ask for the price",
                "keywords": ["kostet", "preis", "wie viel"],
                "completed": False,
                "hint": "Try 'Was kostet das?'"
            },
            {
                "id": "say_goodbye",
                "description": "Say goodbye",
                "keywords": ["tschüss", "auf wiedersehen", "bis bald"],
                "completed": False,
                "hint": "Say 'Tschüss' or 'Auf Wiedersehen'"
            }
        ],
        "context": "You're at a German supermarket. Max is there to help you find what you need.",
        "created_at": datetime.utcnow()
    }
    
    await db.scenarios.insert_one(shopping_scenario)
    
    # Vocab Set 2: Shopping Vocabulary
    shopping_vocab_id = ObjectId()
    shopping_vocab = {
        "_id": shopping_vocab_id,
        "title": "Shopping Essentials",
        "description": "Basic vocabulary for grocery shopping",
        "level": "A1",
        "location_id": str(supermarket_location_id),
        "xp_reward": 50,
        "estimated_minutes": 10,
        "words": [
            {"german": "das Brot", "english": "bread", "example": "Ich kaufe Brot."},
            {"german": "die Milch", "english": "milk", "example": "Eine Flasche Milch, bitte."},
            {"german": "das Obst", "english": "fruit", "example": "Ich esse gern Obst."},
            {"german": "das Gemüse", "english": "vegetables", "example": "Frisches Gemüse ist gesund."},
            {"german": "der Apfel", "english": "apple", "example": "Ein Kilo Äpfel, bitte."},
            {"german": "die Banane", "english": "banana", "example": "Ich mag Bananen."},
            {"german": "kaufen", "english": "to buy", "example": "Ich kaufe Brot."},
            {"german": "kosten", "english": "to cost", "example": "Was kostet das?"},
            {"german": "bezahlen", "english": "to pay", "example": "Ich möchte bezahlen."},
            {"german": "die Kasse", "english": "checkout", "example": "Wo ist die Kasse?"}
        ],
        "created_at": datetime.utcnow()
    }
    
    await db.vocab_sets.insert_one(shopping_vocab)
    
    # Quiz 2: Shopping Quiz
    shopping_quiz_id = ObjectId()
    shopping_quiz = {
        "_id": shopping_quiz_id,
        "title": "Shopping Vocabulary Quiz",
        "description": "Test your shopping vocabulary",
        "level": "A1",
        "location_id": str(supermarket_location_id),
        "xp_reward": 30,
        "estimated_minutes": 5,
        "questions": [
            {
                "question": "What is 'bread' in German?",
                "options": ["das Brot", "die Milch", "der Käse", "das Wasser"],
                "correct_answer": "das Brot",
                "explanation": "'Das Brot' is bread. It's a neuter noun."
            },
            {
                "question": "How do you ask 'How much does it cost?'",
                "options": [
                    "Was kostet das?",
                    "Wie heißt das?",
                    "Wo ist das?",
                    "Wann kommt das?"
                ],
                "correct_answer": "Was kostet das?",
                "explanation": "'Was kostet das?' literally means 'What costs that?'"
            }
        ],
        "created_at": datetime.utcnow()
    }
    
    await db.quizzes.insert_one(shopping_quiz)
    
    # Create Supermarket Location
    supermarket_location = {
        "_id": supermarket_location_id,
        "chapter_id": str(chapter1_id),
        "name": "Der Supermarkt",
        "description": "A German supermarket where you'll learn shopping vocabulary",
        "type": "scenario",
        "image": "/images/locations/supermarket.jpg",
        "position": {"x": 300, "y": 200},
        "estimated_minutes": 20,
        "scenarios": [str(shopping_scenario_id)],
        "characters": [str(max_id)],
        "unlock_requirements": {"chapter_progress": 30},
        "rewards": {
            "xp": 150,
            "badge": "Smart Shopper"
        },
        "created_at": datetime.utcnow()
    }
    
    await db.locations.insert_one(supermarket_location)
    print(f"  ✓ Created Supermarket location with scenario, vocab, and quiz")
    
    # Grammar Exercise for Chapter 1
    grammar1_id = ObjectId()
    grammar1 = {
        "_id": grammar1_id,
        "chapter_id": str(chapter1_id),
        "title": "Basic Articles (der, die, das)",
        "description": "Learn the three German articles and when to use them",
        "level": "A1",
        "xp_reward": 40,
        "estimated_minutes": 8,
        "rule": "German has three articles: der (masculine), die (feminine), das (neuter)",
        "examples": [
            "der Kaffee (masculine)",
            "die Milch (feminine)",
            "das Brot (neuter)"
        ],
        "exercises": [
            {
                "sentence": "___ Kaffee ist heiß.",
                "correct": "Der Kaffee ist heiß.",
                "explanation": "Kaffee is masculine, so we use 'der'"
            },
            {
                "sentence": "___ Milch ist kalt.",
                "correct": "Die Milch ist kalt.",
                "explanation": "Milch is feminine, so we use 'die'"
            }
        ],
        "created_at": datetime.utcnow()
    }
    
    await db.grammar_exercises.insert_one(grammar1)
    print(f"  ✓ Created grammar exercise for Chapter 1")
    
    # Create Chapter 1
    chapter1 = {
        "_id": chapter1_id,
        "chapter": 1,
        "title": "German Basics",
        "description": "Start your German journey with everyday situations",
        "story": "Welcome to Germany! You've just arrived and need to learn the basics to navigate daily life. Start with simple conversations at a café and shopping at the supermarket.",
        "image": "/images/chapters/chapter1.jpg",
        "level": "A1",
        "estimated_hours": 2,
        "locations": [str(cafe_location_id), str(supermarket_location_id)],
        "characters": [str(anna_id), str(max_id)],
        "unlock_requirements": {},
        "completion_reward": {
            "xp": 500,
            "badge": "German Beginner",
            "unlock": "Chapter 2"
        },
        "created_at": datetime.utcnow()
    }
    
    await db.learning_paths.insert_one(chapter1)
    print(f"✅ Chapter 1 complete: 2 locations, 2 scenarios, 2 vocab sets, 2 quizzes, 1 grammar")
    
    # ========================================================================
    # CHAPTER 2: TRAVEL (A1-A2 Level)
    # ========================================================================
    
    print("\n📚 Creating Chapter 2: Travel & Transportation...")
    
    chapter2_id = ObjectId()
    
    # Create character for Chapter 2
    petra_id = ObjectId()
    petra = {
        "_id": petra_id,
        "name": "Petra",
        "role": "Train Station Agent",
        "personality": "professional, helpful, efficient",
        "description": "A train station agent who helps travelers",
        "greeting": "Guten Tag! Wie kann ich Ihnen helfen?",
        "voice_id": "de_DE-thorsten-high",
        "personality_traits": {"professionalism": 10, "helpfulness": 9},
        "emotion": {"current": "professional"},
        "remembers_user": True,
        "memory": {}
    }
    
    await db.characters.insert_one(petra)
    
    # Location: Train Station
    station_location_id = ObjectId()
    
    # Scenario: Buying Train Ticket
    ticket_scenario_id = ObjectId()
    ticket_scenario = {
        "_id": ticket_scenario_id,
        "name": "Buying a Train Ticket",
        "description": "Learn to buy tickets and ask about train schedules",
        "difficulty": "intermediate",
        "category": "travel",
        "estimated_duration": 7,
        "xp_reward": 150,
        "icon": "🚂",
        "characters": [str(petra_id)],
        "objectives": [
            {
                "id": "greet",
                "description": "Greet Petra",
                "keywords": ["guten tag", "hallo"],
                "completed": False,
                "hint": "Say 'Guten Tag'"
            },
            {
                "id": "ask_ticket",
                "description": "Ask for a ticket",
                "keywords": ["fahrkarte", "ticket", "nach", "möchte"],
                "completed": False,
                "hint": "Try 'Ich möchte eine Fahrkarte nach Berlin'"
            },
            {
                "id": "ask_time",
                "description": "Ask about departure time",
                "keywords": ["wann", "abfahrt", "uhr"],
                "completed": False,
                "hint": "Ask 'Wann fährt der Zug ab?'"
            }
        ],
        "context": "You're at a German train station. Petra can help you buy tickets.",
        "created_at": datetime.utcnow()
    }
    
    await db.scenarios.insert_one(ticket_scenario)
    
    # Vocab Set: Travel Vocabulary
    travel_vocab_id = ObjectId()
    travel_vocab = {
        "_id": travel_vocab_id,
        "title": "Travel Essentials",
        "description": "Essential vocabulary for traveling by train",
        "level": "A2",
        "location_id": str(station_location_id),
        "xp_reward": 50,
        "estimated_minutes": 12,
        "words": [
            {"german": "der Zug", "english": "train", "example": "Der Zug fährt um 10 Uhr."},
            {"german": "die Fahrkarte", "english": "ticket", "example": "Ich brauche eine Fahrkarte."},
            {"german": "der Bahnhof", "english": "train station", "example": "Wo ist der Bahnhof?"},
            {"german": "die Abfahrt", "english": "departure", "example": "Wann ist die Abfahrt?"},
            {"german": "die Ankunft", "english": "arrival", "example": "Die Ankunft ist um 15 Uhr."},
            {"german": "das Gleis", "english": "platform", "example": "Der Zug fährt von Gleis 3."},
            {"german": "einfach", "english": "one-way", "example": "Eine einfache Fahrkarte, bitte."},
            {"german": "hin und zurück", "english": "round-trip", "example": "Hin und zurück nach München."},
            {"german": "umsteigen", "english": "to change trains", "example": "Muss ich umsteigen?"},
            {"german": "verspätet", "english": "delayed", "example": "Der Zug ist verspätet."}
        ],
        "created_at": datetime.utcnow()
    }
    
    await db.vocab_sets.insert_one(travel_vocab)
    
    # Quiz: Travel Quiz
    travel_quiz_id = ObjectId()
    travel_quiz = {
        "_id": travel_quiz_id,
        "title": "Travel Vocabulary Quiz",
        "description": "Test your travel vocabulary",
        "level": "A2",
        "location_id": str(station_location_id),
        "xp_reward": 30,
        "estimated_minutes": 5,
        "questions": [
            {
                "question": "What is 'train' in German?",
                "options": ["der Zug", "der Bus", "das Auto", "das Flugzeug"],
                "correct_answer": "der Zug",
                "explanation": "'Der Zug' means train. It's a masculine noun."
            },
            {
                "question": "How do you say 'round-trip' in German?",
                "options": ["einfach", "hin und zurück", "umsteigen", "verspätet"],
                "correct_answer": "hin und zurück",
                "explanation": "'Hin und zurück' literally means 'there and back'."
            }
        ],
        "created_at": datetime.utcnow()
    }
    
    await db.quizzes.insert_one(travel_quiz)
    
    # Create Station Location
    station_location = {
        "_id": station_location_id,
        "chapter_id": str(chapter2_id),
        "name": "Der Bahnhof",
        "description": "The train station where you'll learn travel vocabulary",
        "type": "scenario",
        "image": "/images/locations/train_station.jpg",
        "position": {"x": 150, "y": 100},
        "estimated_minutes": 25,
        "scenarios": [str(ticket_scenario_id)],
        "characters": [str(petra_id)],
        "unlock_requirements": {},
        "rewards": {
            "xp": 200,
            "badge": "Train Master"
        },
        "created_at": datetime.utcnow()
    }
    
    await db.locations.insert_one(station_location)
    print(f"  ✓ Created Train Station location with scenario, vocab, and quiz")
    
    # Grammar Exercise for Chapter 2
    grammar2_id = ObjectId()
    grammar2 = {
        "_id": grammar2_id,
        "chapter_id": str(chapter2_id),
        "title": "Modal Verbs (möchte, kann, muss)",
        "description": "Learn essential modal verbs for expressing wants and needs",
        "level": "A2",
        "xp_reward": 40,
        "estimated_minutes": 10,
        "rule": "Modal verbs express ability, permission, or necessity",
        "examples": [
            "Ich möchte eine Fahrkarte. (I would like a ticket)",
            "Ich kann Deutsch sprechen. (I can speak German)",
            "Ich muss umsteigen. (I must change trains)"
        ],
        "exercises": [
            {
                "sentence": "Ich ___ eine Fahrkarte kaufen.",
                "correct": "Ich möchte eine Fahrkarte kaufen.",
                "explanation": "Use 'möchte' to express 'would like to'"
            }
        ],
        "created_at": datetime.utcnow()
    }
    
    await db.grammar_exercises.insert_one(grammar2)
    print(f"  ✓ Created grammar exercise for Chapter 2")
    
    # Create Chapter 2
    chapter2 = {
        "_id": chapter2_id,
        "chapter": 2,
        "title": "Travel & Transportation",
        "description": "Learn to navigate German transportation systems",
        "story": "Now that you know the basics, it's time to explore Germany! Learn how to buy train tickets, ask for directions, and travel confidently.",
        "image": "/images/chapters/chapter2.jpg",
        "level": "A2",
        "estimated_hours": 2,
        "locations": [str(station_location_id)],
        "characters": [str(petra_id)],
        "unlock_requirements": {"min_xp": 300},
        "completion_reward": {
            "xp": 400,
            "badge": "German Traveler",
            "unlock": "Chapter 3"
        },
        "created_at": datetime.utcnow()
    }
    
    await db.learning_paths.insert_one(chapter2)
    print(f"✅ Chapter 2 complete: 1 location, 1 scenario, 1 vocab set, 1 quiz, 1 grammar")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print("\n" + "="*60)
    print("✅ LEARNING SYSTEM SEEDED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  • Chapters: 2")
    print(f"  • Locations: 3")
    print(f"  • Scenarios: 3")
    print(f"  • Characters: 3")
    print(f"  • Vocab Sets: 3")
    print(f"  • Quizzes: 3")
    print(f"  • Grammar Exercises: 2")
    print(f"\n🎯 All data is properly interconnected:")
    print(f"  • Each location belongs to a chapter")
    print(f"  • Each scenario is linked to a location")
    print(f"  • Each vocab set is linked to a location")
    print(f"  • Each quiz is linked to a location")
    print(f"  • Each grammar exercise is linked to a chapter")
    print(f"  • All IDs are properly referenced")
    print(f"\n🚀 Ready to use!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_learning_system())
