"""
Integrated Learning Path API
Combines all learning features into one unified journey
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from app.db import get_db
from app.security import auth_dep
from bson import ObjectId

router = APIRouter(prefix="/api/v1/integrated-learning", tags=["integrated-learning"])


class Activity(BaseModel):
    """Single learning activity"""
    id: str
    type: str  # scenario, vocabulary, quiz, grammar, reading, writing, review
    name: str
    description: str
    xp_reward: int
    estimated_minutes: int
    icon: str
    difficulty: str
    completed: bool = False
    progress_percent: int = 0


class LocationActivities(BaseModel):
    """All activities for a location"""
    location_id: str
    location_name: str
    location_type: str
    activities: List[Activity]
    total_activities: int
    completed_activities: int
    total_xp: int
    total_minutes: int
    completion_percent: int


class DailyLearningPath(BaseModel):
    """Recommended daily learning path"""
    date: str
    activities: List[Activity]
    total_xp: int
    total_minutes: int
    theme: str


@router.get("/location/{location_id}/activities", response_model=LocationActivities)
async def get_location_activities(
    location_id: str,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Get all available activities for a location"""
    
    # Get location
    location = await db.locations.find_one({"_id": ObjectId(location_id)})
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get user progress
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    chapter_id = str(location["chapter_id"])
    chapter_progress = progress_doc.get("chapter_progress", {}).get(chapter_id) if progress_doc else {}
    completed_scenarios = chapter_progress.get("scenarios_completed", []) if chapter_progress else []
    
    activities = []
    
    # 1. Add vocabulary activities
    vocab_sets = await db.vocab_sets.find({"category": location.get("type", "general")}).limit(1).to_list(length=1)
    for vocab_set in vocab_sets:
        activities.append(Activity(
            id=str(vocab_set["_id"]),
            type="vocabulary",
            name=vocab_set["name"],
            description=vocab_set.get("description", ""),
            xp_reward=vocab_set.get("xp_reward", 50),
            estimated_minutes=vocab_set.get("estimated_minutes", 10),
            icon="📚",
            difficulty=vocab_set.get("level", "A1"),
            completed=False  # TODO: Check if user completed
        ))
    
    # 2. Add scenarios
    for scenario_id in location.get("scenarios", []):
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if scenario:
            is_completed = str(scenario_id) in completed_scenarios
            activities.append(Activity(
                id=str(scenario["_id"]),
                type="scenario",
                name=scenario["name"],
                description=scenario.get("description", ""),
                xp_reward=scenario.get("xp_reward", 100),
                estimated_minutes=scenario.get("estimated_duration", 5),
                icon="🎭",
                difficulty=scenario.get("difficulty", "beginner"),
                completed=is_completed
            ))
    
    # 3. Add quizzes
    quizzes = await db.quizzes.find({"category": location.get("type", "general")}).limit(1).to_list(length=1)
    for quiz in quizzes:
        activities.append(Activity(
            id=str(quiz["_id"]),
            type="quiz",
            name=quiz["title"],
            description=quiz.get("description", ""),
            xp_reward=quiz.get("xp_reward", 30),
            estimated_minutes=quiz.get("time_limit_minutes", 5),
            icon="📝",
            difficulty=quiz.get("level", "A1"),
            completed=False
        ))
    
    # 4. Add grammar exercises
    grammar = await db.grammar_exercises.find({"category": location.get("type", "general")}).limit(1).to_list(length=1)
    for gram in grammar:
        activities.append(Activity(
            id=str(gram["_id"]),
            type="grammar",
            name=gram["title"],
            description=gram.get("description", ""),
            xp_reward=gram.get("xp_reward", 60),
            estimated_minutes=gram.get("estimated_minutes", 10),
            icon="🎯",
            difficulty=gram.get("level", "A1"),
            completed=False
        ))
    
    # 5. Add reading exercises
    reading = await db.reading_exercises.find({"category": location.get("type", "general")}).limit(1).to_list(length=1)
    for read in reading:
        activities.append(Activity(
            id=str(read["_id"]),
            type="reading",
            name=read["title"],
            description=read.get("description", ""),
            xp_reward=read.get("xp_reward", 40),
            estimated_minutes=read.get("estimated_minutes", 5),
            icon="📖",
            difficulty=read.get("level", "A1"),
            completed=False
        ))
    
    # Calculate totals
    completed_count = sum(1 for a in activities if a.completed)
    total_xp = sum(a.xp_reward for a in activities)
    total_minutes = sum(a.estimated_minutes for a in activities)
    completion_percent = int((completed_count / len(activities) * 100)) if activities else 0
    
    return LocationActivities(
        location_id=location_id,
        location_name=location["name"],
        location_type=location.get("type", "scenario"),
        activities=activities,
        total_activities=len(activities),
        completed_activities=completed_count,
        total_xp=total_xp,
        total_minutes=total_minutes,
        completion_percent=completion_percent
    )


