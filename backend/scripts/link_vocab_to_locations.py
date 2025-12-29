"""
Link vocabulary sets to locations and update progress tracking
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
from bson import ObjectId

# Load environment variables
load_dotenv()

async def link_vocab_to_locations():
    """Link vocabulary sets to locations bidirectionally"""
    
    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[os.getenv("MONGODB_DB_NAME", "german_ai")]
    
    print("🔗 Linking vocabulary sets to locations...")
    print("")
    
    # Get all vocabulary sets
    vocab_sets = await db.vocab_sets.find({}).to_list(length=1000)
    
    print(f"Found {len(vocab_sets)} vocabulary sets")
    print("")
    
    linked_count = 0
    
    for vocab_set in vocab_sets:
        location_id = vocab_set.get("location_id")
        vocab_set_id = vocab_set["_id"]
        
        if location_id:
            # Convert to ObjectId if string
            if isinstance(location_id, str):
                location_id = ObjectId(location_id)
            
            # Update location to reference this vocab set
            result = await db.locations.update_one(
                {"_id": location_id},
                {
                    "$set": {
                        "vocab_set_id": vocab_set_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                location = await db.locations.find_one({"_id": location_id})
                print(f"  ✓ {location.get('name', 'Unknown')}: Linked to vocab set")
                linked_count += 1
    
    print("")
    print(f"✅ Linked {linked_count} vocabulary sets to locations")
    print("")
    print("🎉 Vocabulary sets now integrated with Learning Path!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(link_vocab_to_locations())
