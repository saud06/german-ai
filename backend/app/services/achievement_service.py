"""
Achievement service for managing user achievements and gamification
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.achievement import (
    Achievement,
    UserAchievement,
    UserStats,
    ACHIEVEMENT_DEFINITIONS,
    calculate_xp_for_level,
    get_level_from_xp
)


class AchievementService:
    """Service for managing achievements and user stats"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.achievements_collection = db.achievements
        self.user_achievements_collection = db.user_achievements
        self.user_stats_collection = db.user_stats
    
    async def initialize_achievements(self):
        """Initialize achievement definitions in database"""
        for achievement_def in ACHIEVEMENT_DEFINITIONS:
            existing = await self.achievements_collection.find_one(
                {"code": achievement_def["code"]}
            )
            if not existing:
                await self.achievements_collection.insert_one(achievement_def)
    
    async def get_user_stats(self, user_id: str) -> Optional[UserStats]:
        """Get user's statistics"""
        stats_dict = await self.user_stats_collection.find_one({"user_id": user_id})
        if stats_dict:
            return UserStats(**stats_dict)
        
        # Create new stats for user
        new_stats = UserStats(user_id=user_id)
        await self.user_stats_collection.insert_one(new_stats.dict(by_alias=True, exclude={"id"}))
        return new_stats
    
    async def update_user_stats(self, user_id: str, updates: Dict[str, Any]) -> UserStats:
        """Update user statistics"""
        updates["updated_at"] = datetime.utcnow()
        
        await self.user_stats_collection.update_one(
            {"user_id": user_id},
            {"$set": updates},
            upsert=True
        )
        
        return await self.get_user_stats(user_id)
    
    async def add_xp(self, user_id: str, xp_amount: int, reason: str = "") -> Dict[str, Any]:
        """
        Add XP to user and check for level up
        Returns: {leveled_up: bool, new_level: int, xp_gained: int}
        """
        stats = await self.get_user_stats(user_id)
        old_level = stats.level
        new_total_xp = stats.total_xp + xp_amount
        
        # Calculate new level
        new_level, xp_in_level, xp_to_next = get_level_from_xp(new_total_xp)
        
        # Update stats
        await self.update_user_stats(user_id, {
            "total_xp": new_total_xp,
            "level": new_level,
            "xp_to_next_level": xp_to_next
        })
        
        # Create level-up notification if leveled up
        if new_level > old_level:
            try:
                from ..services.notification_service import NotificationService
                notification_service = NotificationService(self.db)
                await notification_service.create_level_up_notification(
                    user_id=user_id,
                    new_level=new_level
                )
            except Exception as e:
                print(f"Failed to create level-up notification: {e}")
        
        return {
            "leveled_up": new_level > old_level,
            "old_level": old_level,
            "new_level": new_level,
            "xp_gained": xp_amount,
            "total_xp": new_total_xp,
            "xp_to_next_level": xp_to_next
        }
    
    async def update_streak(self, user_id: str) -> Dict[str, Any]:
        """
        Update user's daily streak
        Returns: {streak_continued: bool, current_streak: int, longest_streak: int}
        """
        stats = await self.get_user_stats(user_id)
        today = datetime.utcnow().date()
        
        if not stats.last_activity_date:
            # First activity
            new_streak = 1
            streak_continued = True
        else:
            last_date = stats.last_activity_date.date()
            days_diff = (today - last_date).days
            
            if days_diff == 0:
                # Same day, no change
                return {
                    "streak_continued": True,
                    "current_streak": stats.current_streak,
                    "longest_streak": stats.longest_streak
                }
            elif days_diff == 1:
                # Consecutive day
                new_streak = stats.current_streak + 1
                streak_continued = True
            else:
                # Streak broken
                new_streak = 1
                streak_continued = False
        
        # Update longest streak
        new_longest = max(new_streak, stats.longest_streak)
        
        await self.update_user_stats(user_id, {
            "current_streak": new_streak,
            "longest_streak": new_longest,
            "last_activity_date": datetime.utcnow()
        })
        
        # Check streak achievements
        await self.check_achievements(user_id, "current_streak", new_streak)
        
        return {
            "streak_continued": streak_continued,
            "current_streak": new_streak,
            "longest_streak": new_longest
        }
    
    async def record_scenario_completion(
        self,
        user_id: str,
        scenario_id: str,
        completion_time: int,
        perfect: bool = False
    ) -> Dict[str, Any]:
        """Record scenario completion and award XP"""
        stats = await self.get_user_stats(user_id)
        
        # Update stats
        new_completed = stats.scenarios_completed + 1
        new_total_time = stats.total_scenario_time + completion_time
        
        await self.update_user_stats(user_id, {
            "scenarios_completed": new_completed,
            "total_scenario_time": new_total_time
        })
        
        # Award XP
        base_xp = 100
        bonus_xp = 50 if perfect else 0
        xp_result = await self.add_xp(user_id, base_xp + bonus_xp, f"Completed scenario {scenario_id}")
        
        # Check achievements
        await self.check_achievements(user_id, "scenarios_completed", new_completed)
        
        # Update streak
        streak_result = await self.update_streak(user_id)
        
        return {
            **xp_result,
            **streak_result,
            "scenarios_completed": new_completed
        }
    
    async def record_vocabulary_learned(self, user_id: str, word_count: int = 1) -> Dict[str, Any]:
        """Record vocabulary learning"""
        stats = await self.get_user_stats(user_id)
        new_count = stats.words_learned + word_count
        
        await self.update_user_stats(user_id, {
            "words_learned": new_count
        })
        
        # Award XP
        xp_result = await self.add_xp(user_id, 10 * word_count, f"Learned {word_count} words")
        
        # Check achievements
        await self.check_achievements(user_id, "words_learned", new_count)
        
        return {**xp_result, "words_learned": new_count}
    
    async def record_quiz_completion(
        self,
        user_id: str,
        score: float,
        perfect: bool = False
    ) -> Dict[str, Any]:
        """Record quiz completion"""
        stats = await self.get_user_stats(user_id)
        
        new_completed = stats.quizzes_completed + 1
        new_perfect = stats.perfect_quizzes + (1 if perfect else 0)
        
        # Calculate new average accuracy
        total_score = stats.quiz_accuracy * stats.quizzes_completed + score
        new_accuracy = total_score / new_completed
        
        await self.update_user_stats(user_id, {
            "quizzes_completed": new_completed,
            "quiz_accuracy": new_accuracy,
            "perfect_quizzes": new_perfect
        })
        
        # Award XP
        base_xp = 30
        bonus_xp = 70 if perfect else int(score * 0.5)
        xp_result = await self.add_xp(user_id, base_xp + bonus_xp, "Completed quiz")
        
        # Check achievements
        await self.check_achievements(user_id, "quizzes_completed", new_completed)
        if perfect:
            await self.check_achievements(user_id, "perfect_quizzes", new_perfect)
        
        return {**xp_result, "quizzes_completed": new_completed}
    
    async def record_grammar_check(
        self,
        user_id: str,
        errors_found: int = 0
    ) -> Dict[str, Any]:
        """Record grammar check"""
        stats = await self.get_user_stats(user_id)
        
        new_checks = stats.grammar_checks + 1
        new_errors_fixed = stats.grammar_errors_fixed + errors_found
        
        await self.update_user_stats(user_id, {
            "grammar_checks": new_checks,
            "grammar_errors_fixed": new_errors_fixed
        })
        
        # Award XP
        xp_amount = 5 + (errors_found * 10)
        xp_result = await self.add_xp(user_id, xp_amount, "Grammar check")
        
        # Check achievements
        await self.check_achievements(user_id, "grammar_checks", new_checks)
        await self.check_achievements(user_id, "grammar_errors_fixed", new_errors_fixed)
        
        return {**xp_result, "grammar_checks": new_checks}
    
    async def check_achievements(
        self,
        user_id: str,
        stat_type: str,
        current_value: int
    ) -> List[Achievement]:
        """
        Check if user unlocked any achievements
        Returns list of newly unlocked achievements
        """
        # Get all achievements for this stat type
        achievements = await self.achievements_collection.find({
            "conditions.type": stat_type
        }).to_list(length=100)
        
        newly_unlocked = []
        
        for achievement_dict in achievements:
            achievement = Achievement(**achievement_dict)
            
            # Check if already unlocked
            existing = await self.user_achievements_collection.find_one({
                "user_id": user_id,
                "achievement_code": achievement.code,
                "unlocked": True
            })
            
            if existing:
                continue
            
            # Check if conditions are met
            conditions_met = True
            for condition in achievement.conditions:
                if condition.type == stat_type:
                    if current_value < condition.target:
                        conditions_met = False
                        break
            
            if conditions_met:
                # Unlock achievement
                await self.unlock_achievement(user_id, achievement.code)
                newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    async def unlock_achievement(self, user_id: str, achievement_code: str) -> bool:
        """Unlock an achievement for user"""
        # Get achievement
        achievement_dict = await self.achievements_collection.find_one({"code": achievement_code})
        if not achievement_dict:
            return False
        
        achievement = Achievement(**achievement_dict)
        
        # Create or update user achievement
        await self.user_achievements_collection.update_one(
            {
                "user_id": user_id,
                "achievement_code": achievement_code
            },
            {
                "$set": {
                    "unlocked": True,
                    "progress": 100,
                    "unlocked_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "user_id": user_id,
                    "achievement_code": achievement_code,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        # Award XP
        await self.add_xp(user_id, achievement.xp_reward, f"Achievement: {achievement.name}")
        
        # Create notification
        try:
            from ..services.notification_service import NotificationService
            notification_service = NotificationService(self.db)
            await notification_service.create_achievement_notification(
                user_id=user_id,
                achievement_code=achievement.code,
                achievement_name=achievement.name,
                achievement_tier=achievement.tier,
                xp_reward=achievement.xp_reward,
                icon=achievement.icon
            )
        except Exception as e:
            # Don't fail achievement unlock if notification fails
            print(f"Failed to create achievement notification: {e}")
        
        return True
    
    async def get_user_achievements(
        self,
        user_id: str,
        unlocked_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get user's achievements with progress"""
        # Get all achievements
        all_achievements = await self.achievements_collection.find(
            {"secret": False} if not unlocked_only else {}
        ).to_list(length=100)
        
        # Get user's progress
        user_progress = await self.user_achievements_collection.find(
            {"user_id": user_id}
        ).to_list(length=100)
        
        progress_dict = {p.get("achievement_code", p.get("code", str(p.get("_id")))): p for p in user_progress}
        
        result = []
        for achievement_dict in all_achievements:
            achievement = Achievement(**achievement_dict)
            user_ach = progress_dict.get(achievement.code)
            
            if unlocked_only and (not user_ach or not user_ach.get("unlocked")):
                continue
            
            result.append({
                "achievement": achievement.dict(),
                "unlocked": user_ach.get("unlocked", False) if user_ach else False,
                "progress": user_ach.get("progress", 0) if user_ach else 0,
                "unlocked_at": user_ach.get("unlocked_at") if user_ach else None
            })
        
        # Sort by order
        result.sort(key=lambda x: x["achievement"]["order"])
        
        return result
    
    async def get_leaderboard(
        self,
        leaderboard_type: str = "xp",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get leaderboard
        Types: xp, level, streak, scenarios, quizzes
        """
        sort_field = {
            "xp": "total_xp",
            "level": "level",
            "streak": "current_streak",
            "scenarios": "scenarios_completed",
            "quizzes": "quizzes_completed"
        }.get(leaderboard_type, "total_xp")
        
        try:
            stats = await self.user_stats_collection.find().sort(
                sort_field, -1
            ).limit(limit).to_list(length=limit)
            
            # Convert ObjectId to string
            for stat in stats:
                if "_id" in stat:
                    stat["_id"] = str(stat["_id"])
            
            return stats
        except Exception as e:
            # Return empty list if no stats yet
            return []
