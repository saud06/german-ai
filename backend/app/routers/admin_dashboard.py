"""
Admin Dashboard Router
Administrative functions for organization management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from ..db import get_db
from ..routers.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


async def check_admin_access(organization_id: str, user_id: str, db) -> bool:
    """Check if user has admin access"""
    member = await db["organization_members"].find_one({
        "organization_id": organization_id,
        "user_id": user_id
    })
    
    return member and member.get("role") in ["owner", "admin"]


# User Management

@router.get("/users")
async def list_all_users(
    organization_id: str,
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """List all users in organization"""
    if not await check_admin_access(organization_id, user_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get organization members
    members = await db["organization_members"].find({
        "organization_id": organization_id
    }).to_list(length=1000)
    
    user_ids = [m["user_id"] for m in members]
    
    # Build query
    query = {"_id": {"$in": user_ids}}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    # Get users
    users = await db["users"].find(query).skip(skip).limit(limit).to_list(length=limit)
    total = await db["users"].count_documents(query)
    
    # Enrich with stats
    enriched_users = []
    for user in users:
        user["_id"] = str(user["_id"])
        
        # Get user stats
        stats = await db["user_stats"].find_one({"user_id": str(user["_id"])})
        user["stats"] = stats if stats else {}
        
        # Get member info
        member = next((m for m in members if m["user_id"] == str(user["_id"])), None)
        user["role"] = member.get("role") if member else "viewer"
        user["joined_at"] = member.get("joined_at") if member else None
        
        enriched_users.append(user)
    
    return {
        "users": enriched_users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/users/{target_user_id}")
async def get_user_details(
    target_user_id: str,
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get detailed user information"""
    if not await check_admin_access(organization_id, user_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get user
    user = await db["users"].find_one({"_id": target_user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["_id"] = str(user["_id"])
    
    # Get stats
    stats = await db["user_stats"].find_one({"user_id": target_user_id})
    
    # Get recent activity
    recent_scenarios = await db["conversation_states"].find({
        "user_id": target_user_id
    }).sort("created_at", -1).limit(10).to_list(length=10)
    
    recent_achievements = await db["user_achievements"].find({
        "user_id": target_user_id
    }).sort("unlocked_at", -1).limit(10).to_list(length=10)
    
    return {
        "user": user,
        "stats": stats,
        "recent_scenarios": recent_scenarios,
        "recent_achievements": recent_achievements
    }


@router.patch("/users/{target_user_id}/role")
async def update_user_role(
    target_user_id: str,
    organization_id: str,
    role: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Update user's role in organization"""
    if not await check_admin_access(organization_id, user_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Validate role
    valid_roles = ["viewer", "member", "admin", "owner"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )
    
    # Cannot change owner role
    member = await db["organization_members"].find_one({
        "organization_id": organization_id,
        "user_id": target_user_id
    })
    
    if member and member.get("role") == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change owner role"
        )
    
    # Update role
    result = await db["organization_members"].update_one(
        {
            "organization_id": organization_id,
            "user_id": target_user_id
        },
        {"$set": {"role": role}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in organization"
        )
    
    return {"message": "User role updated successfully"}


@router.delete("/users/{target_user_id}")
async def suspend_user(
    target_user_id: str,
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Suspend user from organization"""
    if not await check_admin_access(organization_id, user_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Remove from organization
    result = await db["organization_members"].delete_one({
        "organization_id": organization_id,
        "user_id": target_user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in organization"
        )
    
    return {"message": "User suspended successfully"}


# Content Management

@router.get("/scenarios")
async def list_scenarios_admin(
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """List all scenarios with usage stats"""
    if not await check_admin_access(organization_id, user_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    scenarios = await db["scenarios"].find().to_list(length=1000)
    
    # Get usage stats for each scenario
    enriched_scenarios = []
    for scenario in scenarios:
        scenario["_id"] = str(scenario["_id"])
        
        # Count starts and completions
        starts = await db["conversation_states"].count_documents({
            "scenario_id": str(scenario["_id"])
        })
        
        completions = await db["conversation_states"].count_documents({
            "scenario_id": str(scenario["_id"]),
            "status": "completed"
        })
        
        scenario["stats"] = {
            "starts": starts,
            "completions": completions,
            "completion_rate": (completions / starts * 100) if starts > 0 else 0
        }
        
        enriched_scenarios.append(scenario)
    
    return {"scenarios": enriched_scenarios, "total": len(enriched_scenarios)}


@router.get("/achievements")
async def list_achievements_admin(
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """List all achievements with unlock stats"""
    if not await check_admin_access(organization_id, user_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    achievements = await db["achievements"].find().to_list(length=1000)
    
    # Get unlock stats
    enriched_achievements = []
    for achievement in achievements:
        achievement["_id"] = str(achievement["_id"])
        
        # Count unlocks
        unlocks = await db["user_achievements"].count_documents({
            "achievement_code": achievement.get("code")
        })
        
        achievement["stats"] = {
            "unlocks": unlocks
        }
        
        enriched_achievements.append(achievement)
    
    return {"achievements": enriched_achievements, "total": len(enriched_achievements)}


# Analytics

@router.get("/analytics/overview")
async def get_analytics_overview(
    organization_id: str,
    days: int = 30,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get organization analytics overview"""
    if not await check_admin_access(organization_id, user_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get member IDs
    members = await db["organization_members"].find({
        "organization_id": organization_id
    }).to_list(length=1000)
    user_ids = [m["user_id"] for m in members]
    
    # Total users
    total_users = len(user_ids)
    
    # Active users (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users = await db["conversation_states"].distinct(
        "user_id",
        {
            "user_id": {"$in": user_ids},
            "created_at": {"$gte": seven_days_ago}
        }
    )
    
    # Total scenarios completed
    scenarios_completed = await db["conversation_states"].count_documents({
        "user_id": {"$in": user_ids},
        "status": "completed",
        "created_at": {"$gte": start_date}
    })
    
    # Total achievements unlocked
    achievements_unlocked = await db["user_achievements"].count_documents({
        "user_id": {"$in": user_ids},
        "unlocked_at": {"$gte": start_date}
    })
    
    # API usage
    api_calls = await db["api_usage"].count_documents({
        "organization_id": organization_id,
        "created_at": {"$gte": start_date}
    })
    
    # Growth metrics
    new_users = await db["organization_members"].count_documents({
        "organization_id": organization_id,
        "joined_at": {"$gte": start_date}
    })
    
    return {
        "period_days": days,
        "total_users": total_users,
        "active_users": len(active_users),
        "new_users": new_users,
        "scenarios_completed": scenarios_completed,
        "achievements_unlocked": achievements_unlocked,
        "api_calls": api_calls
    }


@router.get("/analytics/activity")
async def get_activity_timeline(
    organization_id: str,
    days: int = 30,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get activity timeline"""
    if not await check_admin_access(organization_id, user_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get member IDs
    members = await db["organization_members"].find({
        "organization_id": organization_id
    }).to_list(length=1000)
    user_ids = [m["user_id"] for m in members]
    
    # Activity by day
    pipeline = [
        {
            "$match": {
                "user_id": {"$in": user_ids},
                "created_at": {"$gte": start_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "scenarios": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    activity = await db["conversation_states"].aggregate(pipeline).to_list(length=days)
    
    return {
        "period_days": days,
        "activity": activity
    }


# Audit Logs

@router.get("/audit-logs")
async def get_audit_logs(
    organization_id: str,
    limit: int = 100,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get organization audit logs"""
    if not await check_admin_access(organization_id, user_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    logs = await db["audit_logs"].find({
        "organization_id": organization_id
    }).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    # Enrich with user names
    for log in logs:
        log["_id"] = str(log["_id"])
        user = await db["users"].find_one({"_id": log["user_id"]})
        log["user_name"] = user.get("name") if user else "Unknown"
    
    return {"logs": logs, "total": len(logs)}


# Reports

@router.get("/reports/user-engagement")
async def get_user_engagement_report(
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user engagement report"""
    if not await check_admin_access(organization_id, user_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get member IDs
    members = await db["organization_members"].find({
        "organization_id": organization_id
    }).to_list(length=1000)
    user_ids = [m["user_id"] for m in members]
    
    # Engagement metrics per user
    engagement = []
    for uid in user_ids:
        user = await db["users"].find_one({"_id": uid})
        if not user:
            continue
        
        # Get stats
        scenarios = await db["conversation_states"].count_documents({"user_id": uid})
        achievements = await db["user_achievements"].count_documents({"user_id": uid})
        
        stats = await db["user_stats"].find_one({"user_id": uid})
        
        engagement.append({
            "user_id": uid,
            "user_name": user.get("name", "Unknown"),
            "scenarios_completed": scenarios,
            "achievements_unlocked": achievements,
            "total_xp": stats.get("total_xp", 0) if stats else 0,
            "current_streak": stats.get("current_streak", 0) if stats else 0
        })
    
    # Sort by XP
    engagement.sort(key=lambda x: x["total_xp"], reverse=True)
    
    return {"engagement": engagement, "total_users": len(engagement)}
