from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class JourneyType(str, Enum):
    STUDENT = "student"
    TRAVELER = "traveler"
    PROFESSIONAL = "professional"
    HOBBY = "hobby"

class LevelSystemType(str, Enum):
    CEFR = "cefr"
    DIFFICULTY = "difficulty"

class JourneyProgress(BaseModel):
    lessons_completed: int = 0
    scenarios_completed: int = 0
    quizzes_completed: int = 0
    total_xp: int = 0
    current_streak: int = 0
    milestones: List[Dict[str, Any]] = []

class UserJourney(BaseModel):
    id: str
    type: JourneyType
    is_primary: bool = False
    level: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    progress: JourneyProgress = Field(default_factory=JourneyProgress)

class LearningJourneys(BaseModel):
    active_journey_id: Optional[str] = None
    journeys: List[UserJourney] = []
    onboarding_completed: bool = False
    onboarding_completed_at: Optional[datetime] = None

class JourneyContentMapping(BaseModel):
    content_type: str
    content_id: str
    purposes: List[JourneyType]
    priority_by_purpose: Dict[str, int]
    level_tags: List[str] = []
    topic_tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DashboardSection(BaseModel):
    id: str
    title: str
    description: str
    content_types: List[str]
    order: int

class LevelSystem(BaseModel):
    type: LevelSystemType
    levels: List[str]

class DashboardConfig(BaseModel):
    hero_title: str
    hero_subtitle: str
    primary_cta: str
    sections: List[DashboardSection]

class JourneyMilestone(BaseModel):
    id: str
    title: str
    description: str
    criteria: Dict[str, Any]

class JourneyConfiguration(BaseModel):
    journey_type: JourneyType
    display_name: str
    description: str
    icon: str
    color: str
    level_system: LevelSystem
    dashboard_config: DashboardConfig
    milestones: List[JourneyMilestone]

class SelectJourneyRequest(BaseModel):
    journey_type: JourneyType
    level: str
    is_primary: bool = False

class SwitchJourneyRequest(BaseModel):
    journey_id: str

class JourneyResponse(BaseModel):
    id: str
    type: JourneyType
    is_primary: bool
    level: str
    created_at: datetime
    last_accessed: datetime
    progress: JourneyProgress
    configuration: Optional[JourneyConfiguration] = None
