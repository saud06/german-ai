"""
GDPR Compliance Router
Data export, deletion, and privacy management
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional
from datetime import datetime
from ..db import get_db
from ..routers.auth import get_current_user
import json
import zipfile
import io
from pydantic import BaseModel

router = APIRouter(prefix="/gdpr", tags=["GDPR Compliance"])


class DataExportRequest(BaseModel):
    """Request for data export"""
    include_scenarios: bool = True
    include_achievements: bool = True
    include_vocabulary: bool = True
    include_reviews: bool = True
    include_conversations: bool = True


class DataDeletionRequest(BaseModel):
    """Request for data deletion"""
    confirm: bool
    reason: Optional[str] = None


class ConsentUpdate(BaseModel):
    """Update consent preferences"""
    analytics: bool
    marketing: bool
    third_party: bool


# Data Export

@router.post("/export")
async def request_data_export(
    export_request: DataExportRequest,
    user_id: str = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
    db=Depends(get_db)
):
    """Request export of all user data (GDPR Article 15)"""
    # Create export request record
    export_record = {
        "user_id": user_id,
        "status": "pending",
        "requested_at": datetime.utcnow(),
        "include_scenarios": export_request.include_scenarios,
        "include_achievements": export_request.include_achievements,
        "include_vocabulary": export_request.include_vocabulary,
        "include_reviews": export_request.include_reviews,
        "include_conversations": export_request.include_conversations
    }
    
    result = await db["data_export_requests"].insert_one(export_record)
    export_id = str(result.inserted_id)
    
    # Queue export job in background
    if background_tasks:
        background_tasks.add_task(
            generate_data_export,
            export_id,
            user_id,
            export_request,
            db
        )
    
    return {
        "export_id": export_id,
        "status": "pending",
        "message": "Data export requested. You will be notified when it's ready.",
        "estimated_time": "5-10 minutes"
    }


async def generate_data_export(
    export_id: str,
    user_id: str,
    export_request: DataExportRequest,
    db
):
    """Generate data export file"""
    try:
        # Update status
        await db["data_export_requests"].update_one(
            {"_id": export_id},
            {"$set": {"status": "processing", "started_at": datetime.utcnow()}}
        )
        
        export_data = {}
        
        # User profile
        user = await db["users"].find_one({"_id": user_id})
        if user:
            user["_id"] = str(user["_id"])
            export_data["profile"] = user
        
        # User stats
        stats = await db["user_stats"].find_one({"user_id": user_id})
        if stats:
            stats["_id"] = str(stats["_id"])
            export_data["statistics"] = stats
        
        # Scenarios
        if export_request.include_scenarios:
            scenarios = await db["conversation_states"].find({
                "user_id": user_id
            }).to_list(length=10000)
            for s in scenarios:
                s["_id"] = str(s["_id"])
            export_data["scenarios"] = scenarios
        
        # Achievements
        if export_request.include_achievements:
            achievements = await db["user_achievements"].find({
                "user_id": user_id
            }).to_list(length=1000)
            for a in achievements:
                a["_id"] = str(a["_id"])
            export_data["achievements"] = achievements
        
        # Vocabulary
        if export_request.include_vocabulary:
            vocab_progress = await db["vocabulary_progress"].find({
                "user_id": user_id
            }).to_list(length=10000)
            for v in vocab_progress:
                v["_id"] = str(v["_id"])
            export_data["vocabulary_progress"] = vocab_progress
        
        # Reviews
        if export_request.include_reviews:
            reviews = await db["review_cards"].find({
                "user_id": user_id
            }).to_list(length=10000)
            for r in reviews:
                r["_id"] = str(r["_id"])
            export_data["review_cards"] = reviews
        
        # Conversations
        if export_request.include_conversations:
            conversations = await db["conversations"].find({
                "user_id": user_id
            }).to_list(length=10000)
            for c in conversations:
                c["_id"] = str(c["_id"])
            export_data["conversations"] = conversations
        
        # Save export data
        export_json = json.dumps(export_data, indent=2, default=str)
        
        # Store in database (in production, store in S3 or similar)
        await db["data_export_requests"].update_one(
            {"_id": export_id},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.utcnow(),
                    "data": export_json,
                    "size_bytes": len(export_json)
                }
            }
        )
        
        # TODO: Send email notification
        
    except Exception as e:
        # Update status to failed
        await db["data_export_requests"].update_one(
            {"_id": export_id},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e),
                    "failed_at": datetime.utcnow()
                }
            }
        )


@router.get("/export/{export_id}")
async def get_export_status(
    export_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get status of data export request"""
    export_record = await db["data_export_requests"].find_one({
        "_id": export_id,
        "user_id": user_id
    })
    
    if not export_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export request not found"
        )
    
    export_record["_id"] = str(export_record["_id"])
    export_record.pop("data", None)  # Don't include data in status response
    
    return export_record


