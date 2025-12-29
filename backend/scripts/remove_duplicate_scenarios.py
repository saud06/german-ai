"""
Remove duplicate scenarios from locations - keep only one scenario per location
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

async def remove_duplicate_scenarios():
    """Remove duplicate scenarios, keeping only the first one for each location"""
    
    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[os.getenv("MONGODB_DB_NAME", "german_ai")]
    
    print("🧹 Removing duplicate scenarios from locations...")
    print("")
    
    # Get all locations
    locations = await db.locations.find({}).to_list(length=1000)
    
    updated_count = 0
    deleted_scenarios = 0
    
    for location in locations:
        location_name = location.get("name", "")
        scenarios = location.get("scenarios", [])
        
        if len(scenarios) > 1:
            # Keep only the first scenario
            keep_scenario = scenarios[0]
            delete_scenarios = scenarios[1:]
            
            print(f"{location_name}: {len(scenarios)} scenarios → keeping 1, deleting {len(delete_scenarios)}")
            
            # Update location to have only one scenario
            await db.locations.update_one(
                {"_id": location["_id"]},
                {
                    "$set": {
                        "scenarios": [keep_scenario],
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Delete the duplicate scenarios
            for scenario_id in delete_scenarios:
                result = await db.scenarios.delete_one({"_id": scenario_id})
                if result.deleted_count > 0:
                    deleted_scenarios += 1
            
            updated_count += 1
    
    print("")
    print(f"✅ Updated {updated_count} locations")
    print(f"🗑️  Deleted {deleted_scenarios} duplicate scenarios")
    print("")
    print("🎉 All locations now have exactly 1 scenario!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(remove_duplicate_scenarios())
