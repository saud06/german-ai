"""
Check all users and their journeys
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "german_ai")

async def check():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    print("=" * 60)
    print("ALL USERS IN DATABASE")
    print("=" * 60)
    
    users = await db.users.find({}).to_list(100)
    
    if not users:
        print("\n❌ No users found in database!")
    else:
        print(f"\n✅ Found {len(users)} users:\n")
        
        for user in users:
            print(f"📧 Email: {user.get('email')}")
            print(f"   Name: {user.get('name')}")
            print(f"   ID: {user.get('_id')}")
            
            journeys_data = user.get("learning_journeys", {})
            active_id = journeys_data.get("active_journey_id")
            journeys = journeys_data.get("journeys", [])
            
            if journeys:
                print(f"   Active Journey ID: {active_id}")
                print(f"   Total Journeys: {len(journeys)}")
                
                for journey in journeys:
                    is_active = "✓ ACTIVE" if journey.get("id") == active_id else ""
                    print(f"      - {journey.get('type')} (Level: {journey.get('level')}) {is_active}")
            else:
                print(f"   ⚠️  No journeys configured")
            
            print()
    
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check())