@router.get("/export/{export_id}/download")
async def download_export(
    export_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Download exported data"""
    export_record = await db["data_export_requests"].find_one({
        "_id": export_id,
        "user_id": user_id
    })
    
    if not export_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export request not found"
        )
    
    if export_record.get("status") != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Export not ready yet"
        )
    
    return {
        "data": export_record.get("data"),
        "format": "json",
        "size_bytes": export_record.get("size_bytes")
    }


# Data Deletion (Right to be Forgotten)

@router.post("/delete-account")
async def request_account_deletion(
    deletion_request: DataDeletionRequest,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Request account and data deletion (GDPR Article 17)"""
    if not deletion_request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation required for account deletion"
        )
    
    # Create deletion request
    deletion_record = {
        "user_id": user_id,
        "status": "pending",
        "requested_at": datetime.utcnow(),
        "reason": deletion_request.reason,
        "scheduled_deletion": datetime.utcnow()  # Immediate in this case
    }
    
    result = await db["data_deletion_requests"].insert_one(deletion_record)
    
    return {
        "deletion_id": str(result.inserted_id),
        "status": "pending",
        "message": "Account deletion requested. Your data will be permanently deleted.",
        "grace_period_days": 0  # No grace period in this implementation
    }


@router.post("/delete-account/{deletion_id}/cancel")
async def cancel_account_deletion(
    deletion_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Cancel pending account deletion"""
    result = await db["data_deletion_requests"].update_one(
        {
            "_id": deletion_id,
            "user_id": user_id,
            "status": "pending"
        },
        {
            "$set": {
                "status": "cancelled",
                "cancelled_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deletion request not found or already processed"
        )
    
    return {"message": "Account deletion cancelled"}


async def execute_account_deletion(user_id: str, db):
    """Execute account deletion (called by background job)"""
    # Delete user data from all collections
    collections_to_clean = [
        "users",
        "user_stats",
        "conversation_states",
        "user_achievements",
        "vocabulary_progress",
        "review_cards",
        "conversations",
        "quiz_attempts",
        "writing_submissions",
        "reading_submissions",
        "grammar_exercise_attempts",
        "organization_members"
    ]
    
    for collection in collections_to_clean:
        await db[collection].delete_many({"user_id": user_id})
    
    # Mark deletion as completed
    await db["data_deletion_requests"].update_one(
        {"user_id": user_id, "status": "pending"},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.utcnow()
            }
        }
    )


# Consent Management

@router.get("/consent")
async def get_consent_preferences(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user's consent preferences"""
    consent = await db["user_consents"].find_one({"user_id": user_id})
    
    if not consent:
        # Default consents
        consent = {
            "user_id": user_id,
            "analytics": True,
            "marketing": False,
            "third_party": False,
            "created_at": datetime.utcnow()
        }
        await db["user_consents"].insert_one(consent)
    
    consent["_id"] = str(consent["_id"])
    return consent


@router.patch("/consent")
async def update_consent_preferences(
    consent_update: ConsentUpdate,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Update user's consent preferences"""
    result = await db["user_consents"].update_one(
        {"user_id": user_id},
        {
            "$set": {
                "analytics": consent_update.analytics,
                "marketing": consent_update.marketing,
                "third_party": consent_update.third_party,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    # Log consent change
    await db["audit_logs"].insert_one({
        "user_id": user_id,
        "action": "update",
        "resource_type": "consent",
        "resource_id": user_id,
        "ip_address": "0.0.0.0",
        "user_agent": "API",
        "metadata": consent_update.dict(),
        "created_at": datetime.utcnow()
    })
    
    return {"message": "Consent preferences updated successfully"}


# Data Portability

@router.get("/data-portability")
async def get_portable_data(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user data in portable format (GDPR Article 20)"""
    # Get essential user data in machine-readable format
    user = await db["users"].find_one({"_id": user_id})
    stats = await db["user_stats"].find_one({"user_id": user_id})
    
    portable_data = {
        "format": "json",
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "user": {
            "id": str(user["_id"]) if user else None,
            "name": user.get("name") if user else None,
            "email": user.get("email") if user else None,
            "created_at": user.get("created_at").isoformat() if user and user.get("created_at") else None
        },
        "statistics": {
            "total_xp": stats.get("total_xp", 0) if stats else 0,
            "current_level": stats.get("current_level", 1) if stats else 1,
            "scenarios_completed": stats.get("scenarios_completed", 0) if stats else 0,
            "words_learned": stats.get("words_learned", 0) if stats else 0,
            "current_streak": stats.get("current_streak", 0) if stats else 0
        }
    }
    
    return portable_data


# Privacy Policy

@router.get("/privacy-policy")
async def get_privacy_policy():
    """Get current privacy policy"""
    return {
        "version": "1.0",
        "effective_date": "2025-01-01",
        "last_updated": "2025-01-01",
        "url": "https://german-ai.com/privacy",
        "summary": "We collect and process your data to provide German learning services. You have the right to access, export, and delete your data at any time."
    }
