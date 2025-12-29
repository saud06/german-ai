"""
Update all scenario character voice_ids to use config default instead of hardcoded value
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db
from dotenv import load_dotenv

load_dotenv()

async def update_voice_ids():
    """Remove hardcoded voice_ids from all scenarios"""
    db = await get_db()
    scenarios_collection = db.scenarios
    
    # Get all scenarios
    scenarios = await scenarios_collection.find({}).to_list(length=None)
    
    print(f"Found {len(scenarios)} scenarios")
    
    updated_count = 0
    for scenario in scenarios:
        # Check if scenario has characters
        if 'characters' in scenario and scenario['characters']:
            needs_update = False
            
            # Update each character to remove voice_id (will use config default)
            for character in scenario['characters']:
                if 'voice_id' in character:
                    # Remove the hardcoded voice_id
                    del character['voice_id']
                    needs_update = True
            
            if needs_update:
                # Update the scenario
                await scenarios_collection.update_one(
                    {'_id': scenario['_id']},
                    {'$set': {'characters': scenario['characters']}}
                )
                updated_count += 1
                print(f"✅ Updated scenario: {scenario.get('title', 'Unknown')}")
    
    print(f"\n✅ Updated {updated_count} scenarios")
    print(f"All characters will now use PIPER_VOICE from config (de_DE-eva_k-x_low)")

if __name__ == "__main__":
    asyncio.run(update_voice_ids())
