"""
Gamification service for XP, levels, streaks, and rewards
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models.gamification import (
    UserLevel, XPEvent, DailyStreak, WeeklyChallenge, UserChallenge,
    Leaderboard, XP_REWARDS, calculate_xp_for_level, calculate_level_from_xp
)


class GamificationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.user_levels = db.user_levels
        self.xp_events = db.xp_events
        self.daily_streaks = db.daily_streaks
        self.weekly_challenges = db.weekly_challenges
        self.user_challenges = db.user_challenges
    
    async def get_or_create_user_level(self, user_id: str) -> UserLevel:
        """Get or create user level data"""
        user_level = await self.user_levels.find_one({"user_id": user_id})
        
        if not user_level:
            user_level = UserLevel(user_id=user_id)
            await self.user_levels.insert_one(user_level.dict())
        else:
            user_level = UserLevel(**user_level)
        
        return user_level
    
    async def award_xp(
        self,
        user_id: str,
        event_type: str,
        custom_xp: Optional[int] = None,
        description: Optional[str] = None,
        metadata: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """Award XP to user and handle level ups"""
        
        # Get XP amount
        xp_earned = custom_xp if custom_xp else XP_REWARDS.get(event_type, 0)
        
        if xp_earned == 0:
            return {"success": False, "message": "Invalid event type"}
        
        # Get user level
        user_level = await self.get_or_create_user_level(user_id)
        
        # Calculate new XP and level
        old_level = user_level.level
        new_total_xp = user_level.total_xp + xp_earned
        new_level = calculate_level_from_xp(new_total_xp)
        
        # Calculate current XP in level
        xp_for_current_level = calculate_xp_for_level(new_level)
        xp_for_next_level = calculate_xp_for_level(new_level + 1)
        current_xp = new_total_xp - xp_for_current_level
        next_level_xp = xp_for_next_level - xp_for_current_level
        
        # Update user level
        update_data = {
            "total_xp": new_total_xp,
            "level": new_level,
            "current_xp": current_xp,
            "next_level_xp": next_level_xp,
            "updated_at": datetime.utcnow()
        }
        
        # Update statistics based on event type
        if event_type == "lesson_complete":
            update_data["total_lessons_completed"] = user_level.total_lessons_completed + 1
        elif event_type in ["quiz_complete", "quiz_perfect"]:
            update_data["total_quizzes_completed"] = user_level.total_quizzes_completed + 1
        elif event_type in ["scenario_complete", "scenario_perfect"]:
            update_data["total_scenarios_completed"] = user_level.total_scenarios_completed + 1
        elif event_type in ["review_correct", "review_session"]:
            update_data["total_reviews_completed"] = user_level.total_reviews_completed + 1
        elif event_type == "word_learned":
            update_data["total_words_learned"] = user_level.total_words_learned + 1
        
        await self.user_levels.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        # Log XP event
        xp_event = XPEvent(
            user_id=user_id,
            event_type=event_type,
            xp_earned=xp_earned,
            description=description or f"Earned {xp_earned} XP from {event_type}",
            metadata=metadata
        )
        await self.xp_events.insert_one(xp_event.dict())
        
        # Check for level up
        level_up = new_level > old_level
        
        return {
            "success": True,
            "xp_earned": xp_earned,
            "total_xp": new_total_xp,
            "level": new_level,
            "level_up": level_up,
            "old_level": old_level,
            "current_xp": current_xp,
            "next_level_xp": next_level_xp
        }
    
    async def update_daily_streak(self, user_id: str) -> Dict[str, Any]:
        """Update user's daily streak"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Get user level
        user_level = await self.get_or_create_user_level(user_id)
        
        # Check if already logged in today
        today_streak = await self.daily_streaks.find_one({
            "user_id": user_id,
            "date": today.isoformat()
        })
        
        if today_streak:
            return {
                "success": True,
                "already_logged": True,
                "current_streak": user_level.current_streak
            }
        
        # Check yesterday's streak
        yesterday_streak = await self.daily_streaks.find_one({
            "user_id": user_id,
            "date": yesterday.isoformat()
        })
        
        # Calculate new streak
        if yesterday_streak:
            new_streak = user_level.current_streak + 1
        else:
            new_streak = 1
        
        # Update user level
        longest_streak = max(user_level.longest_streak, new_streak)
        await self.user_levels.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "current_streak": new_streak,
                    "longest_streak": longest_streak,
                    "last_activity_date": today.isoformat(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Create today's streak record
        daily_streak = DailyStreak(
            user_id=user_id,
            date=today,
            streak_day=new_streak
        )
        streak_dict = daily_streak.dict()
        streak_dict["date"] = today.isoformat()  # Convert date to string for MongoDB
        await self.daily_streaks.insert_one(streak_dict)
        
        # Award streak bonuses
        bonus_xp = 0
        if new_streak == 3:
            result = await self.award_xp(user_id, "streak_3_days", description="3-day streak bonus!")
            bonus_xp = result.get("xp_earned", 0)
        elif new_streak == 7:
            result = await self.award_xp(user_id, "streak_7_days", description="7-day streak bonus!")
            bonus_xp = result.get("xp_earned", 0)
        elif new_streak == 30:
            result = await self.award_xp(user_id, "streak_30_days", description="30-day streak bonus!")
            bonus_xp = result.get("xp_earned", 0)
        
        # Daily login XP
        login_result = await self.award_xp(user_id, "daily_login", description="Daily login bonus")
        
        return {
            "success": True,
            "current_streak": new_streak,
            "longest_streak": longest_streak,
            "bonus_xp": bonus_xp,
            "login_xp": login_result.get("xp_earned", 0),
            "new_streak": new_streak == 1
        }
    
    async def get_leaderboard(
        self,
        leaderboard_type: str = "global",
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Leaderboard]:
        """Get leaderboard rankings"""
        
        # Get top users by total XP
        pipeline = [
            {"$sort": {"total_xp": -1}},
            {"$limit": limit}
        ]
        
        users = await self.user_levels.aggregate(pipeline).to_list(length=limit)
        
        # Get user details
        leaderboard = []
        for idx, user_level in enumerate(users):
            # Get username from users collection
            user = await self.db.users.find_one({"_id": user_level["user_id"]})
            username = user.get("email", "Unknown") if user else "Unknown"
            
            leaderboard.append(Leaderboard(
                user_id=user_level["user_id"],
                username=username,
                level=user_level["level"],
                total_xp=user_level["total_xp"],
                current_streak=user_level.get("current_streak", 0),
                rank=idx + 1
            ))
        
        return leaderboard
    
    async def get_user_rank(self, user_id: str) -> Dict[str, Any]:
        """Get user's global rank"""
        user_level = await self.get_or_create_user_level(user_id)
        
        # Count users with more XP
        rank = await self.user_levels.count_documents({
            "total_xp": {"$gt": user_level.total_xp}
        }) + 1
        
        # Get total users
        total_users = await self.user_levels.count_documents({})
        
        return {
            "rank": rank,
            "total_users": total_users,
            "percentile": round((1 - (rank / total_users)) * 100, 1) if total_users > 0 else 0
        }
    
    async def create_weekly_challenge(
        self,
        title: str,
        description: str,
        challenge_type: str,
        target: int,
        xp_reward: int,
        coin_reward: int,
        gem_reward: int = 0
    ) -> WeeklyChallenge:
        """Create a new weekly challenge"""
        
        today = date.today()
        # Start on Monday
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        
        challenge = WeeklyChallenge(
            id=f"challenge_{datetime.utcnow().timestamp()}",
            title=title,
            description=description,
            challenge_type=challenge_type,
            target=target,
            xp_reward=xp_reward,
            coin_reward=coin_reward,
            gem_reward=gem_reward,
            start_date=start_date,
            end_date=end_date
        )
        
        challenge_dict = challenge.dict()
        challenge_dict["start_date"] = start_date.isoformat()  # Convert date to string
        challenge_dict["end_date"] = end_date.isoformat()  # Convert date to string
        await self.weekly_challenges.insert_one(challenge_dict)
        return challenge
    
    async def get_active_challenges(self) -> List[WeeklyChallenge]:
        """Get all active weekly challenges"""
        today = date.today()
        
        challenges = await self.weekly_challenges.find({
            "active": True,
            "start_date": {"$lte": today.isoformat()},
            "end_date": {"$gte": today.isoformat()}
        }).to_list(length=100)
        
        return [WeeklyChallenge(**c) for c in challenges]
    
    async def update_challenge_progress(
        self,
        user_id: str,
        challenge_type: str,
        increment: int = 1
    ) -> List[Dict[str, Any]]:
        """Update user's progress on challenges"""
        
        # Get active challenges of this type
        challenges = await self.weekly_challenges.find({
            "active": True,
            "challenge_type": challenge_type,
            "end_date": {"$gte": date.today().isoformat()}
        }).to_list(length=100)
        
        results = []
        for challenge in challenges:
            # Get or create user challenge
            user_challenge = await self.user_challenges.find_one({
                "user_id": user_id,
                "challenge_id": challenge["id"]
            })
            
            if not user_challenge:
                user_challenge = UserChallenge(
                    user_id=user_id,
                    challenge_id=challenge["id"],
                    progress=0
                )
                await self.user_challenges.insert_one(user_challenge.dict())
            
            # Update progress
            new_progress = user_challenge.get("progress", 0) + increment
            completed = new_progress >= challenge["target"]
            
            update_data = {
                "progress": new_progress,
                "completed": completed
            }
            
            if completed and not user_challenge.get("completed"):
                update_data["completed_at"] = datetime.utcnow()
            
            await self.user_challenges.update_one(
                {"user_id": user_id, "challenge_id": challenge["id"]},
                {"$set": update_data}
            )
            
            results.append({
                "challenge_id": challenge["id"],
                "title": challenge["title"],
                "progress": new_progress,
                "target": challenge["target"],
                "completed": completed,
                "newly_completed": completed and not user_challenge.get("completed")
            })
        
        return results
    
    async def claim_challenge_reward(
        self,
        user_id: str,
        challenge_id: str
    ) -> Dict[str, Any]:
        """Claim reward for completed challenge"""
        
        # Get user challenge
        user_challenge = await self.user_challenges.find_one({
            "user_id": user_id,
            "challenge_id": challenge_id
        })
        
        if not user_challenge:
            return {"success": False, "message": "Challenge not found"}
        
        if not user_challenge.get("completed"):
            return {"success": False, "message": "Challenge not completed"}
        
        if user_challenge.get("claimed"):
            return {"success": False, "message": "Reward already claimed"}
        
        # Get challenge details
        challenge = await self.weekly_challenges.find_one({"id": challenge_id})
        if not challenge:
            return {"success": False, "message": "Challenge not found"}
        
        # Award XP
        xp_result = await self.award_xp(
            user_id,
            "challenge_complete",
            custom_xp=challenge["xp_reward"],
            description=f"Completed challenge: {challenge['title']}"
        )
        
        # Award coins and gems
        await self.user_levels.update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "coins": challenge["coin_reward"],
                    "gems": challenge.get("gem_reward", 0)
                }
            }
        )
        
        # Mark as claimed
        await self.user_challenges.update_one(
            {"user_id": user_id, "challenge_id": challenge_id},
            {
                "$set": {
                    "claimed": True,
                    "claimed_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "xp_earned": challenge["xp_reward"],
            "coins_earned": challenge["coin_reward"],
            "gems_earned": challenge.get("gem_reward", 0)
        }
