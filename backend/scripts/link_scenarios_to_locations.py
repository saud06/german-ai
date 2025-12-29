"""
Link scenarios to their corresponding locations in the Learning Path
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

async def link_scenarios_to_locations():
    """Link scenarios to locations based on name matching"""
    
    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[os.getenv("MONGODB_DB_NAME", "german_ai")]
    
    print("🔗 Linking scenarios to locations...")
    print("")
    
    # Get all locations
    locations = await db.locations.find({}).to_list(length=1000)
    print(f"Found {len(locations)} locations")
    
    # Get all scenarios
    scenarios = await db.scenarios.find({}).to_list(length=1000)
    print(f"Found {len(scenarios)} scenarios")
    print("")
    
    linked_count = 0
    
    for location in locations:
        location_name = location.get("name", "")
        location_id = location["_id"]
        
        # Find matching scenario
        # Scenario name format: "Das Café Conversation"
        # Location name format: "Das Café"
        matching_scenarios = []
        
        for scenario in scenarios:
            scenario_name = scenario.get("name", "")
            # Check if scenario name starts with location name
            if scenario_name.startswith(location_name):
                matching_scenarios.append(scenario["_id"])
        
        if matching_scenarios:
            # Update location with scenario IDs
            await db.locations.update_one(
                {"_id": location_id},
                {
                    "$set": {
                        "scenarios": matching_scenarios,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            print(f"  ✓ {location_name}: Linked {len(matching_scenarios)} scenario(s)")
            linked_count += 1
        else:
            print(f"  ⚠️  {location_name}: No matching scenarios found")
    
    print("")
    print(f"✅ Linked {linked_count} locations to scenarios")
    print("")
    
    # Verify the linking
    print("🔍 Verifying Das Café...")
    cafe_location = await db.locations.find_one({"name": "Das Café"})
    if cafe_location and "scenarios" in cafe_location:
        print(f"  ✓ Das Café has {len(cafe_location['scenarios'])} scenario(s)")
        for scenario_id in cafe_location["scenarios"]:
            scenario = await db.scenarios.find_one({"_id": scenario_id})
            if scenario:
                print(f"    - {scenario['name']}")
    else:
        print("  ❌ Das Café not properly linked")
    
    print("")
    print("🎉 All scenarios linked to locations!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(link_scenarios_to_locations())
