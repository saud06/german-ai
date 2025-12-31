"""
API routes for achievements and gamification
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

from app.db import get_db
from app.security import auth_dep
from app.services.achievement_service import AchievementService
from app.models.achievement import UserStats, Achievement


router = APIRouter(prefix="/api/v1/achievements", tags=["achievements"])


class XPResponse(BaseModel):
    """Response for XP operations"""
    leveled_up: bool
    old_level: int
    new_level: int
    xp_gained: int
    total_xp: int
    xp_to_next_level: int


class StreakResponse(BaseModel):
    """Response for streak operations"""
    streak_continued: bool
    current_streak: int
    longest_streak: int


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    user_id: str
    value: int
    rank: int


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Get user's gamification statistics"""
    service = AchievementService(db)
    stats = await service.get_user_stats(user_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User stats not found"
        )
    
    return stats


@router.get("/list")
async def get_achievements(
    unlocked_only: bool = False,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Get all achievements with user's progress"""
    service = AchievementService(db)
    achievements = await service.get_user_achievements(user_id, unlocked_only)
    
    return {
        "achievements": achievements,
        "total": len(achievements)
    }


@router.get("/leaderboard/{leaderboard_type}")
async def get_leaderboard(
    leaderboard_type: str,
    limit: int = 100,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Get leaderboard
    Types: xp, level, streak, scenarios, quizzes
    """
    service = AchievementService(db)
    leaderboard = await service.get_leaderboard(leaderboard_type, limit)
    
    # Find user's rank
    user_rank = None
    for idx, entry in enumerate(leaderboard):
        if entry["user_id"] == user_id:
            user_rank = idx + 1
            break
    
    return {
        "leaderboard": leaderboard,
        "user_rank": user_rank,
        "type": leaderboard_type
    }


@router.post("/streak/update", response_model=StreakResponse)
async def update_streak(
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Update user's daily streak"""
    service = AchievementService(db)
    result = await service.update_streak(user_id)
    
    return StreakResponse(**result)


@router.post("/initialize")
async def initialize_achievements(
    db = Depends(get_db)
):
    """Initialize achievement definitions (admin only)"""
    service = AchievementService(db)
    await service.initialize_achievements()
    
    return {"message": "Achievements initialized successfully"}
