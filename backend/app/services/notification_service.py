"""
Notification service for managing user notifications
"""
from datetime import datetime, timedelta
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models.notification import Notification, NotificationCreate, NotificationResponse
from bson import ObjectId


class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.notifications
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        icon: str = "🔔",
        achievement_code: Optional[str] = None,
        achievement_name: Optional[str] = None,
        achievement_tier: Optional[str] = None,
        xp_reward: Optional[int] = None,
        metadata: dict = None,
        expires_in_days: int = 30
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            icon=icon,
            achievement_code=achievement_code,
            achievement_name=achievement_name,
            achievement_tier=achievement_tier,
            xp_reward=xp_reward,
            metadata=metadata or {},
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days)
        )
        
        result = await self.collection.insert_one(
            notification.model_dump(by_alias=True, exclude={"id"})
        )
        notification.id = str(result.inserted_id)
        
        return notification
    
    async def create_achievement_notification(
        self,
        user_id: str,
        achievement_code: str,
        achievement_name: str,
        achievement_tier: str,
        xp_reward: int,
        icon: str = "🏆"
    ) -> Notification:
        """Create achievement unlock notification"""
        tier_emoji = {
            "bronze": "🥉",
            "silver": "🥈",
            "gold": "🥇",
            "platinum": "💎",
            "diamond": "👑"
        }
        
        tier_icon = tier_emoji.get(achievement_tier, "🏆")
        
        return await self.create_notification(
            user_id=user_id,
            notification_type="achievement",
            title=f"Achievement Unlocked! {tier_icon}",
            message=f"You've unlocked '{achievement_name}'! +{xp_reward} XP",
            icon=icon,
            achievement_code=achievement_code,
            achievement_name=achievement_name,
            achievement_tier=achievement_tier,
            xp_reward=xp_reward,
            metadata={"tier": achievement_tier}
        )
    
    async def create_level_up_notification(
        self,
        user_id: str,
        new_level: int,
        xp_reward: int = 0
    ) -> Notification:
        """Create level up notification"""
        return await self.create_notification(
            user_id=user_id,
            notification_type="level_up",
            title=f"Level Up! 🎉",
            message=f"Congratulations! You've reached Level {new_level}!",
            icon="⬆️",
            metadata={"level": new_level},
            xp_reward=xp_reward
        )
    
    async def create_streak_notification(
        self,
        user_id: str,
        streak_days: int
    ) -> Notification:
        """Create streak milestone notification"""
        milestones = {
            7: ("Week Warrior", "🔥"),
            30: ("Month Master", "🔥🔥"),
            100: ("Century Club", "🔥🔥🔥"),
            365: ("Year Legend", "👑")
        }
        
        if streak_days in milestones:
            title_suffix, icon = milestones[streak_days]
            return await self.create_notification(
                user_id=user_id,
                notification_type="streak",
                title=f"{streak_days}-Day Streak! {icon}",
                message=f"Amazing! You've maintained a {streak_days}-day learning streak!",
                icon=icon,
                metadata={"streak_days": streak_days}
            )
        
        return None
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[NotificationResponse]:
        """Get user's notifications"""
        query = {"user_id": user_id}
        
        if unread_only:
            query["read"] = False
        
        cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
        notifications = await cursor.to_list(length=limit)
        
        return [
            NotificationResponse(
                id=str(n["_id"]),
                type=n["type"],
                title=n["title"],
                message=n["message"],
                icon=n["icon"],
                achievement_code=n.get("achievement_code"),
                achievement_name=n.get("achievement_name"),
                achievement_tier=n.get("achievement_tier"),
                xp_reward=n.get("xp_reward"),
                metadata=n.get("metadata", {}),
                read=n["read"],
                created_at=n["created_at"]
            )
            for n in notifications
        ]
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        result = await self.collection.update_one(
            {"_id": ObjectId(notification_id), "user_id": user_id},
            {
                "$set": {
                    "read": True,
                    "read_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all user notifications as read"""
        result = await self.collection.update_many(
            {"user_id": user_id, "read": False},
            {
                "$set": {
                    "read": True,
                    "read_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        return await self.collection.count_documents({
            "user_id": user_id,
            "read": False
        })
    
    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        result = await self.collection.delete_one({
            "_id": ObjectId(notification_id),
            "user_id": user_id
        })
        return result.deleted_count > 0
    
    async def cleanup_expired(self) -> int:
        """Delete expired notifications"""
        result = await self.collection.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        return result.deleted_count
