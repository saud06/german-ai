"""
Leaderboard endpoints for gamification
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from ..db import get_db
from ..security import get_current_user_id

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


class LeaderboardEntry(BaseModel):
    """Single leaderboard entry"""
    user_id: str
    name: str
    rank: int
    total_xp: int
    level: int
    streak: int
    scenarios_completed: int
    achievements_unlocked: int
    avatar: Optional[str] = None
    is_current_user: bool = False


class LeaderboardResponse(BaseModel):
    """Leaderboard response with entries and metadata"""
    entries: List[LeaderboardEntry]
    current_user_entry: Optional[LeaderboardEntry] = None
    total_users: int
    period: str  # "all_time", "weekly", "monthly"
    last_updated: datetime


@router.get("/global", response_model=LeaderboardResponse)
async def get_global_leaderboard(
    period: str = Query("all_time", regex="^(all_time|weekly|monthly)$"),
    limit: int = Query(100, ge=10, le=500),
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    Get global leaderboard ranked by total XP
    
    Periods:
    - all_time: All-time rankings
    - weekly: Last 7 days
    - monthly: Last 30 days
    """
    # Calculate time filter
    now = datetime.now(timezone.utc)
    time_filter = {}
    
    if period == "weekly":
        week_ago = now - timedelta(days=7)
        time_filter = {"updated_at": {"$gte": week_ago}}
    elif period == "monthly":
        month_ago = now - timedelta(days=30)
        time_filter = {"updated_at": {"$gte": month_ago}}
    
    # Get user stats with XP
    pipeline = [
        {"$match": time_filter} if time_filter else {"$match": {}},
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {
            "$project": {
                "user_id": "$user_id",
                "name": "$user.name",
                "email": "$user.email",
                "total_xp": 1,
                "level": 1,
                "streak": 1,
                "scenarios_completed": {"$ifNull": ["$scenarios_completed", 0]},
                "achievements_unlocked": {"$ifNull": ["$achievements_unlocked", 0]},
                "avatar": {"$ifNull": ["$user.avatar", None]}
            }
        },
        {"$sort": {"total_xp": -1}},
        {"$limit": limit}
    ]
    
    user_stats = await db.user_stats.aggregate(pipeline).to_list(length=limit)
    
    # Add ranks
    entries = []
    current_user_entry = None
    
    for idx, stat in enumerate(user_stats):
        entry = LeaderboardEntry(
            user_id=str(stat["user_id"]),
            name=stat.get("name", "Anonymous"),
            rank=idx + 1,
            total_xp=stat.get("total_xp", 0),
            level=stat.get("level", 1),
            streak=stat.get("streak", 0),
            scenarios_completed=stat.get("scenarios_completed", 0),
            achievements_unlocked=stat.get("achievements_unlocked", 0),
            avatar=stat.get("avatar"),
            is_current_user=(str(stat["user_id"]) == user_id)
        )
        entries.append(entry)
        
        if str(stat["user_id"]) == user_id:
            current_user_entry = entry
    
    # If current user not in top N, find their rank
    if not current_user_entry:
        user_stat = await db.user_stats.find_one({"user_id": user_id})
        if user_stat:
            # Count users with more XP
            higher_ranked = await db.user_stats.count_documents({
                "total_xp": {"$gt": user_stat.get("total_xp", 0)}
            })
            
            user_doc = await db.users.find_one({"_id": user_id})
            current_user_entry = LeaderboardEntry(
                user_id=user_id,
                name=user_doc.get("name", "You") if user_doc else "You",
                rank=higher_ranked + 1,
                total_xp=user_stat.get("total_xp", 0),
                level=user_stat.get("level", 1),
                streak=user_stat.get("streak", 0),
                scenarios_completed=user_stat.get("scenarios_completed", 0),
                achievements_unlocked=user_stat.get("achievements_unlocked", 0),
                avatar=user_doc.get("avatar") if user_doc else None,
                is_current_user=True
            )
    
    # Get total users count
    total_users = await db.user_stats.count_documents({})
    
    return LeaderboardResponse(
        entries=entries,
        current_user_entry=current_user_entry,
        total_users=total_users,
        period=period,
        last_updated=now
    )


