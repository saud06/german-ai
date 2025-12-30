"""
Achievement system for gamification
Tracks user accomplishments and unlocks
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


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


class AchievementCategory(str, Enum):
    """Achievement categories"""
    SCENARIOS = "scenarios"
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"
    QUIZ = "quiz"
    SOCIAL = "social"
    STREAK = "streak"
    SPECIAL = "special"


class AchievementTier(str, Enum):
    """Achievement tiers/rarity"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class UnlockCondition(BaseModel):
    """Condition that must be met to unlock achievement"""
    type: str  # "scenario_complete", "vocab_learned", "quiz_score", "streak_days", etc.
    target: int  # Target value (e.g., 10 scenarios, 100 words, 7 days)
    current: int = 0  # Current progress
    metadata: Dict[str, Any] = {}  # Additional data (e.g., specific scenario_id)


class Achievement(BaseModel):
    """Achievement definition"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    code: str  # Unique code (e.g., "first_scenario", "vocab_master_100")
    name: str  # Display name
    description: str  # What the achievement is for
    icon: str  # Emoji icon
    category: AchievementCategory
    tier: AchievementTier
    
    # Unlock conditions
    conditions: List[UnlockCondition]
    
    # Rewards
    xp_reward: int = 0  # XP points awarded
    badge_image: Optional[str] = None  # URL to badge image
    
    # Metadata
    hidden: bool = False  # Hidden until unlocked
    secret: bool = False  # Secret achievement (not shown in list)
    order: int = 0  # Display order
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserAchievement(BaseModel):
    """User's achievement progress"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    achievement_code: str
    
    # Progress
    unlocked: bool = False
    progress: int = 0  # Current progress (0-100%)
    conditions_met: List[str] = []  # Which conditions are met
    
    # Timestamps
    unlocked_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserStats(BaseModel):
    """User's overall statistics for achievements"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    
    # XP and Levels
    total_xp: int = 0
    level: int = 1
    xp_to_next_level: int = 100
    
    # Streaks
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[datetime] = None
    
    # Scenario stats
    scenarios_completed: int = 0
    scenarios_started: int = 0
    total_scenario_time: int = 0  # minutes
    
    # Vocabulary stats
    words_learned: int = 0
    words_reviewed: int = 0
    
    # Quiz stats
    quizzes_completed: int = 0
    quiz_accuracy: float = 0.0
    perfect_quizzes: int = 0
    
    # Grammar stats
    grammar_checks: int = 0
    grammar_errors_fixed: int = 0
    
    # Social stats
    friends_count: int = 0
    challenges_won: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Achievement definitions
ACHIEVEMENT_DEFINITIONS = [
    # Scenario Achievements
    {
        "code": "first_scenario",
        "name": "Erste Schritte",
        "description": "Complete your first scenario",
        "icon": "🎬",
        "category": "scenarios",
        "tier": "bronze",
        "conditions": [{"type": "scenarios_completed", "target": 1}],
        "xp_reward": 50,
        "order": 1
    },
    {
        "code": "scenario_master_5",
        "name": "Scenario Explorer",
        "description": "Complete 5 different scenarios",
        "icon": "🗺️",
        "category": "scenarios",
        "tier": "silver",
        "conditions": [{"type": "scenarios_completed", "target": 5}],
        "xp_reward": 200,
        "order": 2
    },
    {
        "code": "scenario_master_10",
        "name": "Scenario Champion",
        "description": "Complete all 10 scenarios",
        "icon": "🏆",
        "category": "scenarios",
        "tier": "gold",
        "conditions": [{"type": "scenarios_completed", "target": 10}],
        "xp_reward": 500,
        "order": 3
    },
    {
        "code": "scenario_master_20",
        "name": "Scenario Legend",
        "description": "Complete all 20 scenarios",
        "icon": "👑",
        "category": "scenarios",
        "tier": "platinum",
        "conditions": [{"type": "scenarios_completed", "target": 20}],
        "xp_reward": 1000,
        "order": 4
    },
    
    # Vocabulary Achievements
    {
        "code": "vocab_starter",
        "name": "Word Collector",
        "description": "Learn 10 new words",
        "icon": "📖",
        "category": "vocabulary",
        "tier": "bronze",
        "conditions": [{"type": "words_learned", "target": 10}],
        "xp_reward": 50,
        "order": 10
    },
    {
        "code": "vocab_learner_50",
        "name": "Vocabulary Builder",
        "description": "Learn 50 words",
        "icon": "📚",
        "category": "vocabulary",
        "tier": "silver",
        "conditions": [{"type": "words_learned", "target": 50}],
        "xp_reward": 150,
        "order": 11
    },
    {
        "code": "vocab_master_100",
        "name": "Word Master",
        "description": "Learn 100 words",
        "icon": "🎓",
        "category": "vocabulary",
        "tier": "gold",
        "conditions": [{"type": "words_learned", "target": 100}],
        "xp_reward": 400,
        "order": 12
    },
    {
        "code": "vocab_legend_500",
        "name": "Vocabulary Legend",
        "description": "Learn 500 words",
        "icon": "🌟",
        "category": "vocabulary",
        "tier": "platinum",
        "conditions": [{"type": "words_learned", "target": 500}],
        "xp_reward": 2000,
        "order": 13
    },
    
    # Quiz Achievements
    {
        "code": "quiz_beginner",
        "name": "Quiz Starter",
        "description": "Complete your first quiz",
        "icon": "🎯",
        "category": "quiz",
        "tier": "bronze",
        "conditions": [{"type": "quizzes_completed", "target": 1}],
        "xp_reward": 30,
        "order": 20
    },
    {
        "code": "quiz_perfect",
        "name": "Perfect Score",
        "description": "Get 100% on a quiz",
        "icon": "💯",
        "category": "quiz",
        "tier": "silver",
        "conditions": [{"type": "perfect_quizzes", "target": 1}],
        "xp_reward": 100,
        "order": 21
    },
    {
        "code": "quiz_master_10",
        "name": "Quiz Master",
        "description": "Complete 10 quizzes",
        "icon": "🧠",
        "category": "quiz",
        "tier": "gold",
        "conditions": [{"type": "quizzes_completed", "target": 10}],
        "xp_reward": 300,
        "order": 22
    },
    
    # Streak Achievements
    {
        "code": "streak_3",
        "name": "Getting Started",
        "description": "3-day learning streak",
        "icon": "🔥",
        "category": "streak",
        "tier": "bronze",
        "conditions": [{"type": "current_streak", "target": 3}],
        "xp_reward": 50,
        "order": 30
    },
    {
        "code": "streak_7",
        "name": "Week Warrior",
        "description": "7-day learning streak",
        "icon": "⚡",
        "category": "streak",
        "tier": "silver",
        "conditions": [{"type": "current_streak", "target": 7}],
        "xp_reward": 150,
        "order": 31
    },
    {
        "code": "streak_30",
        "name": "Monthly Master",
        "description": "30-day learning streak",
        "icon": "💪",
        "category": "streak",
        "tier": "gold",
        "conditions": [{"type": "current_streak", "target": 30}],
        "xp_reward": 500,
        "order": 32
    },
    {
        "code": "streak_100",
        "name": "Dedication Legend",
        "description": "100-day learning streak",
        "icon": "🏅",
        "category": "streak",
        "tier": "platinum",
        "conditions": [{"type": "current_streak", "target": 100}],
        "xp_reward": 2000,
        "order": 33
    },
    
    # Grammar Achievements
    {
        "code": "grammar_first",
        "name": "Grammar Checker",
        "description": "Check your first sentence",
        "icon": "✏️",
        "category": "grammar",
        "tier": "bronze",
        "conditions": [{"type": "grammar_checks", "target": 1}],
        "xp_reward": 25,
        "order": 40
    },
    {
        "code": "grammar_fixer_10",
        "name": "Error Corrector",
        "description": "Fix 10 grammar errors",
        "icon": "✅",
        "category": "grammar",
        "tier": "silver",
        "conditions": [{"type": "grammar_errors_fixed", "target": 10}],
        "xp_reward": 100,
        "order": 41
    },
    {
        "code": "grammar_master_50",
        "name": "Grammar Master",
        "description": "Fix 50 grammar errors",
        "icon": "📝",
        "category": "grammar",
        "tier": "gold",
        "conditions": [{"type": "grammar_errors_fixed", "target": 50}],
        "xp_reward": 400,
        "order": 42
    },
    
    # Special Achievements
    {
        "code": "early_bird",
        "name": "Early Bird",
        "description": "Complete a lesson before 8 AM",
        "icon": "🌅",
        "category": "special",
        "tier": "silver",
        "conditions": [{"type": "early_morning_activity", "target": 1}],
        "xp_reward": 100,
        "order": 50,
        "secret": True
    },
    {
        "code": "night_owl",
        "name": "Night Owl",
        "description": "Complete a lesson after 10 PM",
        "icon": "🦉",
        "category": "special",
        "tier": "silver",
        "conditions": [{"type": "late_night_activity", "target": 1}],
        "xp_reward": 100,
        "order": 51,
        "secret": True
    },
    {
        "code": "weekend_warrior",
        "name": "Weekend Warrior",
        "description": "Study on both Saturday and Sunday",
        "icon": "🎉",
        "category": "special",
        "tier": "silver",
        "conditions": [{"type": "weekend_study", "target": 1}],
        "xp_reward": 150,
        "order": 52,
        "secret": True
    },
]


# XP levels (exponential growth)
def calculate_xp_for_level(level: int) -> int:
    """Calculate total XP needed to reach a level"""
    if level <= 1:
        return 0
    # Formula: 100 * (level - 1) ^ 1.5
    return int(100 * ((level - 1) ** 1.5))


def get_level_from_xp(xp: int) -> tuple[int, int, int]:
    """
    Get level, current XP in level, and XP needed for next level
    Returns: (level, xp_in_current_level, xp_to_next_level)
    """
    level = 1
    while calculate_xp_for_level(level + 1) <= xp:
        level += 1
    
    xp_for_current_level = calculate_xp_for_level(level)
    xp_for_next_level = calculate_xp_for_level(level + 1)
    xp_in_current_level = xp - xp_for_current_level
    xp_to_next_level = xp_for_next_level - xp_for_current_level
    
    return level, xp_in_current_level, xp_to_next_level
