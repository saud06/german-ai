"""
Conversation state model for tracking scenario progress
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
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


class Message(BaseModel):
    """Single message in conversation"""
    role: str  # "user" or "character"
    content: str  # Message text
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    audio_url: Optional[str] = None  # For voice messages


class ObjectiveProgress(BaseModel):
    """Progress on a specific objective"""
    objective_id: str
    completed: bool = False
    completed_at: Optional[datetime] = None
    attempts: int = 0


class Checkpoint(BaseModel):
    """Checkpoint for save/resume functionality"""
    checkpoint_id: str
    step: int
    score: int
    objectives_completed: List[str] = []
    messages_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}


class ConversationState(BaseModel):
    """State of an ongoing scenario conversation"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    
    # References
    user_id: str
    scenario_id: str
    character_id: str
    
    # Progress
    current_step: int = 0
    objectives_progress: List[ObjectiveProgress] = []
    
    # Conversation history
    messages: List[Message] = []
    
    # Scoring
    score: int = 0
    max_score: int = 100
    
    # Feedback
    grammar_corrections: List[str] = []
    vocabulary_learned: List[str] = []
    
    # Status
    status: str = "active"  # "active", "completed", "abandoned", "paused"
    
    # Checkpoints
    checkpoints: List[Checkpoint] = []
    last_checkpoint_id: Optional[str] = None
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    paused_at: Optional[datetime] = None
    
    # Metadata
    total_messages: int = 0
    total_duration_seconds: int = 0

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ConversationStateResponse(BaseModel):
    """Response for conversation state"""
    state: ConversationState
    scenario_name: str
    character_name: str
    objectives_completed: int
    objectives_total: int
    completion_percentage: float


class ConversationMessageRequest(BaseModel):
    """Request to send a message in scenario conversation"""
    message: str
    audio_base64: Optional[str] = None  # For voice input


class ConversationMessageResponse(BaseModel):
    """Response from scenario conversation"""
    character_message: str
    character_audio: Optional[str] = None  # Base64 audio
    objectives_updated: List[str] = []  # IDs of objectives that were completed
    grammar_feedback: Optional[str] = None
    score_change: int = 0
    conversation_complete: bool = False
