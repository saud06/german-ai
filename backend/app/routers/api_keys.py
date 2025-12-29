"""
API Key Management Router
Secure API key generation and management for organizations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import List, Optional
from datetime import datetime, timedelta
from ..db import get_db
from ..routers.auth import get_current_user
from ..models.organization import APIKey, APIKeyCreate
import secrets
import hashlib
from pydantic import BaseModel

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


def generate_api_key() -> tuple[str, str, str]:
    """Generate a secure API key with prefix, full key, and hash"""
    # Generate random key
    random_part = secrets.token_urlsafe(32)
    
    # Create key with prefix
    prefix = "sk_live_"
    full_key = f"{prefix}{random_part}"
    
    # Hash the key for storage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    
    # Get display prefix (first 12 chars)
    key_prefix = full_key[:12]
    
    return full_key, key_hash, key_prefix


async def verify_api_key(api_key: str, db) -> Optional[dict]:
    """Verify API key and return organization info"""
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    api_key_doc = await db["api_keys"].find_one({
        "key_hash": key_hash,
        "active": True
    })
    
    if not api_key_doc:
        return None
    
    # Check expiration
    if api_key_doc.get("expires_at") and api_key_doc["expires_at"] < datetime.utcnow():
        return None
    
    # Update last used
    await db["api_keys"].update_one(
        {"_id": api_key_doc["_id"]},
        {
            "$set": {"last_used_at": datetime.utcnow()},
            "$inc": {"total_requests": 1}
        }
    )
    
    return api_key_doc


async def check_rate_limit(organization_id: str, api_key_id: str, db) -> bool:
    """Check if API key has exceeded rate limit"""
    # Get API key rate limit
    api_key = await db["api_keys"].find_one({"_id": api_key_id})
    if not api_key:
        return False
    
    rate_limit = api_key.get("rate_limit", 100)
    
    # Count requests in last hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    request_count = await db["api_usage"].count_documents({
        "organization_id": organization_id,
        "api_key_id": api_key_id,
        "created_at": {"$gte": one_hour_ago}
    })
    
    return request_count < rate_limit


async def log_api_usage(organization_id: str, api_key_id: str, endpoint: str, db):
    """Log API usage for analytics and rate limiting"""
    await db["api_usage"].insert_one({
        "organization_id": organization_id,
        "api_key_id": api_key_id,
        "endpoint": endpoint,
        "created_at": datetime.utcnow()
    })


# Dependency for API key authentication
async def get_api_key_auth(
    x_api_key: Optional[str] = Header(None),
    db=Depends(get_db)
) -> dict:
    """Authenticate request using API key"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    api_key_info = await verify_api_key(x_api_key, db)
    if not api_key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
    
    # Check rate limit
    rate_ok = await check_rate_limit(
        api_key_info["organization_id"],
        str(api_key_info["_id"]),
        db
    )
    
    if not rate_ok:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return api_key_info


# API Key CRUD

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Create a new API key for organization"""
    # Check admin access
    member = await db["organization_members"].find_one({
        "organization_id": organization_id,
        "user_id": user_id
    })
    
    if not member or member.get("role") not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check organization limits
    org = await db["organizations"].find_one({"_id": organization_id})
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Count existing API keys
    key_count = await db["api_keys"].count_documents({
        "organization_id": organization_id,
        "active": True
    })
    
    max_keys = org.get("limits", {}).get("max_api_keys", 5)
    if key_count >= max_keys:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum API keys limit reached ({max_keys})"
        )
    
    # Generate API key
    full_key, key_hash, key_prefix = generate_api_key()
    
    # Calculate expiration
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
    
    # Create API key document
    api_key = APIKey(
        organization_id=organization_id,
        name=key_data.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        permissions=key_data.permissions,
        rate_limit=key_data.rate_limit,
        created_by=user_id,
        expires_at=expires_at
    )
    
    result = await db["api_keys"].insert_one(
        api_key.dict(by_alias=True, exclude={"id"})
    )
    
    # Log audit event
    await db["audit_logs"].insert_one({
        "organization_id": organization_id,
        "user_id": user_id,
        "action": "create",
        "resource_type": "api_key",
        "resource_id": str(result.inserted_id),
        "ip_address": "0.0.0.0",
        "user_agent": "API",
        "metadata": {"name": key_data.name},
        "created_at": datetime.utcnow()
    })
    
    return {
        "id": str(result.inserted_id),
        "api_key": full_key,  # Only returned once!
        "key_prefix": key_prefix,
        "message": "API key created successfully. Save this key securely - it won't be shown again!"
    }


@router.get("/")
async def list_api_keys(
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """List organization's API keys"""
    # Check member access
    member = await db["organization_members"].find_one({
        "organization_id": organization_id,
        "user_id": user_id
    })
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get API keys
    keys = await db["api_keys"].find({
        "organization_id": organization_id
    }).to_list(length=100)
    
    # Remove sensitive data
    safe_keys = []
    for key in keys:
        key["_id"] = str(key["_id"])
        key.pop("key_hash", None)
        safe_keys.append(key)
    
    return {"api_keys": safe_keys, "total": len(safe_keys)}


@router.get("/{key_id}")
async def get_api_key(
    key_id: str,
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get API key details"""
    # Check access
    member = await db["organization_members"].find_one({
        "organization_id": organization_id,
        "user_id": user_id
    })
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get API key
    key = await db["api_keys"].find_one({
        "_id": key_id,
        "organization_id": organization_id
    })
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    key["_id"] = str(key["_id"])
    key.pop("key_hash", None)
    
    return key


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: str,
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Delete (deactivate) an API key"""
    # Check admin access
    member = await db["organization_members"].find_one({
        "organization_id": organization_id,
        "user_id": user_id
    })
    
    if not member or member.get("role") not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Deactivate API key
    result = await db["api_keys"].update_one(
        {"_id": key_id, "organization_id": organization_id},
        {"$set": {"active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Log audit event
    await db["audit_logs"].insert_one({
        "organization_id": organization_id,
        "user_id": user_id,
        "action": "delete",
        "resource_type": "api_key",
        "resource_id": key_id,
        "ip_address": "0.0.0.0",
        "user_agent": "API",
        "metadata": {},
        "created_at": datetime.utcnow()
    })
    
    return {"message": "API key deleted successfully"}


@router.get("/{key_id}/usage")
async def get_api_key_usage(
    key_id: str,
    organization_id: str,
    days: int = 7,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get API key usage statistics"""
    # Check access
    member = await db["organization_members"].find_one({
        "organization_id": organization_id,
        "user_id": user_id
    })
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get usage data
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {
            "$match": {
                "organization_id": organization_id,
                "api_key_id": key_id,
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
                "requests": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    usage_by_day = await db["api_usage"].aggregate(pipeline).to_list(length=days)
    
    # Get total requests
    total_requests = await db["api_usage"].count_documents({
        "organization_id": organization_id,
        "api_key_id": key_id,
        "created_at": {"$gte": start_date}
    })
    
    return {
        "key_id": key_id,
        "period_days": days,
        "total_requests": total_requests,
        "usage_by_day": usage_by_day
    }
