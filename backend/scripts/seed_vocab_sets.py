"""
Seed vocabulary sets for learning path locations
Creates themed vocabulary sets linked to locations
"""
import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.config import get_settings

settings = get_settings()

async def seed_vocab_sets():
    """Create vocabulary sets for each location"""
    
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME or "german_ai"]
    
    print("🌱 Seeding Vocabulary Sets...")
    print("=" * 50)
    
    # Load comprehensive word list
    words_file = Path(__file__).parent.parent / "seed" / "german_words_comprehensive.json"
    with open(words_file, 'r', encoding='utf-8') as f:
        all_words = json.load(f)
    
    # Organize words by level and category
    words_by_level = {}
    for word in all_words:
        level = word['level']
        if level not in words_by_level:
            words_by_level[level] = []
        words_by_level[level].append(word)
    
    print(f"📚 Loaded {len(all_words)} words")
    for level, words in words_by_level.items():
        print(f"  {level}: {len(words)} words")
    
    # Get all locations
    locations = await db.locations.find().to_list(1000)
    print(f"\n📍 Found {len(locations)} locations")
    
    # Clear existing vocab sets
    await db.vocab_sets.delete_many({})
    print("🗑️  Cleared existing vocabulary sets")
    
    vocab_sets_created = 0
    
    # Create vocabulary sets for each location
    for location in locations:
        location_id = location['_id']
        location_name = location['name']
        chapter_id = location.get('chapter_id')
        level = location.get('level', 'A1')
        
        # Get words for this level
        level_words = words_by_level.get(level, words_by_level.get('A1', []))
        
        # Create a vocabulary set with 10-15 words
        num_words = min(12, len(level_words))
        if num_words == 0:
            print(f"  ⚠️  No words available for {location_name} ({level})")
            continue
        
        # Select words (try to get thematic words if possible)
        selected_words = level_words[:num_words]
        
        vocab_set = {
            "location_id": str(location_id),
            "chapter_id": str(chapter_id) if chapter_id else None,
            "title": f"{location_name} Vocabulary",
            "description": f"Essential vocabulary for {location_name.lower()}",
            "level": level,
            "words": [
                {
                    "word": w['word'],
                    "translation": w['translation'],
                    "example": w['example'],
                    "category": w.get('category', 'general'),
                    "audio_url": None
                }
                for w in selected_words
            ],
            "total_words": num_words,
            "completion_criteria": {
                "min_words_learned": max(8, num_words - 2),  # Learn 80% of words
                "min_reviews": 1
            },
            "xp_reward": 50,
            "estimated_minutes": 10,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.vocab_sets.insert_one(vocab_set)
        vocab_sets_created += 1
        print(f"  ✅ Created: {vocab_set['title']} ({num_words} words, {level})")
    
    # Also seed words into the main vocab collection for the standalone vocab coach
    print(f"\n📖 Seeding main vocabulary collection...")
    await db.vocab.delete_many({})
    
    for word in all_words:
        word_doc = {
            "word": word['word'],
            "translation": word['translation'],
            "example": word['example'],
            "level": word['level'],
            "category": word.get('category', 'general'),
            "audio_url": None,
            "created_at": datetime.utcnow()
        }
        await db.vocab.insert_one(word_doc)
    
    print(f"  ✅ Seeded {len(all_words)} words into vocab collection")
    
    # Create indexes
    await db.vocab_sets.create_index("location_id")
    await db.vocab_sets.create_index("chapter_id")
    await db.vocab_sets.create_index("level")
    await db.vocab.create_index("level")
    await db.vocab.create_index("word")
    
    print(f"\n✅ Successfully created {vocab_sets_created} vocabulary sets!")
    print(f"✅ Seeded {len(all_words)} words into main vocabulary")
    print("=" * 50)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_vocab_sets())
