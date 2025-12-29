"""
Referral Program Router
User referral system with rewards and tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from ..db import get_db
from .auth import get_current_user
from pydantic import BaseModel
import secrets
import hashlib

router = APIRouter(prefix="/referrals", tags=["Referrals"])


class ReferralCode(BaseModel):
    """Referral code model"""
    code: str
    user_id: str
    uses: int = 0
    max_uses: Optional[int] = None
    expires_at: Optional[datetime] = None
    reward_type: str = "premium_days"  # premium_days, discount, credits
    reward_value: int = 7  # 7 days free premium
    active: bool = True


class ReferralReward(BaseModel):
    """Referral reward model"""
    referrer_id: str
    referred_id: str
    code: str
    reward_type: str
    reward_value: int
    claimed: bool = False
    claimed_at: Optional[datetime] = None


def generate_referral_code(user_id: str) -> str:
    """Generate a unique referral code"""
    # Create code from user_id hash + random string
    hash_part = hashlib.md5(user_id.encode()).hexdigest()[:4].upper()
    random_part = secrets.token_hex(3).upper()
    return f"{hash_part}{random_part}"


# Referral Code Management

@router.post("/code")
async def create_referral_code(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Create a referral code for user"""
    # Check if user already has an active code
    existing = await db["referral_codes"].find_one({
        "user_id": user_id,
        "active": True
    })
    
    if existing:
        return {
            "code": existing["code"],
            "uses": existing.get("uses", 0),
            "max_uses": existing.get("max_uses"),
            "message": "Using existing referral code"
        }
    
    # Generate new code
    code = generate_referral_code(user_id)
    
    # Ensure uniqueness
    while await db["referral_codes"].find_one({"code": code}):
        code = generate_referral_code(user_id)
    
    # Create referral code
    referral_doc = {
        "code": code,
        "user_id": user_id,
        "uses": 0,
        "max_uses": None,  # Unlimited
        "reward_type": "premium_days",
        "reward_value": 7,  # 7 days premium for both
        "active": True,
        "created_at": datetime.utcnow()
    }
    
    await db["referral_codes"].insert_one(referral_doc)
    
    return {
        "code": code,
        "uses": 0,
        "max_uses": None,
        "reward": "7 days premium for you and your friend",
        "message": "Referral code created successfully"
    }


@router.get("/code")
async def get_my_referral_code(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user's referral code"""
    code = await db["referral_codes"].find_one({
        "user_id": user_id,
        "active": True
    })
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No referral code found. Create one first."
        )
    
    # Get referral stats
    referrals = await db["referral_rewards"].count_documents({
        "referrer_id": user_id
    })
    
    pending_rewards = await db["referral_rewards"].count_documents({
        "referrer_id": user_id,
        "claimed": False
    })
    
    return {
        "code": code["code"],
        "uses": code.get("uses", 0),
        "total_referrals": referrals,
        "pending_rewards": pending_rewards,
        "reward": f"{code['reward_value']} days premium per referral",
        "share_url": f"https://german-ai.com/signup?ref={code['code']}"
    }


