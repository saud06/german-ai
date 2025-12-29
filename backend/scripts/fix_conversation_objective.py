"""
Fix 'Have conversation' objective to be optional and auto-complete
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

async def fix_conversation_objectives():
    """Update all scenarios to make 'Have conversation' objective optional"""
    
    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[os.getenv("MONGODB_DB_NAME", "german_ai")]
    
    print("🔧 Fixing 'Have conversation' objectives...")
    print("")
    
    # Get all scenarios
    scenarios = await db.scenarios.find({}).to_list(length=1000)
    
    updated_count = 0
    for scenario in scenarios:
        modified = False
        
        if "objectives" in scenario:
            for obj in scenario["objectives"]:
                # Find "Have conversation" objectives
                if obj.get("description", "").lower() in ["have conversation", "respond naturally", "converse"]:
                    # Make it optional
                    if obj.get("required", True):
                        obj["required"] = False
                        modified = True
                        print(f"  ✓ {scenario['name']}: Made 'Have conversation' optional")
                    
                    # Update hint to be clearer
                    old_hint = obj.get("hint", "")
                    if old_hint != "Chat naturally - completes after 2 messages":
                        obj["hint"] = "Chat naturally - completes after 2 messages"
                        modified = True
                        print(f"  ✓ {scenario['name']}: Updated hint")
        
        if modified:
            await db.scenarios.update_one(
                {"_id": scenario["_id"]},
                {"$set": {"objectives": scenario["objectives"], "updated_at": datetime.utcnow()}}
            )
            updated_count += 1
    
    print("")
    print(f"✅ Updated {updated_count} scenarios")
    print("")
    
    # Also update active conversation states
    print("🔧 Fixing active conversation states...")
    states = await db.conversation_states.find({"status": "active"}).to_list(length=1000)
    
    state_count = 0
    for state in states:
        modified = False
        
        if "objectives_progress" in state:
            for obj_progress in state["objectives_progress"]:
                # Find the scenario to check objective description
                scenario = await db.scenarios.find_one({"_id": state["scenario_id"]})
                if scenario and "objectives" in scenario:
                    for obj in scenario["objectives"]:
                        if obj["id"] == obj_progress["objective_id"]:
                            if obj.get("description", "").lower() in ["have conversation", "respond naturally", "converse"]:
                                # Check if user has sent 2+ messages
                                user_messages = [msg for msg in state.get("messages", []) if msg.get("role") == "user"]
                                if len(user_messages) >= 2 and not obj_progress.get("completed", False):
                                    obj_progress["completed"] = True
                                    obj_progress["completed_at"] = datetime.utcnow()
                                    modified = True
                                    print(f"  ✓ Auto-completed conversation objective for user {state['user_id']}")
        
        if modified:
            await db.conversation_states.update_one(
                {"_id": state["_id"]},
                {"$set": {"objectives_progress": state["objectives_progress"]}}
            )
            state_count += 1
    
    print("")
    print(f"✅ Updated {state_count} active conversation states")
    print("")
    print("🎉 All fixes applied!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_conversation_objectives())