@router.get("/streak", response_model=LeaderboardResponse)
async def get_streak_leaderboard(
    limit: int = Query(100, ge=10, le=500),
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    Get leaderboard ranked by current streak
    """
    # Get user stats sorted by streak
    pipeline = [
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {
            "$project": {
                "user_id": "$user_id",
                "name": "$user.name",
                "total_xp": 1,
                "level": 1,
                "streak": {"$ifNull": ["$streak", 0]},
                "scenarios_completed": {"$ifNull": ["$scenarios_completed", 0]},
                "achievements_unlocked": {"$ifNull": ["$achievements_unlocked", 0]},
                "avatar": {"$ifNull": ["$user.avatar", None]}
            }
        },
        {"$sort": {"streak": -1, "total_xp": -1}},
        {"$limit": limit}
    ]
    
    user_stats = await db.user_stats.aggregate(pipeline).to_list(length=limit)
    
    # Add ranks
    entries = []
    current_user_entry = None
    
    for idx, stat in enumerate(user_stats):
        entry = LeaderboardEntry(
            user_id=str(stat["user_id"]),
            name=stat.get("name", "Anonymous"),
            rank=idx + 1,
            total_xp=stat.get("total_xp", 0),
            level=stat.get("level", 1),
            streak=stat.get("streak", 0),
            scenarios_completed=stat.get("scenarios_completed", 0),
            achievements_unlocked=stat.get("achievements_unlocked", 0),
            avatar=stat.get("avatar"),
            is_current_user=(str(stat["user_id"]) == user_id)
        )
        entries.append(entry)
        
        if str(stat["user_id"]) == user_id:
            current_user_entry = entry
    
    # If current user not in top N, find their rank
    if not current_user_entry:
        user_stat = await db.user_stats.find_one({"user_id": user_id})
        if user_stat:
            # Count users with higher streak
            higher_ranked = await db.user_stats.count_documents({
                "streak": {"$gt": user_stat.get("streak", 0)}
            })
            
            user_doc = await db.users.find_one({"_id": user_id})
            current_user_entry = LeaderboardEntry(
                user_id=user_id,
                name=user_doc.get("name", "You") if user_doc else "You",
                rank=higher_ranked + 1,
                total_xp=user_stat.get("total_xp", 0),
                level=user_stat.get("level", 1),
                streak=user_stat.get("streak", 0),
                scenarios_completed=user_stat.get("scenarios_completed", 0),
                achievements_unlocked=user_stat.get("achievements_unlocked", 0),
                avatar=user_doc.get("avatar") if user_doc else None,
                is_current_user=True
            )
    
    total_users = await db.user_stats.count_documents({})
    
    return LeaderboardResponse(
        entries=entries,
        current_user_entry=current_user_entry,
        total_users=total_users,
        period="all_time",
        last_updated=datetime.now(timezone.utc)
    )


@router.get("/scenarios", response_model=LeaderboardResponse)
async def get_scenarios_leaderboard(
    limit: int = Query(100, ge=10, le=500),
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    Get leaderboard ranked by scenarios completed
    """
    # Get user stats sorted by scenarios
    pipeline = [
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {
            "$project": {
                "user_id": "$user_id",
                "name": "$user.name",
                "total_xp": 1,
                "level": 1,
                "streak": {"$ifNull": ["$streak", 0]},
                "scenarios_completed": {"$ifNull": ["$scenarios_completed", 0]},
                "achievements_unlocked": {"$ifNull": ["$achievements_unlocked", 0]},
                "avatar": {"$ifNull": ["$user.avatar", None]}
            }
        },
        {"$sort": {"scenarios_completed": -1, "total_xp": -1}},
        {"$limit": limit}
    ]
    
    user_stats = await db.user_stats.aggregate(pipeline).to_list(length=limit)
    
    # Add ranks
    entries = []
    current_user_entry = None
    
    for idx, stat in enumerate(user_stats):
        entry = LeaderboardEntry(
            user_id=str(stat["user_id"]),
            name=stat.get("name", "Anonymous"),
            rank=idx + 1,
            total_xp=stat.get("total_xp", 0),
            level=stat.get("level", 1),
            streak=stat.get("streak", 0),
            scenarios_completed=stat.get("scenarios_completed", 0),
            achievements_unlocked=stat.get("achievements_unlocked", 0),
            avatar=stat.get("avatar"),
            is_current_user=(str(stat["user_id"]) == user_id)
        )
        entries.append(entry)
        
        if str(stat["user_id"]) == user_id:
            current_user_entry = entry
    
    # If current user not in top N, find their rank
    if not current_user_entry:
        user_stat = await db.user_stats.find_one({"user_id": user_id})
        if user_stat:
            # Count users with more scenarios
            higher_ranked = await db.user_stats.count_documents({
                "scenarios_completed": {"$gt": user_stat.get("scenarios_completed", 0)}
            })
            
            user_doc = await db.users.find_one({"_id": user_id})
            current_user_entry = LeaderboardEntry(
                user_id=user_id,
                name=user_doc.get("name", "You") if user_doc else "You",
                rank=higher_ranked + 1,
                total_xp=user_stat.get("total_xp", 0),
                level=user_stat.get("level", 1),
                streak=user_stat.get("streak", 0),
                scenarios_completed=user_stat.get("scenarios_completed", 0),
                achievements_unlocked=user_stat.get("achievements_unlocked", 0),
                avatar=user_doc.get("avatar") if user_doc else None,
                is_current_user=True
            )
    
    total_users = await db.user_stats.count_documents({})
    
    return LeaderboardResponse(
        entries=entries,
        current_user_entry=current_user_entry,
        total_users=total_users,
        period="all_time",
        last_updated=datetime.now(timezone.utc)
    )
