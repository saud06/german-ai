"""
Recalculate user progress for all completed scenarios
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

async def recalculate_all_progress():
    """Recalculate progress for all users based on completed scenarios"""
    
    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[os.getenv("MONGODB_DB_NAME", "german_ai")]
    
    print("🔄 Recalculating user progress...")
    print("")
    
    # Get all completed conversation states
    completed_states = await db.conversation_states.find({"status": "completed"}).to_list(length=10000)
    
    print(f"Found {len(completed_states)} completed scenarios")
    print("")
    
    # Group by user
    user_scenarios = {}
    for state in completed_states:
        user_id = state["user_id"]
        if user_id not in user_scenarios:
            user_scenarios[user_id] = []
        user_scenarios[user_id].append(state)
    
    print(f"Processing {len(user_scenarios)} users...")
    print("")
    
    for user_id, states in user_scenarios.items():
        print(f"User: {user_id}")
        
        # Reset user progress
        await db.user_progress.delete_many({"user_id": user_id})
        
        # Process each completed scenario
        for state in states:
            scenario_id = state["scenario_id"]
            
            # Convert to ObjectId if it's a string
            if isinstance(scenario_id, str):
                scenario_id = ObjectId(scenario_id)
            
            # Get scenario
            scenario = await db.scenarios.find_one({"_id": scenario_id})
            if not scenario:
                print(f"  ⚠️  Scenario not found: {scenario_id}")
                continue
            
            # Find location
            location = await db.locations.find_one({"scenarios": scenario_id})
            if not location:
                print(f"  ⚠️  No location for: {scenario.get('name', 'Unknown')}")
                continue
            
            chapter_id = str(location["chapter_id"])
            location_id = str(location["_id"])
            scenario_id_str = str(scenario_id)
            
            # Get or create user progress
            progress_doc = await db.user_progress.find_one({"user_id": user_id})
            if not progress_doc:
                progress_doc = {
                    "user_id": user_id,
                    "current_chapter": chapter_id,
                    "total_xp": 0,
                    "level": 1,
                    "chapter_progress": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                await db.user_progress.insert_one(progress_doc)
                progress_doc = await db.user_progress.find_one({"user_id": user_id})
            
            # Initialize chapter progress
            if "chapter_progress" not in progress_doc:
                progress_doc["chapter_progress"] = {}
            
            if chapter_id not in progress_doc["chapter_progress"]:
                progress_doc["chapter_progress"][chapter_id] = {
                    "scenarios_completed": [],
                    "locations_completed": [],
                    "progress_percent": 0,
                    "xp_earned": 0
                }
            
            chapter_progress = progress_doc["chapter_progress"][chapter_id]
            
            # Add scenario if not already there
            if scenario_id_str not in chapter_progress["scenarios_completed"]:
                chapter_progress["scenarios_completed"].append(scenario_id_str)
                
                # Award XP
                xp_reward = scenario.get("xp_reward", 100)
                progress_doc["total_xp"] = progress_doc.get("total_xp", 0) + xp_reward
                chapter_progress["xp_earned"] = chapter_progress.get("xp_earned", 0) + xp_reward
                
                # Update level
                total_xp = progress_doc["total_xp"]
                new_level = 1
                while total_xp >= (new_level * 100):
                    new_level += 1
                progress_doc["level"] = new_level
                
                print(f"  ✓ {scenario.get('name', 'Unknown')} (+{xp_reward} XP)")
            
            # Check if location is complete (both scenarios AND vocabulary)
            location_scenarios = [str(sid) for sid in location.get("scenarios", [])]
            completed_scenarios = chapter_progress["scenarios_completed"]
            scenarios_done = all(str(sid) in completed_scenarios for sid in location_scenarios)
            
            # Check vocabulary completion
            location_vocab_set = str(location.get("vocab_set_id", ""))
            vocab_done = location_vocab_set in chapter_progress.get("vocab_sets_completed", []) if location_vocab_set else True
            
            location_complete = scenarios_done and vocab_done
            
            if location_complete and location_id not in chapter_progress.get("locations_completed", []):
                chapter_progress["locations_completed"].append(location_id)
                
                # Award location XP
                location_xp = location.get("rewards", {}).get("xp", 100)
                progress_doc["total_xp"] = progress_doc.get("total_xp", 0) + location_xp
                chapter_progress["xp_earned"] = chapter_progress.get("xp_earned", 0) + location_xp
                
                print(f"  🎉 Location complete: {location.get('name', 'Unknown')} (+{location_xp} XP)")
            
            # Calculate progress percentage
            chapter = await db.learning_paths.find_one({"_id": ObjectId(chapter_id)})
            if chapter:
                total_locations = len(chapter.get("locations", []))
                completed_locations = len(chapter_progress["locations_completed"])
                chapter_progress["progress_percent"] = int((completed_locations / total_locations * 100)) if total_locations > 0 else 0
            
            # Update database
            progress_doc["updated_at"] = datetime.utcnow()
            await db.user_progress.update_one(
                {"user_id": user_id},
                {"$set": progress_doc},
                upsert=True
            )
        
        # Final summary for user
        final_progress = await db.user_progress.find_one({"user_id": user_id})
        if final_progress:
            total_xp = final_progress.get("total_xp", 0)
            level = final_progress.get("level", 1)
            print(f"  📊 Final: Level {level}, {total_xp} XP")
        
        print("")
    
    print("✅ All user progress recalculated!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(recalculate_all_progress())
