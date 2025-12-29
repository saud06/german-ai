"""
Scenario service for managing life simulation scenarios
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.scenario import Scenario, Character, Objective
from app.models.conversation_state import ConversationState, ObjectiveProgress, Message


class ScenarioService:
    """Service for scenario management"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.scenarios_collection = db.scenarios
        self.conversation_states_collection = db.conversation_states
    
    async def get_all_scenarios(self, difficulty: Optional[str] = None) -> List[Scenario]:
        """Get all scenarios, optionally filtered by difficulty"""
        query = {}
        if difficulty:
            query["difficulty"] = difficulty
        
        cursor = self.scenarios_collection.find(query).sort("created_at", -1)
        scenarios = await cursor.to_list(length=100)
        return [Scenario(**scenario) for scenario in scenarios]
    
    async def get_scenario_by_id(self, scenario_id: str) -> Optional[Scenario]:
        """Get scenario by ID"""
        if not ObjectId.is_valid(scenario_id):
            return None
        
        scenario = await self.scenarios_collection.find_one({"_id": ObjectId(scenario_id)})
        if scenario:
            # Characters are already embedded in the scenario document
            # No need to look them up from a separate collection
            return Scenario(**scenario)
        return None
    
    async def create_scenario(self, scenario: Scenario) -> Scenario:
        """Create a new scenario"""
        scenario_dict = scenario.dict(by_alias=True, exclude={"id"})
        result = await self.scenarios_collection.insert_one(scenario_dict)
        scenario.id = result.inserted_id
        return scenario
    
    async def update_scenario(self, scenario_id: str, scenario: Scenario) -> bool:
        """Update an existing scenario"""
        if not ObjectId.is_valid(scenario_id):
            return False
        
        scenario_dict = scenario.dict(by_alias=True, exclude={"id"})
        scenario_dict["updated_at"] = datetime.utcnow()
        
        result = await self.scenarios_collection.update_one(
            {"_id": ObjectId(scenario_id)},
            {"$set": scenario_dict}
        )
        return result.modified_count > 0
    
    async def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario"""
        if not ObjectId.is_valid(scenario_id):
            return False
        
        result = await self.scenarios_collection.delete_one({"_id": ObjectId(scenario_id)})
        return result.deleted_count > 0
    
    async def start_scenario(
        self,
        user_id: str,
        scenario_id: str,
        character_id: str
    ) -> Optional[ConversationState]:
        """Start a new scenario conversation"""
        # Get scenario
        scenario = await self.get_scenario_by_id(scenario_id)
        if not scenario:
            return None
        
        # Find character (handle both Character objects and string IDs)
        character = None
        for c in scenario.characters:
            if isinstance(c, str):
                # If it's a string ID, compare directly
                if c == character_id:
                    # Fetch the character details
                    char_doc = await self.db["characters"].find_one({"_id": ObjectId(character_id)})
                    if char_doc:
                        character = Character(
                            id=str(char_doc["_id"]),
                            name=char_doc.get("name", "Unknown"),
                            role=char_doc.get("role", ""),
                            personality=char_doc.get("personality", ""),
                            description=char_doc.get("description", ""),
                            greeting=char_doc.get("greeting", "Hallo!")
                        )
                    break
            else:
                # If it's a Character object, compare the id attribute
                if c.id == character_id:
                    character = c
                    break
        
        if not character:
            return None
        
        # Create objectives progress
        objectives_progress = [
            ObjectiveProgress(objective_id=obj.id, completed=False)
            for obj in scenario.objectives
        ]
        
        # Create conversation state
        state = ConversationState(
            user_id=user_id,
            scenario_id=scenario_id,
            character_id=character_id,
            objectives_progress=objectives_progress,
            messages=[],
            status="active"
        )
        
        # Add initial greeting from character
        greeting_message = Message(
            role="character",
            content=character.greeting,
            timestamp=datetime.utcnow()
        )
        state.messages.append(greeting_message)
        state.total_messages = 1
        
        # Save to database
        state_dict = state.dict(by_alias=True, exclude={"id"})
        result = await self.conversation_states_collection.insert_one(state_dict)
        state.id = result.inserted_id
        
        return state
    
    async def get_conversation_state(
        self,
        user_id: str,
        scenario_id: str
    ) -> Optional[ConversationState]:
        """Get conversation state for user and scenario (active or completed)"""
        state = await self.conversation_states_collection.find_one({
            "user_id": user_id,
            "scenario_id": scenario_id,
            "status": {"$in": ["active", "completed"]}
        })
        
        if state:
            return ConversationState(**state)
        return None
    
    async def update_conversation_state(self, state: ConversationState) -> bool:
        """Update conversation state"""
        if not state.id:
            return False
        
        state.last_activity = datetime.utcnow()
        state_dict = state.dict(by_alias=True, exclude={"id"})
        
        result = await self.conversation_states_collection.update_one(
            {"_id": state.id},
            {"$set": state_dict}
        )
        return result.modified_count > 0
    
    async def complete_objective(
        self,
        state: ConversationState,
        objective_id: str
    ) -> bool:
        """Mark an objective as completed"""
        for obj_progress in state.objectives_progress:
            if obj_progress.objective_id == objective_id and not obj_progress.completed:
                obj_progress.completed = True
                obj_progress.completed_at = datetime.utcnow()
                
                # Award points
                state.score += 20
                
                return True
        return False
    
    async def add_message(
        self,
        state: ConversationState,
        role: str,
        content: str,
        audio_url: Optional[str] = None
    ) -> None:
        """Add a message to conversation"""
        message = Message(
            role=role,
            content=content,
            audio_url=audio_url,
            timestamp=datetime.utcnow()
        )
        state.messages.append(message)
        state.total_messages += 1
    
    async def complete_scenario(self, state: ConversationState) -> None:
        """Mark scenario as completed"""
        state.status = "completed"
        state.completed_at = datetime.utcnow()
        
        # Calculate final score
        completed_objectives = sum(1 for obj in state.objectives_progress if obj.completed)
        total_objectives = len(state.objectives_progress)
        
        if total_objectives > 0:
            completion_rate = completed_objectives / total_objectives
            state.score = int(state.max_score * completion_rate)
        
        # Update Learning Path progress
        await self._update_learning_path_progress(state)
    
    async def _update_learning_path_progress(self, state: ConversationState) -> None:
        """Update user's Learning Path progress when scenario is completed"""
        from bson import ObjectId
        
        # Get the scenario to find which location/chapter it belongs to
        scenario = await self.scenarios_collection.find_one({"_id": ObjectId(state.scenario_id)})
        if not scenario:
            return
        
        # Find the location that contains this scenario
        location = await self.db.locations.find_one({"scenarios": ObjectId(state.scenario_id)})
        if not location:
            return
        
        chapter_id = str(location["chapter_id"])
        location_id = str(location["_id"])
        scenario_id = state.scenario_id
        
        # Get or create user progress
        progress_doc = await self.db.user_progress.find_one({"user_id": state.user_id})
        if not progress_doc:
            progress_doc = {
                "user_id": state.user_id,
                "current_chapter": chapter_id,
                "total_xp": 0,
                "level": 1,
                "chapter_progress": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await self.db.user_progress.insert_one(progress_doc)
        
        # Initialize chapter progress if needed
        if "chapter_progress" not in progress_doc:
            progress_doc["chapter_progress"] = {}
        
        if chapter_id not in progress_doc["chapter_progress"]:
            progress_doc["chapter_progress"][chapter_id] = {
                "scenarios_completed": [],
                "locations_completed": [],
                "progress_percent": 0,
                "xp_earned": 0
            }
        
        chapter_progress = progress_doc["chapter_progress"][chapter_id]
        
        # Add scenario to completed list if not already there
        if scenario_id not in chapter_progress["scenarios_completed"]:
            chapter_progress["scenarios_completed"].append(scenario_id)
            
            # Award XP
            xp_reward = scenario.get("xp_reward", 100)
            progress_doc["total_xp"] = progress_doc.get("total_xp", 0) + xp_reward
            chapter_progress["xp_earned"] = chapter_progress.get("xp_earned", 0) + xp_reward
            
            # Update level based on XP
            total_xp = progress_doc["total_xp"]
            new_level = 1
            while total_xp >= (new_level * 100):
                new_level += 1
            progress_doc["level"] = new_level
        
        # Check if location is complete (all scenarios AND vocabulary done)
        location_scenarios = [str(sid) for sid in location.get("scenarios", [])]
        scenarios_done = all(
            str(sid) in chapter_progress["scenarios_completed"] 
            for sid in location_scenarios
        )
        
        # Check if vocabulary set is complete
        location_vocab_set = str(location.get("vocab_set_id", ""))
        vocab_done = location_vocab_set in chapter_progress.get("vocab_sets_completed", []) if location_vocab_set else True
        
        location_complete = scenarios_done and vocab_done
        
        if location_complete and location_id not in chapter_progress["locations_completed"]:
            chapter_progress["locations_completed"].append(location_id)
            
            # Award location XP
            location_xp = location.get("rewards", {}).get("xp", 100)
            progress_doc["total_xp"] = progress_doc.get("total_xp", 0) + location_xp
            chapter_progress["xp_earned"] = chapter_progress.get("xp_earned", 0) + location_xp
        
        # Calculate chapter progress percentage
        chapter = await self.db.learning_paths.find_one({"_id": ObjectId(chapter_id)})
        if chapter:
            total_locations = len(chapter.get("locations", []))
            completed_locations = len(chapter_progress["locations_completed"])
            chapter_progress["progress_percent"] = int((completed_locations / total_locations * 100)) if total_locations > 0 else 0
        
        # Update database
        progress_doc["updated_at"] = datetime.utcnow()
        await self.db.user_progress.update_one(
            {"user_id": state.user_id},
            {"$set": progress_doc},
            upsert=True
        )
    
    async def get_user_progress(
        self,
        user_id: str,
        scenario_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get user's progress on a specific scenario"""
        # Check if user has completed this scenario
        completed_state = await self.conversation_states_collection.find_one({
            "user_id": user_id,
            "scenario_id": scenario_id,
            "status": "completed"
        })
        
        if completed_state:
            return {
                "completed": True,
                "score": completed_state.get("score", 0),
                "completed_at": completed_state.get("completed_at"),
                "attempts": await self.conversation_states_collection.count_documents({
                    "user_id": user_id,
                    "scenario_id": scenario_id
                })
            }
        
        # Check if user has an active conversation
        active_state = await self.conversation_states_collection.find_one({
            "user_id": user_id,
            "scenario_id": scenario_id,
            "status": "active"
        })
        
        if active_state:
            return {
                "completed": False,
                "in_progress": True,
                "score": active_state.get("score", 0),
                "attempts": await self.conversation_states_collection.count_documents({
                    "user_id": user_id,
                    "scenario_id": scenario_id
                })
            }
        
        return None
    
    async def get_all_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's progress on all scenarios"""
        # Get all completed scenarios
        completed_states = await self.conversation_states_collection.find({
            "user_id": user_id,
            "status": "completed"
        }).to_list(length=1000)
        
        # Get all active scenarios
        active_states = await self.conversation_states_collection.find({
            "user_id": user_id,
            "status": "active"
        }).to_list(length=1000)
        
        progress = {}
        
        # Add completed scenarios
        for state in completed_states:
            scenario_id = state.get("scenario_id")
            if scenario_id:
                progress[scenario_id] = {
                    "completed": True,
                    "best_score": state.get("score", 0),
                    "attempts": 1,
                    "current_active": False
                }
        
        # Add active scenarios
        for state in active_states:
            scenario_id = state.get("scenario_id")
            if scenario_id and scenario_id not in progress:
                progress[scenario_id] = {
                    "completed": False,
                    "best_score": state.get("score", 0),
                    "attempts": 1,
                    "current_active": True
                }
        
        return progress