@router.get("/daily-path", response_model=DailyLearningPath)
async def get_daily_learning_path(
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Get recommended daily learning path mixing all activity types"""
    from datetime import datetime
    
    # Get user progress to determine current level
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    current_chapter = progress_doc.get("current_chapter") if progress_doc else None
    
    # Get current chapter
    chapter = None
    if current_chapter:
        try:
            chapter = await db.learning_paths.find_one({"_id": ObjectId(current_chapter)})
        except:
            pass
    
    if not chapter:
        # Get first chapter
        chapter = await db.learning_paths.find_one({"path.chapter": 1})
    
    if not chapter:
        raise HTTPException(status_code=404, detail="No learning path found")
    
    activities = []
    
    # 1. Start with vocabulary review (spaced repetition)
    activities.append(Activity(
        id="review-daily",
        type="review",
        name="Daily Vocabulary Review",
        description="Review words you learned recently",
        xp_reward=25,
        estimated_minutes=5,
        icon="🔄",
        difficulty="A1",
        completed=False
    ))
    
    # 2. Learn new vocabulary
    vocab_sets = await db.vocab_sets.find().limit(1).to_list(length=1)
    if vocab_sets:
        vocab = vocab_sets[0]
        activities.append(Activity(
            id=str(vocab["_id"]),
            type="vocabulary",
            name=vocab["name"],
            description="Learn new words",
            xp_reward=50,
            estimated_minutes=10,
            icon="📚",
            difficulty="A1",
            completed=False
        ))
    
    # 3. Practice with scenario
    scenarios = await db.scenarios.find({"difficulty": "beginner"}).limit(1).to_list(length=1)
    if scenarios:
        scenario = scenarios[0]
        activities.append(Activity(
            id=str(scenario["_id"]),
            type="scenario",
            name=scenario["name"],
            description="Practice conversation",
            xp_reward=100,
            estimated_minutes=15,
            icon="🎭",
            difficulty="beginner",
            completed=False
        ))
    
    # 4. Grammar exercise
    activities.append(Activity(
        id="grammar-daily",
        type="grammar",
        name="Grammar Practice",
        description="Practice sentence structure",
        xp_reward=60,
        estimated_minutes=10,
        icon="🎯",
        difficulty="A1",
        completed=False
    ))
    
    # 5. Quiz to test knowledge
    quizzes = await db.quizzes.find().limit(1).to_list(length=1)
    if quizzes:
        quiz = quizzes[0]
        activities.append(Activity(
            id=str(quiz["_id"]),
            type="quiz",
            name=quiz["title"],
            description="Test your knowledge",
            xp_reward=30,
            estimated_minutes=5,
            icon="📝",
            difficulty="A1",
            completed=False
        ))
    
    total_xp = sum(a.xp_reward for a in activities)
    total_minutes = sum(a.estimated_minutes for a in activities)
    
    return DailyLearningPath(
        date=datetime.utcnow().date().isoformat(),
        activities=activities,
        total_xp=total_xp,
        total_minutes=total_minutes,
        theme=chapter["path"]["title"] if chapter else "Getting Started"
    )


@router.get("/all-features")
async def get_all_available_features(
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Get count of all available learning features in the system"""
    
    scenarios_count = await db.scenarios.count_documents({})
    vocab_sets_count = await db.vocab_sets.count_documents({})
    quizzes_count = await db.quizzes.count_documents({})
    grammar_count = await db.grammar_exercises.count_documents({})
    reading_count = await db.reading_exercises.count_documents({})
    
    # Get spaced repetition cards
    review_cards_count = await db.review_cards.count_documents({"user_id": user_id})
    
    return {
        "total_features": scenarios_count + vocab_sets_count + quizzes_count + grammar_count + reading_count,
        "breakdown": {
            "scenarios": scenarios_count,
            "vocabulary_sets": vocab_sets_count,
            "quizzes": quizzes_count,
            "grammar_exercises": grammar_count,
            "reading_exercises": reading_count,
            "review_cards": review_cards_count
        },
        "message": "All features are now integrated into the Learning Path!"
    }
