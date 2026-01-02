"""
Utility functions for journey-related operations
"""
from typing import Optional
from bson import ObjectId


async def get_user_journey_level(db, user_id: str) -> Optional[str]:
    """
    Get the level of the user's active journey
    Returns the level (e.g., 'A1', 'B1', 'Beginner', etc.) or None
    """
    try:
        print(f"[JOURNEY] Looking up user_id: {user_id}")
        user = await db["users"].find_one({"_id": ObjectId(user_id)})
        if not user:
            print(f"[JOURNEY] User not found with ID: {user_id}")
            return None
        
        print(f"[JOURNEY] Found user: {user.get('email')}")
        journeys_data = user.get("learning_journeys", {})
        active_id = journeys_data.get("active_journey_id")
        
        print(f"[JOURNEY] Active journey ID: {active_id}")
        print(f"[JOURNEY] Total journeys: {len(journeys_data.get('journeys', []))}")
        
        if not active_id:
            print(f"[JOURNEY] No active journey ID found")
            return None
        
        # Find active journey
        for journey in journeys_data.get("journeys", []):
            print(f"[JOURNEY] Checking journey: {journey.get('id')} (type: {journey.get('type')}, level: {journey.get('level')})")
            if journey.get("id") == active_id:
                level = journey.get("level")
                print(f"[JOURNEY] ✅ Found active journey level: {level}")
                return level
        
        print(f"[JOURNEY] Active journey not found in journeys list")
        return None
    except Exception as e:
        print(f"[JOURNEY] Error getting user journey level: {e}")
        import traceback
        traceback.print_exc()
        return None


async def get_user_journey_info(db, user_id: str) -> dict:
    """
    Get the user's active journey information
    Returns dict with level, type, and other journey info
    """
    try:
        user = await db["users"].find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"level": None, "type": None, "id": None}
        
        journeys_data = user.get("learning_journeys", {})
        active_id = journeys_data.get("active_journey_id")
        
        if not active_id:
            return {"level": None, "type": None, "id": None}
        
        # Find active journey
        for journey in journeys_data.get("journeys", []):
            if journey.get("id") == active_id:
                return {
                    "level": journey.get("level"),
                    "type": journey.get("type"),
                    "id": journey.get("id"),
                    "is_primary": journey.get("is_primary", False)
                }
        
        return {"level": None, "type": None, "id": None}
    except Exception as e:
        print(f"Error getting user journey info: {e}")
        return {"level": None, "type": None, "id": None}


def normalize_level_for_query(level: str, journey_type: Optional[str] = None) -> dict:
    """
    Convert a level to a MongoDB query filter
    Handles both CEFR levels (A1, A2, etc.) and difficulty levels (Beginner, Intermediate, Advanced)
    
    For CEFR levels: Returns exact match
    For difficulty levels: Returns range of CEFR levels
    """
    if not level:
        return {}
    
    level_lower = level.lower()
    
    # If it's already a CEFR level, return exact match
    if level_lower in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']:
        return {"level": level.upper()}
    
    # Map difficulty levels to CEFR ranges
    difficulty_map = {
        "beginner": ["A1", "A2"],
        "intermediate": ["B1", "B2"],
        "advanced": ["C1", "C2"]
    }
    
    if level_lower in difficulty_map:
        return {"level": {"$in": difficulty_map[level_lower]}}
    
    # Default: try exact match
    return {"level": level}


def get_level_range_for_content(level: str) -> list[str]:
    """
    Get appropriate content levels for a given user level
    Returns only the exact level selected by the user
    
    For example:
    - B1 user gets: b1 content only (lowercase to match DB)
    - A1 user gets: a1 content only
    - Beginner gets: a1, a2 content (difficulty range)
    """
    level_lower = level.lower()
    
    # CEFR levels - return exact level only (lowercase to match DB)
    if level_lower in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']:
        return [level_lower]
    
    # Difficulty levels (lowercase to match DB)
    difficulty_map = {
        'beginner': ['a1', 'a2'],
        'intermediate': ['b1', 'b2'],
        'advanced': ['c1', 'c2']
    }
    
    if level_lower in difficulty_map:
        return difficulty_map[level_lower]
    
    # Default: return lowercase
    return [level_lower]
