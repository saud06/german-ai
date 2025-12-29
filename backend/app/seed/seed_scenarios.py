"""
Script to seed initial scenarios into the database
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.seed.scenarios_data import get_initial_scenarios
from app.seed.new_scenarios_data import get_new_scenarios


async def seed_scenarios():
    """Seed initial scenarios into database"""
    
    print("🌱 Seeding scenarios...")
    
    # Connect to database
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client.german_ai
    scenarios_collection = db.scenarios
    
    # Get all scenarios (initial + new)
    scenarios = get_initial_scenarios() + get_new_scenarios()
    
    # Check if scenarios already exist
    existing_count = await scenarios_collection.count_documents({})
    
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing scenarios")
        response = input("Do you want to delete existing scenarios and reseed? (yes/no): ")
        if response.lower() == 'yes':
            result = await scenarios_collection.delete_many({})
            print(f"🗑️  Deleted {result.deleted_count} scenarios")
        else:
            print("❌ Seeding cancelled")
            client.close()
            return
    
    # Insert scenarios
    for scenario in scenarios:
        scenario_dict = scenario.dict(by_alias=True, exclude={"id"})
        result = await scenarios_collection.insert_one(scenario_dict)
        print(f"✅ Created scenario: {scenario.name} (ID: {result.inserted_id})")
    
    print(f"\n🎉 Successfully seeded {len(scenarios)} scenarios!")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_scenarios())
