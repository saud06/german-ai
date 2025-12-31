from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..db import get_db
from ..security import auth_dep
from ..models.journey import (
    JourneyType, SelectJourneyRequest, SwitchJourneyRequest,
    JourneyResponse, UserJourney, JourneyProgress, LearningJourneys
)
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/journeys")

@router.post("/select")
async def select_journey(
    request: SelectJourneyRequest,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Add a new journey for the user or update existing
    """
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        learning_journeys = user.get("learning_journeys", {
            "active_journey_id": None,
            "journeys": [],
            "onboarding_completed": False
        })
        
        journey_id = f"{request.journey_type}_{len(learning_journeys.get('journeys', []))}"
        
        existing_journey = next(
            (j for j in learning_journeys.get("journeys", []) if j["type"] == request.journey_type),
            None
        )
        
        if existing_journey:
            raise HTTPException(
                status_code=400,
                detail=f"You already have a {request.journey_type} journey. Switch to it instead."
            )
        
        new_journey = {
            "id": journey_id,
            "type": request.journey_type,
            "is_primary": request.is_primary or len(learning_journeys.get("journeys", [])) == 0,
            "level": request.level,
            "created_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow(),
            "progress": {
                "lessons_completed": 0,
                "scenarios_completed": 0,
                "quizzes_completed": 0,
                "total_xp": 0,
                "current_streak": 0,
                "milestones": []
            }
        }
        
        if "journeys" not in learning_journeys:
            learning_journeys["journeys"] = []
        
        learning_journeys["journeys"].append(new_journey)
        
        if not learning_journeys.get("active_journey_id"):
            learning_journeys["active_journey_id"] = journey_id
        
        if len(learning_journeys["journeys"]) == 1:
            learning_journeys["onboarding_completed"] = True
            learning_journeys["onboarding_completed_at"] = datetime.utcnow()
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"learning_journeys": learning_journeys}}
        )
        
        return {
            "success": True,
            "journey": new_journey,
            "message": f"{request.journey_type.capitalize()} journey created successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting journey: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-journeys")
async def get_my_journeys(
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Get all journeys for the current user
    """
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        learning_journeys = user.get("learning_journeys", {
            "active_journey_id": None,
            "journeys": [],
            "onboarding_completed": False
        })
        
        configurations = await db.journey_configurations.find({}).to_list(length=10)
        config_map = {config["journey_type"]: config for config in configurations}
        
        journeys_with_config = []
        for journey in learning_journeys.get("journeys", []):
            journey_data = journey.copy()
            journey_data["configuration"] = config_map.get(journey["type"])
            journeys_with_config.append(journey_data)
        
        return {
            "active_journey_id": learning_journeys.get("active_journey_id"),
            "journeys": journeys_with_config,
            "onboarding_completed": learning_journeys.get("onboarding_completed", False)
        }
    
    except Exception as e:
        logger.error(f"Error getting journeys: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/switch")
async def switch_journey(
    request: SwitchJourneyRequest,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Switch to a different active journey
    """
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        learning_journeys = user.get("learning_journeys", {})
        
        journey_exists = any(
            j["id"] == request.journey_id
            for j in learning_journeys.get("journeys", [])
        )
        
        if not journey_exists:
            raise HTTPException(status_code=404, detail="Journey not found")
        
        for journey in learning_journeys["journeys"]:
            if journey["id"] == request.journey_id:
                journey["last_accessed"] = datetime.utcnow()
        
        learning_journeys["active_journey_id"] = request.journey_id
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"learning_journeys": learning_journeys}}
        )
        
        return {
            "success": True,
            "active_journey_id": request.journey_id,
            "message": "Journey switched successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching journey: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{journey_id}")
async def remove_journey(
    journey_id: str,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Remove a journey (must keep at least one)
    """
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        learning_journeys = user.get("learning_journeys", {})
        
        if len(learning_journeys.get("journeys", [])) <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove your last journey. You must have at least one active journey."
            )
        
        learning_journeys["journeys"] = [
            j for j in learning_journeys["journeys"]
            if j["id"] != journey_id
        ]
        
        if learning_journeys.get("active_journey_id") == journey_id:
            learning_journeys["active_journey_id"] = learning_journeys["journeys"][0]["id"]
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"learning_journeys": learning_journeys}}
        )
        
        return {
            "success": True,
            "message": "Journey removed successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing journey: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configurations")
async def get_journey_configurations(db = Depends(get_db)):
    """
    Get all available journey configurations
    """
    try:
        configurations = await db.journey_configurations.find({}).to_list(length=10)
        
        for config in configurations:
            config["_id"] = str(config["_id"])
        
        return {"configurations": configurations}
    
    except Exception as e:
        logger.error(f"Error getting configurations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active", response_model=JourneyResponse)
async def get_active_journey(
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Get the active journey with full configuration"""
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    journeys_data = user.get("learning_journeys", {})
    active_id = journeys_data.get("active_journey_id")
    
    if not active_id:
        return {"active_journey": None}
    
    # Find active journey
    active_journey = None
    for journey in journeys_data.get("journeys", []):
        if journey.get("id") == active_id:
            active_journey = journey
            break
    
    if not active_journey:
        return {"active_journey": None}
    
    # Get configuration
    configs = db["journey_configurations"]
    config = await configs.find_one(
        {"journey_type": active_journey["type"]}
    )
    
    if config:
        config["_id"] = str(config["_id"])
        active_journey["configuration"] = config
    
    return {"active_journey": active_journey}

@router.get("/content-mappings")
async def get_content_mappings(
    content_type: Optional[str] = None,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Get content mappings for journey-aware filtering"""
    query = {}
    if content_type:
        query["content_type"] = content_type
    
    mappings_collection = db["journey_content_mappings"]
    mappings = await mappings_collection.find(query).to_list(length=1000)
    
    # Convert ObjectId to string
    for mapping in mappings:
        mapping["_id"] = str(mapping["_id"])
    
    return {"mappings": mappings}
