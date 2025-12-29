"""
Gamification models for XP, levels, streaks, and rewards
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class UserLevel(BaseModel):
    """User level and XP tracking"""
    user_id: str
    level: int = 1
    current_xp: int = 0
    total_xp: int = 0
    next_level_xp: int = 100
    
    # Streak tracking
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[date] = None
    
    # Statistics
    total_lessons_completed: int = 0
    total_scenarios_completed: int = 0
    total_quizzes_completed: int = 0
    total_reviews_completed: int = 0
    total_words_learned: int = 0
    
    # Achievements
    achievements_unlocked: List[str] = []
    badges_earned: List[str] = []
    
    # Rewards
    coins: int = 0
    gems: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class XPEvent(BaseModel):
    """XP earning event"""
    user_id: str
    event_type: str  # lesson, quiz, scenario, review, achievement, daily_login, streak_bonus
    xp_earned: int
    description: str
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DailyStreak(BaseModel):
    """Daily streak tracking"""
    user_id: str
    date: date
    activities_completed: List[str] = []
    xp_earned: int = 0
    streak_day: int = 1
    bonus_applied: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WeeklyChallenge(BaseModel):
    """Weekly challenge definition"""
    id: str
    title: str
    description: str
    challenge_type: str  # scenarios, quizzes, reviews, lessons, words
    target: int  # Number to complete
    xp_reward: int
    coin_reward: int
    gem_reward: int = 0
    start_date: date
    end_date: date
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserChallenge(BaseModel):
    """User's progress on a challenge"""
    user_id: str
    challenge_id: str
    progress: int = 0
    completed: bool = False
    claimed: bool = False
    completed_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Leaderboard(BaseModel):
    """Leaderboard entry"""
    user_id: str
    username: str
    level: int
    total_xp: int
    current_streak: int
    rank: int
    avatar_url: Optional[str] = None


class FriendRequest(BaseModel):
    """Friend request"""
    from_user_id: str
    to_user_id: str
    status: str = "pending"  # pending, accepted, rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Friendship(BaseModel):
    """Friendship relationship"""
    user_id: str
    friend_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Reward(BaseModel):
    """Unlockable reward"""
    id: str
    name: str
    description: str
    reward_type: str  # avatar, theme, badge, powerup
    cost_coins: int = 0
    cost_gems: int = 0
    level_required: int = 1
    image_url: Optional[str] = None
    active: bool = True


class UserReward(BaseModel):
    """User's unlocked rewards"""
    user_id: str
    reward_id: str
    unlocked_at: datetime = Field(default_factory=datetime.utcnow)


# XP calculation constants
XP_REWARDS = {
    "daily_login": 10,
    "lesson_complete": 20,
    "quiz_complete": 30,
    "quiz_perfect": 50,
    "scenario_complete": 40,
    "scenario_perfect": 60,
    "review_correct": 5,
    "review_session": 15,
    "word_learned": 10,
    "achievement_unlock": 100,
    "streak_3_days": 25,
    "streak_7_days": 75,
    "streak_30_days": 300,
    "challenge_complete": 150,
    "friend_referral": 200,
}

# Level progression (XP required for each level)
def calculate_xp_for_level(level: int) -> int:
    """Calculate XP required to reach a level"""
    # Formula: 100 * level^1.5
    return int(100 * (level ** 1.5))


def calculate_level_from_xp(total_xp: int) -> int:
    """Calculate level from total XP"""
    level = 1
    while total_xp >= calculate_xp_for_level(level + 1):
        level += 1
    return level
