"""
Webhook Management Router
Webhook configuration and delivery system
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..db import get_db
from ..routers.auth import get_current_user
from ..models.organization import Webhook, WebhookCreate, WebhookDelivery
import secrets
import hashlib
import hmac
import httpx
import asyncio

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


# Webhook event types
WEBHOOK_EVENTS = [
    "user.created",
    "user.updated",
    "user.deleted",
    "scenario.started",
    "scenario.completed",
    "achievement.unlocked",
    "subscription.created",
    "subscription.updated",
    "subscription.cancelled",
    "organization.created",
    "organization.updated",
]


def generate_webhook_secret() -> str:
    """Generate a secure webhook secret"""
    return secrets.token_urlsafe(32)


def generate_webhook_signature(payload: str, secret: str) -> str:
    """Generate HMAC signature for webhook payload"""
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()


async def deliver_webhook(
    webhook_id: str,
    event_type: str,
    payload: Dict[str, Any],
    db
):
    """Deliver webhook with retry logic"""
    # Get webhook configuration
    webhook = await db["webhooks"].find_one({"_id": webhook_id})
    if not webhook or not webhook.get("active"):
        return
    
    # Create delivery record
    delivery = WebhookDelivery(
        webhook_id=webhook_id,
        organization_id=webhook["organization_id"],
        event_type=event_type,
        payload=payload
    )
    
    result = await db["webhook_deliveries"].insert_one(
        delivery.dict(by_alias=True, exclude={"id"})
    )
    delivery_id = str(result.inserted_id)
    
    # Attempt delivery with retries
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            # Generate signature
            payload_str = str(payload)
            signature = generate_webhook_signature(payload_str, webhook["secret"])
            
            # Send webhook
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    webhook["url"],
                    json=payload,
                    headers={
                        "X-Webhook-Signature": signature,
                        "X-Webhook-Event": event_type,
                        "X-Webhook-Delivery": delivery_id,
                        "Content-Type": "application/json"
                    }
                )
            
            # Update delivery record
            await db["webhook_deliveries"].update_one(
                {"_id": delivery_id},
                {
                    "$set": {
                        "status": "delivered" if response.status_code < 400 else "failed",
                        "attempts": attempt,
                        "response_code": response.status_code,
                        "response_body": response.text[:1000],  # Limit size
                        "delivered_at": datetime.utcnow()
                    }
                }
            )
            
            # Update webhook stats
            if response.status_code < 400:
                await db["webhooks"].update_one(
                    {"_id": webhook_id},
                    {
                        "$inc": {
                            "total_deliveries": 1,
                            "successful_deliveries": 1
                        },
                        "$set": {"last_delivery_at": datetime.utcnow()}
                    }
                )
                return  # Success, exit
            else:
                await db["webhooks"].update_one(
                    {"_id": webhook_id},
                    {
                        "$inc": {
                            "total_deliveries": 1,
                            "failed_deliveries": 1
                        }
                    }
                )
        
        except Exception as e:
            # Update delivery record with error
            await db["webhook_deliveries"].update_one(
                {"_id": delivery_id},
                {
                    "$set": {
                        "status": "failed",
                        "attempts": attempt,
                        "error_message": str(e)
                    }
                }
            )
            
            await db["webhooks"].update_one(
                {"_id": webhook_id},
                {
                    "$inc": {
                        "total_deliveries": 1,
                        "failed_deliveries": 1
                    }
                }
            )
        
        # Wait before retry (exponential backoff)
        if attempt < max_attempts:
            await asyncio.sleep(2 ** attempt)


async def trigger_webhook_event(
    organization_id: str,
    event_type: str,
    payload: Dict[str, Any],
    db,
    background_tasks: BackgroundTasks
):
    """Trigger webhook event for organization"""
    # Find webhooks subscribed to this event
    webhooks = await db["webhooks"].find({
        "organization_id": organization_id,
        "active": True,
        "events": event_type
    }).to_list(length=100)
    
    # Deliver to each webhook in background
    for webhook in webhooks:
        background_tasks.add_task(
            deliver_webhook,
            str(webhook["_id"]),
            event_type,
            payload,
            db
        )


# Webhook CRUD

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookCreate,
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Create a new webhook"""
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
    
    # Validate events
    invalid_events = [e for e in webhook_data.events if e not in WEBHOOK_EVENTS]
    if invalid_events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid events: {invalid_events}"
        )
    
    # Check webhook limit
    webhook_count = await db["webhooks"].count_documents({
        "organization_id": organization_id,
        "active": True
    })
    
    org = await db["organizations"].find_one({"_id": organization_id})
    max_webhooks = org.get("limits", {}).get("max_webhooks", 5)
    
    if webhook_count >= max_webhooks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum webhooks limit reached ({max_webhooks})"
        )
    
    # Generate secret
    secret = generate_webhook_secret()
    
    # Create webhook
    webhook = Webhook(
        organization_id=organization_id,
        url=webhook_data.url,
        events=webhook_data.events,
        secret=secret,
        description=webhook_data.description,
        created_by=user_id
    )
    
    result = await db["webhooks"].insert_one(
        webhook.dict(by_alias=True, exclude={"id"})
    )
    
    # Log audit event
    await db["audit_logs"].insert_one({
        "organization_id": organization_id,
        "user_id": user_id,
        "action": "create",
        "resource_type": "webhook",
        "resource_id": str(result.inserted_id),
        "ip_address": "0.0.0.0",
        "user_agent": "API",
        "metadata": {"url": webhook_data.url, "events": webhook_data.events},
        "created_at": datetime.utcnow()
    })
    
    return {
        "id": str(result.inserted_id),
        "secret": secret,
        "message": "Webhook created successfully. Save the secret for signature verification!"
    }


