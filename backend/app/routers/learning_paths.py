"""
Learning Paths API - Story-driven interactive learning system
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from ..db import get_db
from ..models.learning_path import (
    LearningPath, Location, Character, UserProgress,
    LearningPathResponse, LocationResponse, CharacterResponse,
    ProgressSummary, RecommendedAction, DailyChallenge,
    ChapterProgress, CharacterRelationship, LearningProfile
)
from ..routers.auth import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/learning-paths", tags=["learning-paths"])


# ============================================================================
# LEARNING PATHS
# ============================================================================

@router.get("/", response_model=List[LearningPathResponse])
async def get_all_learning_paths(
    user_id: str = Depends(get_current_user),
    journey_level: Optional[str] = None,
    db = Depends(get_db)
):
    """Get all learning paths with user progress, optionally filtered by journey level"""
    
    # Get user progress
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    if not progress_doc:
        # Create initial progress
        progress_doc = {
            "user_id": user_id,
            "current_chapter": 1,
            "chapter_progress": {},
            "character_relationships": {},
            "life_stats": {
                "housing": "hotel",
                "job": "unemployed",
                "friends": 0,
                "cities_visited": 1,
                "certifications": []
            },
            "learning_profile": {},
            "total_xp": 0,
            "level": 1,
            "achievements": [],
            "daily_streak": 0,
            "last_activity": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.user_progress.insert_one(progress_doc)
    
    # Get all learning paths, optionally filtered by level
    query = {}
    if journey_level:
        # Filter to show only paths matching the journey level
        query["level"] = journey_level.upper()
    paths = await db.learning_paths.find(query).sort("chapter", 1).to_list(length=100)
    
    result = []
    for path in paths:
        chapter_id = str(path["_id"])
        chapter_progress = progress_doc.get("chapter_progress", {}).get(chapter_id)
        
        # Convert ObjectIds to strings
        if "locations" in path:
            path["locations"] = [str(loc_id) for loc_id in path["locations"]]
        if "characters" in path:
            path["characters"] = [str(char_id) for char_id in path["characters"]]
        
        # Check if unlocked - first chapter is always unlocked
        is_unlocked = True
        if path.get("chapter", 1) == 1:
            is_unlocked = True
        elif path.get("unlock_requirements"):
            req = path["unlock_requirements"]
            if req.get("min_xp", 0) > progress_doc.get("total_xp", 0):
                is_unlocked = False
        
        # Check if completed
        is_completed = False
        if chapter_progress and chapter_progress.get("progress_percent") == 100:
            is_completed = True
        
        result.append({
            "path": path,
            "progress": chapter_progress,
            "is_unlocked": is_unlocked,
            "is_completed": is_completed
        })
    
    return result


# ============================================================================
# PROGRESS & RECOMMENDATIONS (Must come before /{path_id} to avoid route conflicts)
# ============================================================================

@router.get("/progress/summary", response_model=ProgressSummary)
async def get_progress_summary(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's overall progress summary"""
    
    # Get user progress
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    if not progress_doc:
        raise HTTPException(status_code=404, detail="Progress not found")
    
    # Calculate stats
    chapters_completed = sum(
        1 for p in progress_doc.get("chapter_progress", {}).values()
        if p.get("progress_percent") == 100
    )
    
    # Get total scenarios completed
    scenarios_completed = sum(
        len(p.get("scenarios_completed", []))
        for p in progress_doc.get("chapter_progress", {}).values()
    )
    
    # Words learned (from vocab system)
    words_learned = await db.user_vocab.count_documents({"user_id": user_id})
    
    # Conversations held (from conversation_states)
    conversations_held = await db.conversation_states.count_documents({
        "user_id": user_id,
        "status": "completed"
    })
    
    # Next milestone
    current_xp = progress_doc.get("total_xp", 0)
    next_milestone = None
    milestones = [100, 500, 1000, 2500, 5000, 10000]
    for m in milestones:
        if current_xp < m:
            next_milestone = f"Reach {m} XP ({int((current_xp / m) * 100)}% complete)"
            break
    
    # Ensure current_chapter is an integer (handle ObjectId or string)
    current_chapter_raw = progress_doc.get("current_chapter", 1)
    if isinstance(current_chapter_raw, (ObjectId, str)):
        # If it's an ObjectId or string, default to 1
        current_chapter_int = 1
    else:
        current_chapter_int = int(current_chapter_raw)
    
    return {
        "current_chapter": current_chapter_int,
        "current_location": progress_doc.get("current_location"),
        "total_xp": current_xp,
        "level": progress_doc.get("level", 1),
        "chapters_completed": chapters_completed,
        "scenarios_completed": scenarios_completed,
        "words_learned": words_learned,
        "conversations_held": conversations_held,
        "daily_streak": progress_doc.get("daily_streak", 0),
        "life_stats": progress_doc.get("life_stats", {}),
        "next_milestone": next_milestone
    }


