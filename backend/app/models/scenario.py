"""
Scenario model for Life Simulation feature
Represents real-world conversation scenarios for German practice
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
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


class PersonalityTrait(BaseModel):
    """Character personality traits"""
    friendliness: int = 5  # 1-10 scale
    formality: int = 5  # 1-10 scale
    patience: int = 5  # 1-10 scale
    helpfulness: int = 5  # 1-10 scale
    chattiness: int = 5  # 1-10 scale


class Emotion(BaseModel):
    """Character emotional state"""
    current: str = "neutral"  # happy, sad, angry, frustrated, pleased, neutral, etc.
    intensity: int = 5  # 1-10
    triggers: Dict[str, str] = {}  # What causes emotion changes


class Character(BaseModel):
    """Character in a scenario with personality and emotions"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str  # e.g., "Kellner Hans"
    role: str  # e.g., "waiter", "receptionist", "shop_assistant"
    personality: str  # e.g., "friendly", "formal", "impatient", "helpful"
    personality_traits: PersonalityTrait = Field(default_factory=PersonalityTrait)
    emotion: Emotion = Field(default_factory=Emotion)
    voice_id: Optional[str] = None  # Piper voice ID (uses PIPER_VOICE from config if not set)
    description: str  # Background info about the character
    greeting: str  # Initial greeting in German
    
    # Memory system
    remembers_user: bool = False  # Can remember past interactions
    memory: Dict[str, Any] = {}  # Stored memories

    class Config:
        json_encoders = {ObjectId: str}


class DialogueBranch(BaseModel):
    """Branching dialogue path"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    trigger: str  # What triggers this branch (keyword, phrase, action)
    condition: Optional[str] = None  # Additional condition (e.g., "objective_1_complete")
    response: str  # Character's response
    next_branches: List[str] = []  # IDs of possible next branches
    consequences: Dict[str, Any] = {}  # Effects (e.g., {"emotion": "pleased", "objective_1": "complete"})


class DecisionPoint(BaseModel):
    """Decision point in scenario"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    description: str  # What decision needs to be made
    options: List[Dict[str, str]]  # [{"text": "Option 1", "consequence": "branch_1"}]
    time_limit: Optional[int] = None  # Seconds to decide (optional)


class Objective(BaseModel):
    """Learning objective within a scenario"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    description: str  # e.g., "Order a drink"
    keywords: Optional[List[str]] = []  # Keywords that indicate completion
    required: bool = True  # Whether this objective is required
    hint: Optional[str] = None  # Hint in German
    completed: bool = False
    xp_reward: int = 50  # XP for completing this objective
    difficulty_level: int = 1  # 1-5 difficulty

    class Config:
        json_encoders = {ObjectId: str}


class Scenario(BaseModel):
    """Life simulation scenario with branching paths"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str  # e.g., "Im Restaurant"
    title_en: Optional[str] = None  # English title for reference
    description: str  # German description
    description_en: Optional[str] = None  # English description
    difficulty: str  # "beginner", "intermediate", "advanced"
    category: str  # "restaurant", "hotel", "shopping", "doctor", "transport"
    estimated_duration: int  # minutes
    
    # Characters in this scenario (can be IDs or populated Character objects)
    characters: List[Character] = []  # Character objects
    
    # Learning objectives
    objectives: List[Objective] = []
    
    # Branching dialogue system
    dialogue_branches: List[DialogueBranch] = []
    decision_points: List[DecisionPoint] = []
    
    # Context for AI
    context: Optional[str] = None  # Detailed context for AI to understand the scenario
    system_prompt: Optional[str] = None  # System prompt for AI character
    
    # Scenario flow control
    has_time_limit: bool = False
    time_limit_minutes: Optional[int] = None
    has_checkpoints: bool = False
    checkpoints: List[str] = []  # Checkpoint IDs for save/resume
    
    # Rewards
    xp_reward: int = 100  # Base XP for completion
    bonus_xp: int = 50  # Bonus for perfect completion
    max_score: Optional[int] = 100  # Maximum score achievable
    
    # Metadata
    icon: str = "🎭"  # Emoji icon
    tags: List[str] = []
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Stats
    total_completions: int = 0
    total_attempts: int = 0
    average_rating: float = 0.0
    average_completion_time: int = 0  # minutes

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ScenarioListResponse(BaseModel):
    """Response for scenario list"""
    scenarios: List[Scenario]
    total: int


class ScenarioDetailResponse(BaseModel):
    """Response for scenario detail"""
    scenario: Scenario
    user_progress: Optional[Dict[str, Any]] = None
