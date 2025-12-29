"""
Seed script for vocabulary expansion
Populates the database with 500+ German words
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.seed.vocabulary_expansion import get_expanded_vocabulary, get_vocabulary_stats


async def seed_vocabulary():
    """Seed vocabulary into database"""
    
    print("🌱 Seeding vocabulary...")
    
    # Connect to database
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client.german_ai
    vocab_collection = db.seed_words
    
    # Get vocabulary
    vocabulary = get_expanded_vocabulary()
    
    # Check if vocabulary already exists
    existing_count = await vocab_collection.count_documents({})
    
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing words")
        response = input("Do you want to delete existing words and reseed? (yes/no): ")
        if response.lower() == 'yes':
            result = await vocab_collection.delete_many({})
            print(f"🗑️  Deleted {result.deleted_count} words")
        else:
            print("❌ Seeding cancelled")
            client.close()
            return
    
    # Insert vocabulary
    print(f"\n📚 Inserting {len(vocabulary)} words...")
    
    inserted_count = 0
    for word_data in vocabulary:
        try:
            result = await vocab_collection.insert_one(word_data)
            inserted_count += 1
            if inserted_count % 50 == 0:
                print(f"  ✅ Inserted {inserted_count} words...")
        except Exception as e:
            print(f"  ⚠️  Error inserting word '{word_data.get('word')}': {e}")
    
    print(f"\n✅ Successfully inserted {inserted_count} words!")
    
    # Show statistics
    stats = get_vocabulary_stats()
    print(f"\n📊 Vocabulary Statistics:")
    print(f"  Total words: {stats['total_words']}")
    print(f"\n  By Level:")
    for level, count in sorted(stats['by_level'].items()):
        print(f"    {level}: {count} words")
    print(f"\n  By Category:")
    for category, count in sorted(stats['by_category'].items()):
        print(f"    {category}: {count} words")
    print(f"\n  By Part of Speech:")
    for pos, count in sorted(stats['by_part_of_speech'].items()):
        print(f"    {pos}: {count} words")
    
    # Create indexes for better performance
    print(f"\n🔍 Creating indexes...")
    await vocab_collection.create_index("word")
    await vocab_collection.create_index("level")
    await vocab_collection.create_index("category")
    await vocab_collection.create_index([("level", 1), ("category", 1)])
    print("✅ Indexes created")
    
    client.close()
    print("\n🎉 Vocabulary seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_vocabulary())