@router.get("/recommendations", response_model=List[RecommendedAction])
async def get_recommendations(
    user_id: str = Depends(get_current_user),
    journey_level: Optional[str] = None,
    db = Depends(get_db)
):
    """Get AI-powered recommendations for next actions, optionally filtered by journey level"""
    
    # Get user progress
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    if not progress_doc:
        return []
    
    recommendations = []
    
    # 1. Continue current chapter
    current_chapter = progress_doc.get("current_chapter", 1)
    chapter_progress = progress_doc.get("chapter_progress", {})
    
    # Find incomplete locations in current chapter
    path_query = {"chapter": current_chapter}
    if journey_level:
        path_query["level"] = journey_level.upper()
    path = await db.learning_paths.find_one(path_query)
    if path:
        for location_id in path.get("locations", []):
            location = await db.locations.find_one({"_id": ObjectId(location_id)})
            if location:
                recommendations.append({
                    "type": "location",
                    "id": str(location["_id"]),
                    "title": f"Visit {location['name']}",
                    "description": location["description"],
                    "estimated_minutes": location.get("estimated_minutes", 15),
                    "xp_reward": 50,
                    "priority": "high",
                    "reason": "Continue your journey in Chapter " + str(current_chapter)
                })
    
    # 2. Practice with characters
    relationships = progress_doc.get("character_relationships", {})
    for char_id, rel in relationships.items():
        if rel.get("level", 0) < 5:
            character = await db.characters.find_one({"_id": ObjectId(char_id)})
            if character:
                recommendations.append({
                    "type": "character",
                    "id": char_id,
                    "title": f"Chat with {character['name']}",
                    "description": f"Improve your relationship (Level {rel.get('level', 0)}/10)",
                    "estimated_minutes": 10,
                    "xp_reward": 30,
                    "priority": "medium",
                    "reason": "Build stronger relationships!"
                })
    
    # 3. Review vocabulary
    due_cards = await db.review_cards.count_documents({
        "user_id": user_id,
        "next_review": {"$lte": datetime.utcnow()}
    })
    if due_cards > 0:
        recommendations.append({
            "type": "review",
            "id": "reviews",
            "title": f"Review {due_cards} cards",
            "description": "Keep your vocabulary fresh with spaced repetition",
            "estimated_minutes": due_cards * 0.5,
            "xp_reward": 20,
            "priority": "medium",
            "reason": "Spaced repetition helps retention!"
        })
    
    return recommendations[:5]  # Top 5 recommendations


@router.get("/challenges/daily", response_model=List[DailyChallenge])
async def get_daily_challenges(
    user_id: str = Depends(get_current_user),
    journey_level: Optional[str] = None,
    db = Depends(get_db)
):
    """Get today's challenges, optionally filtered by journey level"""
    
    # Get or create today's challenges
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    challenges_doc = await db.daily_challenges.find_one({
        "user_id": user_id,
        "date": today
    })
    
    if not challenges_doc:
        # Create new challenges for today
        challenges_doc = {
            "user_id": user_id,
            "date": today,
            "challenges": [
                {
                    "id": "scenarios",
                    "title": "Complete 2 Scenarios",
                    "description": "Practice real-life conversations",
                    "type": "conversation",
                    "target": 2,
                    "progress": 0,
                    "xp_reward": 100,
                    "expires_at": tomorrow
                },
                {
                    "id": "vocab",
                    "title": "Learn 10 New Words",
                    "description": "Expand your vocabulary",
                    "type": "vocabulary",
                    "target": 10,
                    "progress": 0,
                    "xp_reward": 50,
                    "expires_at": tomorrow
                },
                {
                    "id": "streak",
                    "title": "Maintain Your Streak",
                    "description": "Log in every day",
                    "type": "daily",
                    "target": 1,
                    "progress": 1,  # Already logged in today
                    "xp_reward": 25,
                    "expires_at": tomorrow
                }
            ],
            "created_at": datetime.utcnow()
        }
        await db.daily_challenges.insert_one(challenges_doc)
    
    return challenges_doc["challenges"]


