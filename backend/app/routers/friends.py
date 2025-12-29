"""
Friend system API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from datetime import datetime

from ..db import get_db
from .auth import get_current_user
from ..models.gamification import FriendRequest, Friendship

router = APIRouter()


# Request models
class SendFriendRequestModel(BaseModel):
    friend_email: str


class RespondToRequestModel(BaseModel):
    status: str  # accepted or rejected


# Endpoints
@router.post("/request")
async def send_friend_request(
    request: SendFriendRequestModel,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Send a friend request"""
    
    # Find friend by email
    friend = await db.users.find_one({"email": request.friend_email})
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")
    
    friend_id = str(friend["_id"])
    
    # Can't friend yourself
    if friend_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
    
    # Check if already friends
    existing_friendship = await db.friendships.find_one({
        "$or": [
            {"user_id": user_id, "friend_id": friend_id},
            {"user_id": friend_id, "friend_id": user_id}
        ]
    })
    
    if existing_friendship:
        raise HTTPException(status_code=400, detail="Already friends")
    
    # Check if request already exists
    existing_request = await db.friend_requests.find_one({
        "$or": [
            {"from_user_id": user_id, "to_user_id": friend_id, "status": "pending"},
            {"from_user_id": friend_id, "to_user_id": user_id, "status": "pending"}
        ]
    })
    
    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already pending")
    
    # Create friend request
    friend_request = FriendRequest(
        from_user_id=user_id,
        to_user_id=friend_id
    )
    
    await db.friend_requests.insert_one(friend_request.dict())
    
    return {
        "success": True,
        "message": f"Friend request sent to {request.friend_email}"
    }


@router.get("/requests/incoming")
async def get_incoming_requests(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get incoming friend requests"""
    
    requests = await db.friend_requests.find({
        "to_user_id": user_id,
        "status": "pending"
    }).to_list(length=100)
    
    # Get sender details
    result = []
    for req in requests:
        sender = await db.users.find_one({"_id": req["from_user_id"]})
        if sender:
            result.append({
                "request_id": str(req["_id"]),
                "from_user_id": req["from_user_id"],
                "from_email": sender.get("email"),
                "created_at": req["created_at"]
            })
    
    return result


@router.get("/requests/outgoing")
async def get_outgoing_requests(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get outgoing friend requests"""
    
    requests = await db.friend_requests.find({
        "from_user_id": user_id,
        "status": "pending"
    }).to_list(length=100)
    
    # Get recipient details
    result = []
    for req in requests:
        recipient = await db.users.find_one({"_id": req["to_user_id"]})
        if recipient:
            result.append({
                "request_id": str(req["_id"]),
                "to_user_id": req["to_user_id"],
                "to_email": recipient.get("email"),
                "created_at": req["created_at"]
            })
    
    return result


@router.post("/requests/{request_id}/respond")
async def respond_to_friend_request(
    request_id: str,
    response: RespondToRequestModel,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Accept or reject a friend request"""
    
    if response.status not in ["accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Get friend request
    friend_request = await db.friend_requests.find_one({
        "_id": request_id,
        "to_user_id": user_id,
        "status": "pending"
    })
    
    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    # Update request status
    await db.friend_requests.update_one(
        {"_id": request_id},
        {
            "$set": {
                "status": response.status,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # If accepted, create friendship
    if response.status == "accepted":
        friendship = Friendship(
            user_id=user_id,
            friend_id=friend_request["from_user_id"]
        )
        await db.friendships.insert_one(friendship.dict())
        
        # Create reverse friendship
        reverse_friendship = Friendship(
            user_id=friend_request["from_user_id"],
            friend_id=user_id
        )
        await db.friendships.insert_one(reverse_friendship.dict())
    
    return {
        "success": True,
        "status": response.status
    }


@router.get("/list")
async def get_friends(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get list of friends"""
    
    friendships = await db.friendships.find({
        "user_id": user_id
    }).to_list(length=1000)
    
    # Get friend details and gamification stats
    friends = []
    for friendship in friendships:
        friend_id = friendship["friend_id"]
        
        # Get user details
        friend = await db.users.find_one({"_id": friend_id})
        if not friend:
            continue
        
        # Get gamification stats
        friend_level = await db.user_levels.find_one({"user_id": friend_id})
        
        friends.append({
            "user_id": friend_id,
            "email": friend.get("email"),
            "level": friend_level.get("level", 1) if friend_level else 1,
            "total_xp": friend_level.get("total_xp", 0) if friend_level else 0,
            "current_streak": friend_level.get("current_streak", 0) if friend_level else 0,
            "friends_since": friendship["created_at"]
        })
    
    return friends


@router.delete("/{friend_id}")
async def remove_friend(
    friend_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Remove a friend"""
    
    # Delete both friendship records
    result1 = await db.friendships.delete_one({
        "user_id": user_id,
        "friend_id": friend_id
    })
    
    result2 = await db.friendships.delete_one({
        "user_id": friend_id,
        "friend_id": user_id
    })
    
    if result1.deleted_count == 0 and result2.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Friendship not found")
    
    return {
        "success": True,
        "message": "Friend removed"
    }


@router.get("/leaderboard")
async def get_friends_leaderboard(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get leaderboard of friends"""
    
    # Get friend IDs
    friendships = await db.friendships.find({
        "user_id": user_id
    }).to_list(length=1000)
    
    friend_ids = [f["friend_id"] for f in friendships]
    friend_ids.append(user_id)  # Include self
    
    # Get gamification stats for all friends
    friend_levels = await db.user_levels.find({
        "user_id": {"$in": friend_ids}
    }).sort("total_xp", -1).to_list(length=1000)
    
    # Build leaderboard
    leaderboard = []
    for idx, friend_level in enumerate(friend_levels):
        friend = await db.users.find_one({"_id": friend_level["user_id"]})
        if friend:
            leaderboard.append({
                "rank": idx + 1,
                "user_id": friend_level["user_id"],
                "email": friend.get("email"),
                "level": friend_level.get("level", 1),
                "total_xp": friend_level.get("total_xp", 0),
                "current_streak": friend_level.get("current_streak", 0),
                "is_you": friend_level["user_id"] == user_id
            })
    
    return leaderboard


@router.get("/search")
async def search_users(
    query: str,
    limit: int = 10,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Search for users by email"""
    
    # Search users by email (case-insensitive)
    users = await db.users.find({
        "email": {"$regex": query, "$options": "i"},
        "_id": {"$ne": user_id}  # Exclude self
    }).limit(limit).to_list(length=limit)
    
    # Get friendship status for each user
    result = []
    for user in users:
        user_id_str = str(user["_id"])
        
        # Check if already friends
        is_friend = await db.friendships.find_one({
            "user_id": user_id,
            "friend_id": user_id_str
        })
        
        # Check if request pending
        pending_request = await db.friend_requests.find_one({
            "$or": [
                {"from_user_id": user_id, "to_user_id": user_id_str, "status": "pending"},
                {"from_user_id": user_id_str, "to_user_id": user_id, "status": "pending"}
            ]
        })
        
        # Get level
        user_level = await db.user_levels.find_one({"user_id": user_id_str})
        
        result.append({
            "user_id": user_id_str,
            "email": user.get("email"),
            "level": user_level.get("level", 1) if user_level else 1,
            "is_friend": bool(is_friend),
            "request_pending": bool(pending_request)
        })
    
    return result
