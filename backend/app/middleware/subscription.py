"""
Subscription middleware and decorators for access control
"""
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from functools import wraps
from typing import Callable, Optional
from ..db import get_db
from ..security import get_current_user_id, decode_jwt, security_scheme
from ..models.subscription import SubscriptionTier, get_tier_features


async def get_user_subscription_tier(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
) -> SubscriptionTier:
    """Get user's current subscription tier"""
    subscription = await db["subscriptions"].find_one({"user_id": user_id})
    if not subscription:
        return SubscriptionTier.FREE
    return SubscriptionTier(subscription.get("tier", "free"))


async def check_subscription_tier(
    required_tier: SubscriptionTier,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
) -> bool:
    """Check if user has required subscription tier"""
    subscription = await db["subscriptions"].find_one({"user_id": user_id})
    if not subscription:
        current_tier = SubscriptionTier.FREE
    else:
        current_tier = SubscriptionTier(subscription.get("tier", "free"))
    
    # Tier hierarchy: FREE < PREMIUM < PLUS < ENTERPRISE
    tier_levels = {
        SubscriptionTier.FREE: 0,
        SubscriptionTier.PREMIUM: 1,
        SubscriptionTier.PLUS: 2,
        SubscriptionTier.ENTERPRISE: 3
    }
    
    return tier_levels.get(current_tier, 0) >= tier_levels.get(required_tier, 0)


async def require_premium(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Require Premium tier or higher"""
    has_access = await check_subscription_tier(SubscriptionTier.PREMIUM, user_id, db)
    if not has_access:
        raise HTTPException(
            status_code=403,
            detail="This feature requires a Premium subscription or higher"
        )
    return user_id


async def require_plus(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Require Plus tier or higher"""
    has_access = await check_subscription_tier(SubscriptionTier.PLUS, user_id, db)
    if not has_access:
        raise HTTPException(
            status_code=403,
            detail="This feature requires a Plus subscription or higher"
        )
    return user_id


async def require_enterprise(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Require Enterprise tier"""
    has_access = await check_subscription_tier(SubscriptionTier.ENTERPRISE, user_id, db)
    if not has_access:
        raise HTTPException(
            status_code=403,
            detail="This feature requires an Enterprise subscription"
        )
    return user_id


async def check_ai_usage_limit(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
) -> bool:
    """Check if user can use AI features (within daily limit)"""
    from datetime import datetime
    
    # Get subscription tier
    subscription = await db["subscriptions"].find_one({"user_id": user_id})
    if not subscription:
        tier = SubscriptionTier.FREE
    else:
        tier = SubscriptionTier(subscription.get("tier", "free"))
    
    features = get_tier_features(tier)
    
    # Unlimited for premium tiers
    if features.ai_minutes_per_day is None:
        return True
    
    # Check daily usage
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    usage = await db["usage_tracking"].find_one({
        "user_id": user_id,
        "date": today
    })
    
    if not usage:
        return True
    
    ai_minutes_used = usage.get("ai_minutes_used", 0)
    return ai_minutes_used < features.ai_minutes_per_day


async def check_scenario_limit(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
) -> bool:
    """Check if user can start a new scenario (within daily limit)"""
    from datetime import datetime
    
    # Get subscription tier
    subscription = await db["subscriptions"].find_one({"user_id": user_id})
    if not subscription:
        tier = SubscriptionTier.FREE
    else:
        tier = SubscriptionTier(subscription.get("tier", "free"))
    
    features = get_tier_features(tier)
    
    # Unlimited for premium tiers
    if features.scenarios_per_day is None:
        return True
    
    # Check today's usage
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    usage_record = await db["usage_tracking"].find_one({
        "user_id": user_id,
        "date": today
    })
    
    if not usage_record:
        return True  # No usage today yet
    
    scenarios_today = usage_record.get("scenarios_completed", 0)
    return scenarios_today < features.scenarios_per_day


async def require_ai_access(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Require AI access (check usage limits)"""
    # Check if user is admin - admins have unlimited access
    user = await db["users"].find_one({"_id": user_id})
    if user and user.get("role") == "admin":
        return user_id
    
    can_use = await check_ai_usage_limit(user_id, db)
    if not can_use:
        raise HTTPException(
            status_code=429,
            detail="Daily AI usage limit reached. Upgrade to Premium for unlimited access."
        )
    return user_id


async def require_scenario_access(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db = Depends(get_db)
):
    """Require scenario access (check usage limits)"""
    # Decode token to get role
    token = credentials.credentials
    payload = decode_jwt(token)
    user_id = payload["sub"]
    user_role = payload.get("role", "user")
    
    # Check if user is admin - admins have unlimited access
    if user_role == "admin":
        return user_id
    
    can_use = await check_scenario_limit(user_id, db)
    if not can_use:
        raise HTTPException(
            status_code=429,
            detail="Daily scenario limit reached. Upgrade to Premium for unlimited access."
        )
    return user_id


async def track_ai_usage_minutes(
    user_id: str,
    minutes: int,
    db
):
    """Track AI usage minutes"""
    from datetime import datetime
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    await db["usage_tracking"].update_one(
        {"user_id": user_id, "date": today},
        {
            "$inc": {"ai_minutes_used": minutes},
            "$set": {"last_reset": datetime.utcnow()}
        },
        upsert=True
    )


async def track_scenario_usage(
    user_id: str,
    db
):
    """Track scenario completion"""
    from datetime import datetime
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    await db["usage_tracking"].update_one(
        {"user_id": user_id, "date": today},
        {
            "$inc": {"scenarios_completed": 1},
            "$set": {"last_reset": datetime.utcnow()}
        },
        upsert=True
    )
