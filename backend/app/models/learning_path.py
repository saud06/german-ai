"""
Learning Path Models - Story-driven interactive learning system
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ], serialization=core_schema.plain_serializer_function_ser_schema(str))

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


class CompletionReward(BaseModel):
    """Rewards for completing a chapter/location/scenario"""
    xp: int
    badge: Optional[str] = None
    unlock: Optional[str] = None
    housing_upgrade: Optional[str] = None
    career_upgrade: Optional[str] = None
    relationship_boost: Optional[Dict[str, int]] = None


class UnlockRequirements(BaseModel):
    """Requirements to unlock content"""
    chapter_progress: int = 0  # Percentage (0-100)
    previous_location: Optional[str] = None
    min_xp: int = 0
    min_level: int = 0
    required_scenarios: List[str] = []
    relationship_level: Optional[Dict[str, int]] = None  # {"emma": 3}


class MapPosition(BaseModel):
    """Position on the interactive map"""
    x: int
    y: int


class LearningPath(BaseModel):
    """A chapter in the learning journey (e.g., Chapter 1: The Arrival)"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    chapter: int  # 1-6
    level: str  # A1, A2, B1, B2, C1, C2
    title: str
    description: str
    story: str  # Narrative introduction
    image: str  # Chapter cover image
    locations: List[str] = []  # Location IDs
    characters: List[str] = []  # Character IDs
    estimated_hours: float
    unlock_requirements: Optional[UnlockRequirements] = None
    completion_reward: CompletionReward
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Location(BaseModel):
    """A location in a chapter (e.g., Hotel, Café, Supermarket)"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    chapter_id: str
    name: str
    type: str  # scenario, practice, quiz, review
    description: str
    image: str
    position: MapPosition  # Position on map
    scenarios: List[str] = []  # Scenario IDs
    unlock_requirements: UnlockRequirements
    characters: List[str] = []  # Character IDs appearing here
    estimated_minutes: int
    rewards: Optional[CompletionReward] = Field(alias="completion_reward", default=None)
    difficulty_requirements: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ConversationTopic(BaseModel):
    """Topics available at different relationship levels"""
    level: int  # Relationship level required
    topics: List[str]


class Character(BaseModel):
    """An AI character in the learning journey"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    role: str  # Neighbor, Waiter, Boss, etc.
    personality: str  # Friendly, strict, funny, etc.
    age: int
    occupation: str
    avatar: str  # Image URL
    voice_id: str  # Piper voice ID
    appears_in_chapters: List[int]
    relationship_levels: Dict[str, str]  # {0: "Stranger", 3: "Acquaintance", ...}
    conversation_topics: Dict[str, List[str]]  # {0: ["greetings"], 3: ["hobbies"], ...}
    ai_prompt: str  # System prompt for AI conversations
    backstory: str  # Character background
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CharacterRelationship(BaseModel):
    """User's relationship with a character"""
    character_id: str
    level: int = 0  # 0-10
    conversations: int = 0
    last_interaction: Optional[datetime] = None
    unlocked_topics: List[str] = []
    memorable_moments: List[str] = []  # Key conversation highlights


class LifeStats(BaseModel):
    """User's virtual life progression"""
    housing: str = "hotel"  # hotel, shared_flat, apartment, house
    job: str = "unemployed"  # unemployed, intern, employee, manager, director
    friends: int = 0
    cities_visited: int = 1
    certifications: List[str] = []


class LearningProfile(BaseModel):
    """User's learning preferences and style"""
    style: str = "balanced"  # visual, auditory, kinesthetic, balanced
    pace: str = "medium"  # slow, medium, fast
    strengths: List[str] = []
    weaknesses: List[str] = []
    interests: List[str] = []
    goals: List[str] = []
    preferred_time: str = "anytime"
    session_length: int = 20  # minutes


class ChapterProgress(BaseModel):
    """Progress in a specific chapter"""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percent: int = 0
    locations_completed: List[str] = []
    scenarios_completed: List[str] = []
    xp_earned: int = 0
    time_spent_minutes: int = 0


class UserProgress(BaseModel):
    """User's overall learning journey progress"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    current_chapter: int = 1
    current_location: Optional[str] = None
    chapter_progress: Dict[str, ChapterProgress] = {}  # {chapter_id: progress}
    character_relationships: Dict[str, CharacterRelationship] = {}  # {character_id: relationship}
    life_stats: LifeStats = Field(default_factory=LifeStats)
    learning_profile: LearningProfile = Field(default_factory=LearningProfile)
    total_xp: int = 0
    level: int = 1
    achievements: List[str] = []
    daily_streak: int = 0
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# API Response Models

class LearningPathResponse(BaseModel):
    """Response for learning path details"""
    path: LearningPath
    progress: Optional[ChapterProgress] = None
    is_unlocked: bool
    is_completed: bool


class LocationResponse(BaseModel):
    """Response for location details"""
    location: Location
    is_unlocked: bool
    is_completed: bool
    completion_percent: int


class CharacterResponse(BaseModel):
    """Response for character details"""
    character: Character
    relationship: Optional[CharacterRelationship] = None
    available_topics: List[str]


class ProgressSummary(BaseModel):
    """Summary of user's progress"""
    current_chapter: int
    current_location: Optional[str]
    total_xp: int
    level: int
    chapters_completed: int
    scenarios_completed: int
    words_learned: int
    conversations_held: int
    daily_streak: int
    life_stats: LifeStats
    next_milestone: Optional[str]


class RecommendedAction(BaseModel):
    """AI-recommended next action"""
    type: str  # scenario, practice, review, challenge
    id: Optional[str] = None  # ID of the recommended item
    title: str
    description: str
    estimated_minutes: int
    xp_reward: int
    priority: str  # high, medium, low
    reason: str  # Why this is recommended


class DailyChallenge(BaseModel):
    """Daily challenge for user"""
    id: str
    title: str
    description: str
    type: str  # conversation, vocabulary, grammar, pronunciation
    target: int
    progress: int
    xp_reward: int
    expires_at: datetime