@router.post("/apply/{code}")
async def apply_referral_code(
    code: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Apply a referral code (for new users)"""
    # Check if code exists and is active
    referral_code = await db["referral_codes"].find_one({
        "code": code.upper(),
        "active": True
    })
    
    if not referral_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired referral code"
        )
    
    # Check if user is trying to use their own code
    if referral_code["user_id"] == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot use your own referral code"
        )
    
    # Check if user has already used a referral code
    existing_reward = await db["referral_rewards"].find_one({
        "referred_id": user_id
    })
    
    if existing_reward:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already used a referral code"
        )
    
    # Check max uses
    if referral_code.get("max_uses") and referral_code["uses"] >= referral_code["max_uses"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Referral code has reached maximum uses"
        )
    
    # Create rewards for both users
    reward_value = referral_code["reward_value"]
    
    # Reward for referrer
    referrer_reward = {
        "referrer_id": referral_code["user_id"],
        "referred_id": user_id,
        "code": code.upper(),
        "reward_type": referral_code["reward_type"],
        "reward_value": reward_value,
        "claimed": False,
        "created_at": datetime.utcnow()
    }
    await db["referral_rewards"].insert_one(referrer_reward)
    
    # Reward for referred user (immediate)
    referred_reward = {
        "referrer_id": referral_code["user_id"],
        "referred_id": user_id,
        "code": code.upper(),
        "reward_type": referral_code["reward_type"],
        "reward_value": reward_value,
        "claimed": True,
        "claimed_at": datetime.utcnow(),
        "created_at": datetime.utcnow()
    }
    await db["referral_rewards"].insert_one(referred_reward)
    
    # Apply reward immediately to referred user
    if referral_code["reward_type"] == "premium_days":
        # Extend premium subscription
        subscription = await db["subscriptions"].find_one({"user_id": user_id})
        if subscription:
            current_end = subscription.get("current_period_end", datetime.utcnow())
            new_end = current_end + timedelta(days=reward_value)
            
            await db["subscriptions"].update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "tier": "premium",
                        "current_period_end": new_end,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
    
    # Increment code usage
    await db["referral_codes"].update_one(
        {"_id": referral_code["_id"]},
        {"$inc": {"uses": 1}}
    )
    
    return {
        "message": f"Referral code applied! You received {reward_value} days of premium.",
        "reward_value": reward_value,
        "reward_type": referral_code["reward_type"]
    }


@router.get("/rewards")
async def get_my_rewards(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user's referral rewards"""
    rewards = await db["referral_rewards"].find({
        "referrer_id": user_id
    }).sort("created_at", -1).to_list(length=100)
    
    total_rewards = len(rewards)
    claimed_rewards = len([r for r in rewards if r.get("claimed")])
    pending_rewards = total_rewards - claimed_rewards
    
    # Calculate total value
    total_value = sum(r.get("reward_value", 0) for r in rewards if r.get("claimed"))
    
    return {
        "total_referrals": total_rewards,
        "claimed_rewards": claimed_rewards,
        "pending_rewards": pending_rewards,
        "total_value": total_value,
        "rewards": [
            {
                "referred_user_id": r["referred_id"],
                "reward_value": r["reward_value"],
                "reward_type": r["reward_type"],
                "claimed": r.get("claimed", False),
                "claimed_at": r.get("claimed_at"),
                "created_at": r["created_at"]
            }
            for r in rewards
        ]
    }


@router.post("/rewards/claim")
async def claim_rewards(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Claim all pending referral rewards"""
    # Get pending rewards
    pending = await db["referral_rewards"].find({
        "referrer_id": user_id,
        "claimed": False
    }).to_list(length=100)
    
    if not pending:
        return {
            "message": "No pending rewards to claim",
            "claimed_count": 0,
            "total_value": 0
        }
    
    # Calculate total value
    total_value = sum(r.get("reward_value", 0) for r in pending)
    
    # Apply rewards
    if pending[0]["reward_type"] == "premium_days":
        # Extend premium subscription
        subscription = await db["subscriptions"].find_one({"user_id": user_id})
        if subscription:
            current_end = subscription.get("current_period_end", datetime.utcnow())
            new_end = current_end + timedelta(days=total_value)
            
            await db["subscriptions"].update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "tier": "premium",
                        "current_period_end": new_end,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
    
    # Mark rewards as claimed
    await db["referral_rewards"].update_many(
        {
            "referrer_id": user_id,
            "claimed": False
        },
        {
            "$set": {
                "claimed": True,
                "claimed_at": datetime.utcnow()
            }
        }
    )
    
    return {
        "message": f"Claimed {len(pending)} rewards worth {total_value} days of premium!",
        "claimed_count": len(pending),
        "total_value": total_value
    }


@router.get("/leaderboard")
async def get_referral_leaderboard(
    limit: int = 10,
    db=Depends(get_db)
):
    """Get top referrers leaderboard"""
    pipeline = [
        {
            "$group": {
                "_id": "$referrer_id",
                "total_referrals": {"$sum": 1},
                "total_value": {"$sum": "$reward_value"}
            }
        },
        {"$sort": {"total_referrals": -1}},
        {"$limit": limit}
    ]
    
    leaderboard = await db["referral_rewards"].aggregate(pipeline).to_list(length=limit)
    
    # Enrich with user names
    enriched = []
    for entry in leaderboard:
        user = await db["users"].find_one({"_id": entry["_id"]})
        enriched.append({
            "user_id": entry["_id"],
            "user_name": user.get("name", "Anonymous") if user else "Anonymous",
            "total_referrals": entry["total_referrals"],
            "total_value": entry["total_value"]
        })
    
    return {
        "leaderboard": enriched,
        "total": len(enriched)
    }


@router.get("/stats")
async def get_referral_stats(
    db=Depends(get_db)
):
    """Get overall referral program statistics"""
    total_codes = await db["referral_codes"].count_documents({"active": True})
    total_referrals = await db["referral_rewards"].count_documents({})
    total_claimed = await db["referral_rewards"].count_documents({"claimed": True})
    
    # Get total value distributed
    pipeline = [
        {"$match": {"claimed": True}},
        {"$group": {"_id": None, "total_value": {"$sum": "$reward_value"}}}
    ]
    result = await db["referral_rewards"].aggregate(pipeline).to_list(length=1)
    total_value = result[0]["total_value"] if result else 0
    
    return {
        "total_active_codes": total_codes,
        "total_referrals": total_referrals,
        "total_claimed_rewards": total_claimed,
        "total_value_distributed": total_value,
        "average_referrals_per_code": total_referrals / total_codes if total_codes > 0 else 0
    }
