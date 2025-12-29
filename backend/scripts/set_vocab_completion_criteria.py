"""
Set completion criteria for all vocabulary sets
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def set_vocab_completion_criteria():
    """Set reasonable completion criteria for vocabulary sets"""
    
    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[os.getenv("MONGODB_DB_NAME", "german_ai")]
    
    print("📝 Setting vocabulary completion criteria...")
    print("")
    
    # Get all vocabulary sets
    vocab_sets = await db.vocab_sets.find({}).to_list(length=1000)
    
    updated_count = 0
    
    for vocab_set in vocab_sets:
        word_count = len(vocab_set.get("words", []))
        
        # Set criteria: learn at least 70% of words and complete 1 review
        min_words = max(5, int(word_count * 0.7))  # At least 5 words or 70%
        
        criteria = {
            "min_words_learned": min_words,
            "min_reviews": 1
        }
        
        # Update the vocab set
        await db.vocab_sets.update_one(
            {"_id": vocab_set["_id"]},
            {
                "$set": {
                    "completion_criteria": criteria,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        print(f"  ✓ {vocab_set.get('title', 'Unknown')}: Learn {min_words}/{word_count} words + 1 review")
        updated_count += 1
    
    print("")
    print(f"✅ Updated {updated_count} vocabulary sets")
    print("")
    print("📊 Completion criteria:")
    print("   - Learn 70% of words (minimum 5)")
    print("   - Complete 1 review session")
    print("")
    print("🎉 Vocabulary sets ready for Learning Path integration!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(set_vocab_completion_criteria())
