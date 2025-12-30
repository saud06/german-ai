"""
Gamification API endpoints for XP, levels, streaks, leaderboards, and challenges
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

from ..db import get_db
from .auth import get_current_user
from ..services.gamification_service import GamificationService
from ..models.gamification import UserLevel, Leaderboard, WeeklyChallenge

router = APIRouter()


# Request models
class AwardXPRequest(BaseModel):
    event_type: str
    custom_xp: Optional[int] = None
    description: Optional[str] = None


class CreateChallengeRequest(BaseModel):
    title: str
    description: str
    challenge_type: str
    target: int
    xp_reward: int
    coin_reward: int
    gem_reward: int = 0


# Endpoints
@router.get("/profile")
async def get_gamification_profile(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's gamification profile"""
    service = GamificationService(db)
    user_level = await service.get_or_create_user_level(user_id)
    rank_info = await service.get_user_rank(user_id)
    
    return {
        **user_level.dict(),
        "rank": rank_info["rank"],
        "total_users": rank_info["total_users"],
        "percentile": rank_info["percentile"]
    }


@router.post("/xp/award")
async def award_xp(
    request: AwardXPRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Award XP to user"""
    service = GamificationService(db)
    result = await service.award_xp(
        user_id=user_id,
        event_type=request.event_type,
        custom_xp=request.custom_xp,
        description=request.description
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return result


@router.post("/streak/update")
async def update_streak(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update daily streak (call on daily login)"""
    service = GamificationService(db)
    result = await service.update_daily_streak(user_id)
    return result


@router.get("/streak/history")
async def get_streak_history(
    days: int = 30,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get streak history for the last N days"""
    from datetime import timedelta
    
    today = date.today()
    start_date = today - timedelta(days=days)
    
    streaks = await db.daily_streaks.find({
        "user_id": user_id,
        "date": {"$gte": start_date.isoformat()}
    }).sort("date", -1).to_list(length=days)
    
    # Convert ObjectId to string for JSON serialization
    for streak in streaks:
        if "_id" in streak:
            streak["_id"] = str(streak["_id"])
        if "created_at" in streak and hasattr(streak["created_at"], "isoformat"):
            streak["created_at"] = streak["created_at"].isoformat()
    
    return streaks


@router.get("/leaderboard")
async def get_leaderboard(
    leaderboard_type: str = "global",
    limit: int = 100,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get leaderboard rankings"""
    service = GamificationService(db)
    leaderboard = await service.get_leaderboard(
        leaderboard_type=leaderboard_type,
        user_id=user_id,
        limit=limit
    )
    
    return {
        "leaderboard": [entry.dict() for entry in leaderboard],
        "type": leaderboard_type
    }


@router.get("/rank")
async def get_user_rank(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's current rank"""
    service = GamificationService(db)
    return await service.get_user_rank(user_id)


@router.get("/challenges")
async def get_active_challenges(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all active weekly challenges"""
    service = GamificationService(db)
    challenges = await service.get_active_challenges()
    
    # Get user's progress on each challenge
    result = []
    for challenge in challenges:
        user_challenge = await db.user_challenges.find_one({
            "user_id": user_id,
            "challenge_id": challenge.id
        })
        
        result.append({
            **challenge.dict(),
            "user_progress": user_challenge.get("progress", 0) if user_challenge else 0,
            "user_completed": user_challenge.get("completed", False) if user_challenge else False,
            "user_claimed": user_challenge.get("claimed", False) if user_challenge else False
        })
    
    return result


@router.post("/challenges/create")
async def create_challenge(
    request: CreateChallengeRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new weekly challenge (admin only)"""
    service = GamificationService(db)
    challenge = await service.create_weekly_challenge(
        title=request.title,
        description=request.description,
        challenge_type=request.challenge_type,
        target=request.target,
        xp_reward=request.xp_reward,
        coin_reward=request.coin_reward,
        gem_reward=request.gem_reward
    )
    
    return challenge.dict()


@router.post("/challenges/{challenge_id}/claim")
async def claim_challenge_reward(
    challenge_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Claim reward for completed challenge"""
    service = GamificationService(db)
    result = await service.claim_challenge_reward(user_id, challenge_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return result


@router.get("/xp/history")
async def get_xp_history(
    limit: int = 50,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get XP earning history"""
    events = await db.xp_events.find({
        "user_id": user_id
    }).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    # Convert ObjectId and datetime to JSON-serializable formats
    for event in events:
        if "_id" in event:
            event["_id"] = str(event["_id"])
        if "created_at" in event and hasattr(event["created_at"], "isoformat"):
            event["created_at"] = event["created_at"].isoformat()
    
    return events


@router.get("/stats")
async def get_gamification_stats(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get comprehensive gamification statistics"""
    service = GamificationService(db)
    user_level = await service.get_or_create_user_level(user_id)
    rank_info = await service.get_user_rank(user_id)
    
    # Get recent XP events
    recent_xp = await db.xp_events.find({
        "user_id": user_id
    }).sort("created_at", -1).limit(10).to_list(length=10)
    
    # Convert ObjectId and datetime to JSON-serializable formats
    for event in recent_xp:
        if "_id" in event:
            event["_id"] = str(event["_id"])
        if "created_at" in event and hasattr(event["created_at"], "isoformat"):
            event["created_at"] = event["created_at"].isoformat()
    
    # Get active challenges progress
    challenges = await service.get_active_challenges()
    challenge_progress = []
    for challenge in challenges:
        user_challenge = await db.user_challenges.find_one({
            "user_id": user_id,
            "challenge_id": challenge.id
        })
        if user_challenge:
            challenge_progress.append({
                "title": challenge.title,
                "progress": user_challenge.get("progress", 0),
                "target": challenge.target,
                "completed": user_challenge.get("completed", False)
            })
    
    return {
        "level": user_level.level,
        "total_xp": user_level.total_xp,
        "current_xp": user_level.current_xp,
        "next_level_xp": user_level.next_level_xp,
        "current_streak": user_level.current_streak,
        "longest_streak": user_level.longest_streak,
        "rank": rank_info["rank"],
        "percentile": rank_info["percentile"],
        "coins": user_level.coins,
        "gems": user_level.gems,
        "statistics": {
            "lessons_completed": user_level.total_lessons_completed,
            "scenarios_completed": user_level.total_scenarios_completed,
            "quizzes_completed": user_level.total_quizzes_completed,
            "reviews_completed": user_level.total_reviews_completed,
            "words_learned": user_level.total_words_learned
        },
        "recent_xp": recent_xp[:5],
        "active_challenges": challenge_progress
    }


# Public endpoints
@router.get("/leaderboard/public")
async def get_public_leaderboard(
    limit: int = 10,
    db = Depends(get_db)
):
    """Get public leaderboard (no auth required)"""
    service = GamificationService(db)
    leaderboard = await service.get_leaderboard(limit=limit)
    
    return {
        "leaderboard": [entry.dict() for entry in leaderboard]
    }