@router.get("/{path_id}", response_model=LearningPathResponse)
async def get_learning_path(
    path_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get specific learning path details"""
    
    # Get path
    path = await db.learning_paths.find_one({"_id": ObjectId(path_id)})
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    # Convert ObjectIds to strings
    if "locations" in path:
        path["locations"] = [str(loc_id) for loc_id in path["locations"]]
    if "characters" in path:
        path["characters"] = [str(char_id) for char_id in path["characters"]]
    
    # Get user progress
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    chapter_progress = progress_doc.get("chapter_progress", {}).get(path_id) if progress_doc else None
    
    # Check if unlocked
    is_unlocked = True
    if path.get("unlock_requirements") and progress_doc:
        req = path["unlock_requirements"]
        if req.get("min_xp", 0) > progress_doc.get("total_xp", 0):
            is_unlocked = False
    
    # Check if completed
    is_completed = False
    if chapter_progress and chapter_progress.get("progress_percent") == 100:
        is_completed = True
    
    return {
        "path": path,
        "progress": chapter_progress,
        "is_unlocked": is_unlocked,
        "is_completed": is_completed
    }


# ============================================================================
# LOCATIONS
# ============================================================================

@router.get("/{path_id}/locations", response_model=List[LocationResponse])
async def get_path_locations(
    path_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all locations in a learning path"""
    
    # Get path
    path = await db.learning_paths.find_one({"_id": ObjectId(path_id)})
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    # Get user progress
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    chapter_progress = progress_doc.get("chapter_progress", {}).get(path_id) if progress_doc else None
    completed_locations = chapter_progress.get("locations_completed", []) if chapter_progress else []
    
    # Get locations
    locations = await db.locations.find({"chapter_id": path_id}).to_list(length=100)
    
    result = []
    for idx, location in enumerate(locations):
        location_id = str(location["_id"])
        
        # Convert ObjectId scenario references to strings
        if "scenarios" in location:
            location["scenarios"] = [str(sid) for sid in location["scenarios"]]
        
        # Check if unlocked - first location is always unlocked, others require previous completion
        is_unlocked = False
        if idx == 0:
            # First location is always unlocked
            is_unlocked = True
        elif idx > 0 and result:
            # Unlock if previous location is completed
            prev_location_id = str(locations[idx - 1]["_id"])
            is_unlocked = prev_location_id in completed_locations
        
        # Check if completed
        is_completed = location_id in completed_locations
        
        # Calculate completion percent
        total_scenarios = len(location.get("scenarios", []))
        completed_scenarios = 0
        if chapter_progress:
            for scenario_id in location.get("scenarios", []):
                if scenario_id in chapter_progress.get("scenarios_completed", []):
                    completed_scenarios += 1
        
        completion_percent = int((completed_scenarios / total_scenarios * 100)) if total_scenarios > 0 else 0
        
        result.append({
            "location": location,
            "is_unlocked": is_unlocked,
            "is_completed": is_completed,
            "completion_percent": completion_percent
        })
    
    return result


@router.get("/locations/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get specific location details"""
    
    # Get location
    location = await db.locations.find_one({"_id": ObjectId(location_id)})
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Convert ObjectId scenario references to strings
    if "scenarios" in location:
        location["scenarios"] = [str(sid) for sid in location["scenarios"]]
    
    # Get user progress
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    chapter_id = location["chapter_id"]
    chapter_progress = progress_doc.get("chapter_progress", {}).get(chapter_id) if progress_doc else None
    
    # Check if unlocked
    is_unlocked = True
    if location.get("unlock_requirements") and chapter_progress:
        req = location["unlock_requirements"]
        current_progress = chapter_progress.get("progress_percent", 0)
        if req.get("chapter_progress", 0) > current_progress:
            is_unlocked = False
    
    # Check if completed
    is_completed = str(location["_id"]) in chapter_progress.get("locations_completed", []) if chapter_progress else False
    
    # Calculate completion percent based on ALL activities
    total_activities = 0
    completed_activities = 0
    
    # Count scenarios
    scenario_ids = location.get("scenarios", [])
    total_activities += len(scenario_ids)
    if chapter_progress:
        for scenario_id in scenario_ids:
            if str(scenario_id) in chapter_progress.get("scenarios_completed", []):
                completed_activities += 1
    
    # Count vocabulary sets
    vocab_set_id = location.get("vocab_set_id")
    if vocab_set_id:
        total_activities += 1
        if chapter_progress and str(vocab_set_id) in chapter_progress.get("vocab_sets_completed", []):
            completed_activities += 1
    
    # Count quizzes linked to this location
    quiz_count = await db.quizzes.count_documents({"location_id": location_id})
    total_activities += quiz_count
    if chapter_progress and quiz_count > 0:
        quizzes = await db.quizzes.find({"location_id": location_id}).to_list(100)
        for quiz in quizzes:
            if str(quiz["_id"]) in chapter_progress.get("quizzes_completed", []):
                completed_activities += 1
    
    # Count grammar exercises linked to this chapter
    if chapter_id:
        grammar_count = await db.grammar_exercises.count_documents({"chapter_id": chapter_id})
        total_activities += grammar_count
        if chapter_progress and grammar_count > 0:
            exercises = await db.grammar_exercises.find({"chapter_id": chapter_id}).to_list(100)
            for exercise in exercises:
                if str(exercise["_id"]) in chapter_progress.get("grammar_completed", []):
                    completed_activities += 1
    
    completion_percent = int((completed_activities / total_activities * 100)) if total_activities > 0 else 0
    
    return {
        "location": location,
        "is_unlocked": is_unlocked,
        "is_completed": is_completed,
        "completion_percent": completion_percent,
        "completed_activities": completed_activities,
        "total_activities": total_activities
    }


@router.get("/locations/{location_id}/activities")
async def get_location_activities(
    location_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get ALL activities for a location (scenarios, vocab, quizzes, etc.)"""
    
    activities = []
    
    # Get location to find scenario IDs
    location = await db.locations.find_one({"_id": ObjectId(location_id)})
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get user progress
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    chapter_id = location.get("chapter_id")
    chapter_progress = progress_doc.get("chapter_progress", {}).get(chapter_id, {}) if progress_doc else {}
    
    # Get completion status from different tracking fields
    completed_scenarios = set(chapter_progress.get("scenarios_completed", []))
    completed_vocab_sets = set(chapter_progress.get("vocab_sets_completed", []))
    completed_quizzes = set(chapter_progress.get("quizzes_completed", []))
    completed_grammar = set(chapter_progress.get("grammar_completed", []))
    
    # Get scenarios
    scenario_ids = location.get("scenarios", [])
    if scenario_ids:
        # Convert string IDs to ObjectId
        scenario_object_ids = [ObjectId(sid) if isinstance(sid, str) else sid for sid in scenario_ids]
        scenarios = await db.scenarios.find({"_id": {"$in": scenario_object_ids}}).to_list(100)
        for scenario in scenarios:
            scenario_id_str = str(scenario["_id"])
            activities.append({
                "id": scenario_id_str,
                "type": "scenario",
                "name": scenario["name"],
                "description": scenario["description"],
                "xp_reward": scenario.get("xp_reward", 100),
                "estimated_minutes": scenario.get("estimated_duration", 5),
                "icon": scenario.get("icon", "🎭"),
                "difficulty": scenario.get("difficulty", "beginner"),
                "completed": scenario_id_str in completed_scenarios
            })
    
    # Get vocabulary sets
    vocab_sets = await db.vocab_sets.find({"location_id": location_id}).to_list(100)
    for vocab_set in vocab_sets:
        vocab_id_str = str(vocab_set["_id"])
        activities.append({
            "id": vocab_id_str,
            "type": "vocabulary",
            "name": vocab_set["title"],
            "description": vocab_set["description"],
            "xp_reward": vocab_set.get("xp_reward", 50),
            "estimated_minutes": vocab_set.get("estimated_minutes", 10),
            "icon": "📚",
            "difficulty": vocab_set.get("level", "A1"),
            "completed": vocab_id_str in completed_vocab_sets
        })
    
    # Get quizzes
    quizzes = await db.quizzes.find({"location_id": location_id}).to_list(100)
    for quiz in quizzes:
        quiz_id_str = str(quiz["_id"])
        activities.append({
            "id": quiz_id_str,
            "type": "quiz",
            "name": quiz["title"],
            "description": quiz["description"],
            "xp_reward": quiz.get("xp_reward", 30),
            "estimated_minutes": quiz.get("estimated_minutes", 5),
            "icon": "📝",
            "difficulty": quiz.get("level", "A1"),
            "completed": quiz_id_str in completed_quizzes
        })
    
    # Get grammar exercises (by chapter_id from location)
    if chapter_id:
        grammar_exercises = await db.grammar_exercises.find({"chapter_id": chapter_id}).to_list(100)
        for exercise in grammar_exercises:
            exercise_id_str = str(exercise["_id"])
            activities.append({
                "id": exercise_id_str,
                "type": "grammar",
                "name": exercise["title"],
                "description": exercise["description"],
                "xp_reward": exercise.get("xp_reward", 40),
                "estimated_minutes": exercise.get("estimated_minutes", 8),
                "icon": "🎓",
                "difficulty": exercise.get("level", "A1"),
                "completed": exercise_id_str in completed_grammar
            })
    
    return {
        "location_id": location_id,
        "activities": activities,
        "total_activities": len(activities),
        "total_xp": sum(a["xp_reward"] for a in activities),
        "total_minutes": sum(a["estimated_minutes"] for a in activities)
    }


# ============================================================================
# CHARACTERS
# ============================================================================

@router.get("/characters", response_model=List[CharacterResponse])
async def get_all_characters(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all characters user has met"""
    
    # Get user progress
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    relationships = progress_doc.get("character_relationships", {}) if progress_doc else {}
    
    # Get characters user has met
    met_character_ids = list(relationships.keys())
    if not met_character_ids:
        return []
    
    characters = await db.characters.find({
        "_id": {"$in": [ObjectId(cid) for cid in met_character_ids]}
    }).to_list(length=100)
    
    result = []
    for character in characters:
        char_id = str(character["_id"])
        relationship = relationships.get(char_id)
        
        # Get available topics based on relationship level
        level = relationship.get("level", 0) if relationship else 0
        available_topics = []
        for req_level, topics in character.get("conversation_topics", {}).items():
            if int(req_level) <= level:
                available_topics.extend(topics)
        
        result.append({
            "character": character,
            "relationship": relationship,
            "available_topics": available_topics
        })
    
    return result


@router.get("/characters/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get specific character details"""
    
    # Get character
    character = await db.characters.find_one({"_id": ObjectId(character_id)})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get user progress
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    relationship = progress_doc.get("character_relationships", {}).get(character_id) if progress_doc else None
    
    # Get available topics
    level = relationship.get("level", 0) if relationship else 0
    available_topics = []
    for req_level, topics in character.get("conversation_topics", {}).items():
        if int(req_level) <= level:
            available_topics.extend(topics)
    
    return {
        "character": character,
        "relationship": relationship,
        "available_topics": available_topics
    }


# ============================================================================
# PROGRESS UPDATES
# ============================================================================

@router.post("/progress/scenario-complete")
async def complete_scenario(
    scenario_id: str,
    xp_earned: int,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Mark a scenario as complete and update progress"""
    
    # Get scenario to find chapter and location
    scenario = await db.scenarios.find_one({"_id": ObjectId(scenario_id)})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Get location
    location = await db.locations.find_one({"scenarios": scenario_id})
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    chapter_id = location["chapter_id"]
    location_id = str(location["_id"])
    
    # Update user progress
    await db.user_progress.update_one(
        {"user_id": user_id},
        {
            "$inc": {"total_xp": xp_earned},
            "$addToSet": {
                f"chapter_progress.{chapter_id}.scenarios_completed": scenario_id
            },
            "$set": {
                "last_activity": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    # Recalculate chapter progress
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    chapter_progress = progress_doc.get("chapter_progress", {}).get(chapter_id, {})
    
    # Get total scenarios in chapter
    path = await db.learning_paths.find_one({"_id": ObjectId(chapter_id)})
    total_scenarios = 0
    for loc_id in path.get("locations", []):
        loc = await db.locations.find_one({"_id": ObjectId(loc_id)})
        if loc:
            total_scenarios += len(loc.get("scenarios", []))
    
    completed_scenarios = len(chapter_progress.get("scenarios_completed", []))
    progress_percent = int((completed_scenarios / total_scenarios * 100)) if total_scenarios > 0 else 0
    
    # Update chapter progress percent
    await db.user_progress.update_one(
        {"user_id": user_id},
        {
            "$set": {
                f"chapter_progress.{chapter_id}.progress_percent": progress_percent,
                f"chapter_progress.{chapter_id}.updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"success": True, "xp_earned": xp_earned, "chapter_progress": progress_percent}


@router.post("/progress/character-interaction")
async def record_character_interaction(
    character_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Record interaction with a character and update relationship"""
    
    # Get character
    character = await db.characters.find_one({"_id": ObjectId(character_id)})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Update relationship
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    if not progress_doc:
        raise HTTPException(status_code=404, detail="Progress not found")
    
    relationships = progress_doc.get("character_relationships", {})
    relationship = relationships.get(character_id, {
        "level": 0,
        "conversations": 0,
        "last_interaction": None
    })
    
    # Increment conversations and potentially level up
    relationship["conversations"] += 1
    relationship["last_interaction"] = datetime.utcnow()
    
    # Level up every 5 conversations (max level 10)
    new_level = min(relationship["conversations"] // 5, 10)
    if new_level > relationship["level"]:
        relationship["level"] = new_level
        # Unlock new topics
        relationship["unlocked_topics"] = character.get("topics", [])[:new_level]
    
    # Update database
    await db.user_progress.update_one(
        {"user_id": user_id},
        {
            "$set": {
                f"character_relationships.{character_id}": relationship,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"success": True, "relationship_level": relationship["level"]}


@router.post("/progress/activity-complete")
async def complete_activity(
    activity_id: str,
    activity_type: str,  # 'vocabulary', 'quiz', 'grammar', 'reading', 'writing'
    xp_earned: int,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Mark any activity as complete and update progress"""
    
    # Update user progress with activity completion
    await db.user_progress.update_one(
        {"user_id": user_id},
        {
            "$inc": {"total_xp": xp_earned},
            "$addToSet": {
                f"completed_activities.{activity_type}": activity_id
            },
            "$set": {
                "last_activity": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    # Find which location/chapter this activity belongs to
    location = None
    if activity_type == 'vocabulary':
        vocab_set = await db.vocab_sets.find_one({"_id": ObjectId(activity_id)})
        if vocab_set and vocab_set.get("location_id"):
            location = await db.locations.find_one({"_id": ObjectId(vocab_set["location_id"])})
    elif activity_type == 'quiz':
        quiz = await db.quizzes.find_one({"_id": ObjectId(activity_id)})
        if quiz and quiz.get("location_id"):
            location = await db.locations.find_one({"_id": ObjectId(quiz["location_id"])})
    elif activity_type == 'grammar':
        exercise = await db.grammar_exercises.find_one({"_id": ObjectId(activity_id)})
        if exercise and exercise.get("chapter_id"):
            # Grammar exercises are linked to chapters, not locations
            chapter_id = exercise["chapter_id"]
            await db.user_progress.update_one(
                {"user_id": user_id},
                {
                    "$addToSet": {
                        f"chapter_progress.{chapter_id}.activities_completed": activity_id
                    }
                }
            )
    
    # Update location/chapter progress if found
    if location:
        chapter_id = location["chapter_id"]
        location_id = str(location["_id"])
        
        await db.user_progress.update_one(
            {"user_id": user_id},
            {
                "$addToSet": {
                    f"chapter_progress.{chapter_id}.activities_completed": activity_id
                }
            }
        )
        
        # Recalculate progress percentage
        progress_doc = await db.user_progress.find_one({"user_id": user_id})
        chapter_progress = progress_doc.get("chapter_progress", {}).get(chapter_id, {})
        
        # Count total activities in chapter
        path = await db.learning_paths.find_one({"_id": ObjectId(chapter_id)})
        total_activities = 0
        for loc_id in path.get("locations", []):
            loc = await db.locations.find_one({"_id": ObjectId(loc_id)})
            if loc:
                total_activities += len(loc.get("scenarios", []))
                # Count vocab sets
                vocab_count = await db.vocab_sets.count_documents({"location_id": str(loc["_id"])})
                total_activities += vocab_count
                # Count quizzes
                quiz_count = await db.quizzes.count_documents({"location_id": str(loc["_id"])})
                total_activities += quiz_count
        
        # Count grammar exercises in chapter
        grammar_count = await db.grammar_exercises.count_documents({"chapter_id": chapter_id})
        total_activities += grammar_count
        
        # Calculate completion
        completed_scenarios = len(chapter_progress.get("scenarios_completed", []))
        completed_activities = len(chapter_progress.get("activities_completed", []))
        total_completed = completed_scenarios + completed_activities
        
        progress_percent = int((total_completed / total_activities * 100)) if total_activities > 0 else 0
        
        # Update progress
        await db.user_progress.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    f"chapter_progress.{chapter_id}.progress_percent": progress_percent,
                    f"chapter_progress.{chapter_id}.updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"success": True, "xp_earned": xp_earned, "chapter_progress": progress_percent}
    
    return {"success": True, "xp_earned": xp_earned}


@router.post("/progress/update-profile")
async def update_learning_profile(
    profile: LearningProfile,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update user's learning profile"""
    
    await db.user_progress.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "learning_profile": profile.dict(),
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    return {"success": True}
