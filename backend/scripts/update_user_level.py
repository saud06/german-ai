"""
Update a user's journey level
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "german_ai")

async def update_level(email: str, new_level: str):
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    print("=" * 60)
    print(f"UPDATING USER LEVEL: {email} → {new_level}")
    print("=" * 60)
    
    # Find user
    user = await db.users.find_one({"email": email})
    if not user:
        print(f"❌ User not found: {email}")
        return
    
    print(f"✅ Found user: {user.get('name')} ({email})")
    
    # Update journey level
    journeys_data = user.get("learning_journeys", {})
    active_id = journeys_data.get("active_journey_id")
    
    if not active_id:
        print("❌ No active journey found")
        return
    
    # Find and update the active journey
    journeys = journeys_data.get("journeys", [])
    updated = False
    
    for journey in journeys:
        if journey.get("id") == active_id:
            old_level = journey.get("level")
            journey["level"] = new_level
            print(f"\n📝 Updating journey:")
            print(f"   Type: {journey.get('type')}")
            print(f"   Old Level: {old_level}")
            print(f"   New Level: {new_level}")
            updated = True
            break
    
    if not updated:
        print("❌ Active journey not found in journeys list")
        return
    
    # Save to database
    result = await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"learning_journeys.journeys": journeys}}
    )
    
    if result.modified_count > 0:
        print(f"\n✅ Successfully updated {email} to level {new_level}")
        print("\n🎯 Now refresh your vocabulary page to see B1 content!")
    else:
        print("\n❌ Update failed")
    
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python update_user_level.py <email> <level>")
        print("Example: python update_user_level.py saud@gmail.com B1")
        sys.exit(1)
    
    email = sys.argv[1]
    level = sys.argv[2]
    
    asyncio.run(update_level(email, level))