@router.get("/")
async def list_webhooks(
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """List organization's webhooks"""
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
    
    webhooks = await db["webhooks"].find({
        "organization_id": organization_id
    }).to_list(length=100)
    
    # Remove secrets
    for webhook in webhooks:
        webhook["_id"] = str(webhook["_id"])
        webhook["secret"] = "***hidden***"
    
    return {"webhooks": webhooks, "total": len(webhooks)}


@router.get("/{webhook_id}")
async def get_webhook(
    webhook_id: str,
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get webhook details"""
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
    
    webhook = await db["webhooks"].find_one({
        "_id": webhook_id,
        "organization_id": organization_id
    })
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    webhook["_id"] = str(webhook["_id"])
    webhook["secret"] = "***hidden***"
    
    return webhook


@router.patch("/{webhook_id}")
async def update_webhook(
    webhook_id: str,
    organization_id: str,
    active: Optional[bool] = None,
    events: Optional[List[str]] = None,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Update webhook configuration"""
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
    
    # Build update
    update_data = {"updated_at": datetime.utcnow()}
    if active is not None:
        update_data["active"] = active
    if events is not None:
        # Validate events
        invalid_events = [e for e in events if e not in WEBHOOK_EVENTS]
        if invalid_events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid events: {invalid_events}"
            )
        update_data["events"] = events
    
    result = await db["webhooks"].update_one(
        {"_id": webhook_id, "organization_id": organization_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    return {"message": "Webhook updated successfully"}


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    organization_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Delete a webhook"""
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
    
    result = await db["webhooks"].delete_one({
        "_id": webhook_id,
        "organization_id": organization_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    return {"message": "Webhook deleted successfully"}


@router.get("/{webhook_id}/deliveries")
async def get_webhook_deliveries(
    webhook_id: str,
    organization_id: str,
    limit: int = 50,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get webhook delivery history"""
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
    
    deliveries = await db["webhook_deliveries"].find({
        "webhook_id": webhook_id,
        "organization_id": organization_id
    }).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    for delivery in deliveries:
        delivery["_id"] = str(delivery["_id"])
    
    return {"deliveries": deliveries, "total": len(deliveries)}


@router.get("/events/list")
async def list_webhook_events():
    """List available webhook events"""
    return {
        "events": WEBHOOK_EVENTS,
        "total": len(WEBHOOK_EVENTS)
    }


@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    organization_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Send a test webhook"""
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
    
    # Send test webhook
    test_payload = {
        "event": "webhook.test",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "message": "This is a test webhook"
        }
    }
    
    background_tasks.add_task(
        deliver_webhook,
        webhook_id,
        "webhook.test",
        test_payload,
        db
    )
    
    return {"message": "Test webhook queued for delivery"}
