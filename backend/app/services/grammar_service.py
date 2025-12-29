"""
Grammar Service
Manages grammar rules and user progress
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId


class GrammarService:
    """Service for managing grammar rules"""
    
    def __init__(self, db):
        self.db = db
        self.rules_collection = db["grammar_rules"]
        self.progress_collection = db["user_grammar_progress"]
    
    async def initialize_rules(self):
        """Initialize grammar rules in database"""
        from app.seed.grammar_rules_data import get_grammar_rules
        
        # Check if rules already exist
        count = await self.rules_collection.count_documents({})
        if count > 0:
            return {"message": f"Grammar rules already initialized ({count} rules)"}
        
        # Get rules
        rules = get_grammar_rules()
        
        # Insert rules
        rules_data = [rule.dict(by_alias=True, exclude={"id"}) for rule in rules]
        result = await self.rules_collection.insert_many(rules_data)
        
        return {
            "message": "Grammar rules initialized successfully",
            "count": len(result.inserted_ids)
        }
    
    async def get_rules(
        self,
        level: Optional[str] = None,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get grammar rules with optional filtering"""
        query = {}
        
        if level:
            query["level"] = level
        if category:
            query["category"] = category
        
        rules = await self.rules_collection.find(query).skip(skip).limit(limit).to_list(length=limit)
        
        # Convert ObjectId to string
        for rule in rules:
            if "_id" in rule:
                rule["_id"] = str(rule["_id"])
        
        return rules
    
    async def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific grammar rule"""
        try:
            rule = await self.rules_collection.find_one({"_id": ObjectId(rule_id)})
            if rule:
                rule["_id"] = str(rule["_id"])
            return rule
        except:
            return None
    
    async def get_user_progress(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's grammar progress"""
        progress = await self.progress_collection.find({"user_id": user_id}).to_list(length=100)
        
        for item in progress:
            if "_id" in item:
                item["_id"] = str(item["_id"])
        
        return progress
    
    async def update_progress(
        self,
        user_id: str,
        rule_id: str,
        exercise_correct: bool
    ) -> Dict[str, Any]:
        """Update user's progress with a grammar rule"""
        
        # Find existing progress
        progress = await self.progress_collection.find_one({
            "user_id": user_id,
            "rule_id": rule_id
        })
        
        if not progress:
            # Create new progress
            progress = {
                "user_id": user_id,
                "rule_id": rule_id,
                "studied": True,
                "mastered": False,
                "exercises_completed": 1,
                "exercises_correct": 1 if exercise_correct else 0,
                "accuracy": 1.0 if exercise_correct else 0.0,
                "last_studied": datetime.utcnow(),
                "times_reviewed": 1
            }
            result = await self.progress_collection.insert_one(progress)
            progress["_id"] = str(result.inserted_id)
        else:
            # Update existing progress
            exercises_completed = progress.get("exercises_completed", 0) + 1
            exercises_correct = progress.get("exercises_correct", 0) + (1 if exercise_correct else 0)
            accuracy = exercises_correct / exercises_completed if exercises_completed > 0 else 0.0
            
            # Check if mastered (80% accuracy with at least 5 exercises)
            mastered = accuracy >= 0.8 and exercises_completed >= 5
            
            update_data = {
                "$set": {
                    "studied": True,
                    "mastered": mastered,
                    "exercises_completed": exercises_completed,
                    "exercises_correct": exercises_correct,
                    "accuracy": accuracy,
                    "last_studied": datetime.utcnow()
                },
                "$inc": {"times_reviewed": 1}
            }
            
            await self.progress_collection.update_one(
                {"_id": progress["_id"]},
                update_data
            )
            
            progress["exercises_completed"] = exercises_completed
            progress["exercises_correct"] = exercises_correct
            progress["accuracy"] = accuracy
            progress["mastered"] = mastered
            progress["_id"] = str(progress["_id"])
        
        return progress
    
    async def get_recommended_rules(self, user_id: str, level: str) -> List[Dict[str, Any]]:
        """Get recommended grammar rules for user"""
        
        # Get user's progress
        progress = await self.get_user_progress(user_id)
        studied_rule_ids = [p["rule_id"] for p in progress if p.get("studied")]
        
        # Find unstudied rules at user's level
        query = {
            "level": level,
            "_id": {"$nin": [ObjectId(rid) for rid in studied_rule_ids if ObjectId.is_valid(rid)]}
        }
        
        rules = await self.rules_collection.find(query).limit(5).to_list(length=5)
        
        for rule in rules:
            if "_id" in rule:
                rule["_id"] = str(rule["_id"])
        
        return rules
    
    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's grammar statistics"""
        
        progress = await self.get_user_progress(user_id)
        
        total_rules = await self.rules_collection.count_documents({})
        studied_rules = len([p for p in progress if p.get("studied")])
        mastered_rules = len([p for p in progress if p.get("mastered")])
        
        total_exercises = sum(p.get("exercises_completed", 0) for p in progress)
        total_correct = sum(p.get("exercises_correct", 0) for p in progress)
        overall_accuracy = total_correct / total_exercises if total_exercises > 0 else 0.0
        
        return {
            "total_rules": total_rules,
            "studied_rules": studied_rules,
            "mastered_rules": mastered_rules,
            "completion_percentage": (studied_rules / total_rules * 100) if total_rules > 0 else 0,
            "mastery_percentage": (mastered_rules / total_rules * 100) if total_rules > 0 else 0,
            "total_exercises": total_exercises,
            "total_correct": total_correct,
            "overall_accuracy": overall_accuracy
        }
