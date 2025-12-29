"""
Notification endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..db import get_db
from ..security import get_current_user_id
from ..services.notification_service import NotificationService
from ..models.notification import NotificationResponse

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Get user notifications"""
    service = NotificationService(db)
    return await service.get_user_notifications(user_id, unread_only, limit)


@router.get("/unread-count")
async def get_unread_count(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Get count of unread notifications"""
    service = NotificationService(db)
    count = await service.get_unread_count(user_id)
    return {"count": count}


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Mark notification as read"""
    service = NotificationService(db)
    success = await service.mark_as_read(notification_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"success": True}


@router.post("/mark-all-read")
async def mark_all_read(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Mark all notifications as read"""
    service = NotificationService(db)
    count = await service.mark_all_as_read(user_id)
    return {"marked_read": count}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Delete a notification"""
    service = NotificationService(db)
    success = await service.delete_notification(notification_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"success": True}
