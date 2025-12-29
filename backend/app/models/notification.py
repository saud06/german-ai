"""
Notification model for achievement unlocks and system messages
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(str):
    """Custom ObjectId type for Pydantic v2"""
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class Notification(BaseModel):
    """User notification for achievements, milestones, etc."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    type: str  # "achievement", "level_up", "streak", "milestone", "system"
    title: str
    message: str
    icon: str = "🔔"
    
    # Achievement-specific data
    achievement_code: Optional[str] = None
    achievement_name: Optional[str] = None
    achievement_tier: Optional[str] = None
    xp_reward: Optional[int] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = {}
    
    # Status
    read: bool = False
    read_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # Auto-delete after this date
    
    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True


class NotificationCreate(BaseModel):
    """Request to create a notification"""
    user_id: str
    type: str
    title: str
    message: str
    icon: str = "🔔"
    achievement_code: Optional[str] = None
    achievement_name: Optional[str] = None
    achievement_tier: Optional[str] = None
    xp_reward: Optional[int] = None
    metadata: Dict[str, Any] = {}


class NotificationResponse(BaseModel):
    """Notification response"""
    id: str
    type: str
    title: str
    message: str
    icon: str
    achievement_code: Optional[str] = None
    achievement_name: Optional[str] = None
    achievement_tier: Optional[str] = None
    xp_reward: Optional[int] = None
    metadata: Dict[str, Any]
    read: bool
    created_at: datetime
