"""
Seed journey content mappings for existing scenarios, quizzes, and other content
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "german_ai")

# Scenario mappings based on existing 10 scenarios
SCENARIO_MAPPINGS = {
    "restaurant": {
        "purposes": ["traveler", "hobby"],
        "priority": {"student": 4, "traveler": 10, "professional": 5, "hobby": 8},
        "level_tags": ["A2", "Beginner", "Intermediate"],
        "topic_tags": ["travel", "food", "conversation"]
    },
    "hotel": {
        "purposes": ["traveler", "professional"],
        "priority": {"student": 5, "traveler": 10, "professional": 7, "hobby": 6},
        "level_tags": ["A2", "B1", "Beginner", "Intermediate"],
        "topic_tags": ["travel", "accommodation", "formal"]
    },
    "supermarket": {
        "purposes": ["traveler", "hobby"],
        "priority": {"student": 6, "traveler": 9, "professional": 4, "hobby": 8},
        "level_tags": ["A1", "A2", "Beginner"],
        "topic_tags": ["shopping", "daily_life", "food"]
    },
    "doctor": {
        "purposes": ["traveler", "professional"],
        "priority": {"student": 7, "traveler": 8, "professional": 8, "hobby": 5},
        "level_tags": ["B1", "Intermediate", "Advanced"],
        "topic_tags": ["health", "emergency", "formal"]
    },
    "train_station": {
        "purposes": ["traveler", "student"],
        "priority": {"student": 7, "traveler": 10, "professional": 6, "hobby": 7},
        "level_tags": ["A2", "B1", "Beginner", "Intermediate"],
        "topic_tags": ["travel", "transportation", "directions"]
    },
    "bank": {
        "purposes": ["professional", "traveler"],
        "priority": {"student": 6, "traveler": 7, "professional": 9, "hobby": 4},
        "level_tags": ["B1", "B2", "Intermediate", "Advanced"],
        "topic_tags": ["finance", "formal", "business"]
    },
    "pharmacy": {
        "purposes": ["traveler", "hobby"],
        "priority": {"student": 6, "traveler": 9, "professional": 5, "hobby": 7},
        "level_tags": ["A2", "B1", "Beginner", "Intermediate"],
        "topic_tags": ["health", "shopping", "daily_life"]
    },
    "post_office": {
        "purposes": ["traveler", "professional"],
        "priority": {"student": 5, "traveler": 8, "professional": 7, "hobby": 6},
        "level_tags": ["A2", "B1", "Beginner", "Intermediate"],
        "topic_tags": ["services", "formal", "daily_life"]
    },
    "apartment_viewing": {
        "purposes": ["professional", "traveler"],
        "priority": {"student": 7, "traveler": 8, "professional": 9, "hobby": 5},
        "level_tags": ["B1", "B2", "Intermediate", "Advanced"],
        "topic_tags": ["housing", "formal", "negotiation"]
    },
    "job_interview": {
        "purposes": ["professional", "student"],
        "priority": {"student": 8, "traveler": 3, "professional": 10, "hobby": 4},
        "level_tags": ["B2", "C1", "Advanced"],
        "topic_tags": ["career", "formal", "business"]
    }
}

# Quiz topic mappings
QUIZ_TOPIC_MAPPINGS = {
    "articles": {
        "purposes": ["student", "hobby"],
        "priority": {"student": 10, "traveler": 5, "professional": 6, "hobby": 7},
        "level_tags": ["A1", "A2", "Beginner"],
        "topic_tags": ["grammar", "fundamentals"]
    },
    "verbs": {
        "purposes": ["student", "professional"],
        "priority": {"student": 10, "traveler": 6, "professional": 8, "hobby": 6},
        "level_tags": ["A2", "B1", "Beginner", "Intermediate"],
        "topic_tags": ["grammar", "verbs"]
    },
    "cases": {
        "purposes": ["student", "professional"],
        "priority": {"student": 10, "traveler": 4, "professional": 7, "hobby": 5},
        "level_tags": ["B1", "B2", "Intermediate", "Advanced"],
        "topic_tags": ["grammar", "cases"]
    },
    "vocabulary": {
        "purposes": ["student", "traveler", "hobby"],
        "priority": {"student": 9, "traveler": 9, "professional": 7, "hobby": 9},
        "level_tags": ["A1", "A2", "B1", "Beginner", "Intermediate"],
        "topic_tags": ["vocabulary", "words"]
    },
    "pronunciation": {
        "purposes": ["traveler", "hobby"],
        "priority": {"student": 6, "traveler": 10, "professional": 7, "hobby": 9},
        "level_tags": ["A1", "A2", "Beginner"],
        "topic_tags": ["pronunciation", "speaking"]
    }
}

# Grammar topic mappings
GRAMMAR_MAPPINGS = {
    "sentence_structure": {
        "purposes": ["student", "professional"],
        "priority": {"student": 10, "traveler": 5, "professional": 8, "hobby": 6},
        "level_tags": ["A2", "B1", "Intermediate"],
        "topic_tags": ["grammar", "syntax"]
    },
    "adjective_endings": {
        "purposes": ["student", "professional"],
        "priority": {"student": 10, "traveler": 4, "professional": 7, "hobby": 5},
        "level_tags": ["B1", "B2", "Intermediate", "Advanced"],
        "topic_tags": ["grammar", "adjectives"]
    },
    "prepositions": {
        "purposes": ["student", "traveler"],
        "priority": {"student": 9, "traveler": 8, "professional": 7, "hobby": 7},
        "level_tags": ["A2", "B1", "Beginner", "Intermediate"],
        "topic_tags": ["grammar", "prepositions"]
    }
}

async def seed_content_mappings():
    """Seed content mappings for journeys"""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DB_NAME]
    
    print("🌱 Seeding journey content mappings...")
    
    # Clear existing mappings
    await db.journey_content_mappings.delete_many({})
    print("   Cleared existing mappings")
    
    mappings_to_insert = []
    
    # Get all scenarios and create mappings
    scenarios = await db.scenarios.find({}).to_list(length=100)
    print(f"\n📍 Processing {len(scenarios)} scenarios...")
    
    for scenario in scenarios:
        scenario_name = scenario.get("name", "").lower().replace(" ", "_")
        
        # Try to find mapping by name or category
        mapping_data = None
        for key, data in SCENARIO_MAPPINGS.items():
            if key in scenario_name or key.replace("_", " ") in scenario.get("name", "").lower():
                mapping_data = data
                break
        
        # Default mapping if not found
        if not mapping_data:
            mapping_data = {
                "purposes": ["student", "traveler", "hobby"],
                "priority": {"student": 5, "traveler": 5, "professional": 5, "hobby": 5},
                "level_tags": ["A2", "B1", "Beginner", "Intermediate"],
                "topic_tags": ["conversation", "practice"]
            }
        
        mappings_to_insert.append({
            "content_type": "scenario",
            "content_id": str(scenario["_id"]),
            "purposes": mapping_data["purposes"],
            "priority_by_purpose": mapping_data["priority"],
            "level_tags": mapping_data["level_tags"],
            "topic_tags": mapping_data["topic_tags"],
            "created_at": datetime.utcnow()
        })
        print(f"   ✓ Mapped scenario: {scenario.get('name')} → {', '.join(mapping_data['purposes'])}")
    
    # Get all quizzes and create mappings
    quizzes = await db.quizzes.find({}).to_list(length=100)
    print(f"\n📝 Processing {len(quizzes)} quizzes...")
    
    for quiz in quizzes:
        quiz_track = quiz.get("track", "vocabulary").lower()
        
        # Find mapping by track
        mapping_data = QUIZ_TOPIC_MAPPINGS.get(quiz_track)
        
        # Default mapping if not found
        if not mapping_data:
            mapping_data = {
                "purposes": ["student", "hobby"],
                "priority": {"student": 8, "traveler": 5, "professional": 6, "hobby": 7},
                "level_tags": ["A2", "B1", "Beginner", "Intermediate"],
                "topic_tags": ["practice", "quiz"]
            }
        
        mappings_to_insert.append({
            "content_type": "quiz",
            "content_id": str(quiz["_id"]),
            "purposes": mapping_data["purposes"],
            "priority_by_purpose": mapping_data["priority"],
            "level_tags": mapping_data["level_tags"],
            "topic_tags": mapping_data["topic_tags"],
            "created_at": datetime.utcnow()
        })
        print(f"   ✓ Mapped quiz: {quiz.get('track', 'Unknown')} → {', '.join(mapping_data['purposes'])}")
    
    # Get vocabulary and create mappings
    vocab_items = await db.vocab.find({}).to_list(length=100)
    print(f"\n📚 Processing {len(vocab_items)} vocabulary items...")
    
    for vocab in vocab_items:
        mappings_to_insert.append({
            "content_type": "vocab",
            "content_id": str(vocab["_id"]),
            "purposes": ["student", "traveler", "hobby"],
            "priority_by_purpose": {"student": 8, "traveler": 9, "professional": 7, "hobby": 9},
            "level_tags": ["A1", "A2", "Beginner"],
            "topic_tags": ["vocabulary", "words"],
            "created_at": datetime.utcnow()
        })
    
    if vocab_items:
        print(f"   ✓ Mapped {len(vocab_items)} vocabulary items")
    
    # Insert all mappings
    if mappings_to_insert:
        result = await db.journey_content_mappings.insert_many(mappings_to_insert)
        print(f"\n✅ Inserted {len(result.inserted_ids)} content mappings")
    
    # Verify
    count = await db.journey_content_mappings.count_documents({})
    print(f"📊 Total mappings in database: {count}")
    
    # Show summary by content type
    print("\n📋 Mappings Summary:")
    for content_type in ["scenario", "quiz", "vocab"]:
        type_count = await db.journey_content_mappings.count_documents({"content_type": content_type})
        print(f"   • {content_type}: {type_count} items")
    
    client.close()
    print("\n✅ Content mappings seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_content_mappings())
