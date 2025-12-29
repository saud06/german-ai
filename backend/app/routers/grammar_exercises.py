"""
Grammar Exercises Router
Provides structured grammar practice with exercises
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..db import get_db
from .auth import get_current_user
import random

router = APIRouter(prefix="/grammar-exercises", tags=["Grammar Exercises"])


class GrammarExercise(BaseModel):
    """Grammar exercise model"""
    id: str
    category: str  # articles, cases, verbs, adjectives, word_order
    level: str  # A1, A2, B1, B2
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    example: str


class ExerciseSubmission(BaseModel):
    """User's answer submission"""
    exercise_id: str
    user_answer: str


class ExerciseResult(BaseModel):
    """Result of exercise submission"""
    correct: bool
    correct_answer: str
    explanation: str
    xp_earned: int


# Grammar exercise database (in production, this would be in MongoDB)
GRAMMAR_EXERCISES = {
    "articles": [
        {
            "id": "art_001",
            "category": "articles",
            "level": "A1",
            "question": "___ Katze ist schwarz.",
            "options": ["der", "die", "das"],
            "correct_answer": "die",
            "explanation": "Katze ist feminin, daher 'die Katze'",
            "example": "Die Katze schläft auf dem Sofa."
        },
        {
            "id": "art_002",
            "category": "articles",
            "level": "A1",
            "question": "___ Hund bellt laut.",
            "options": ["der", "die", "das"],
            "correct_answer": "der",
            "explanation": "Hund ist maskulin, daher 'der Hund'",
            "example": "Der Hund spielt im Garten."
        },
        {
            "id": "art_003",
            "category": "articles",
            "level": "A1",
            "question": "___ Kind spielt.",
            "options": ["der", "die", "das"],
            "correct_answer": "das",
            "explanation": "Kind ist neutral, daher 'das Kind'",
            "example": "Das Kind ist glücklich."
        },
    ],
    "verbs": [
        {
            "id": "verb_001",
            "category": "verbs",
            "level": "A1",
            "question": "Ich ___ nach Hause.",
            "options": ["gehe", "gehst", "geht"],
            "correct_answer": "gehe",
            "explanation": "Mit 'ich' benutzt man 'gehe'",
            "example": "Ich gehe jeden Tag zur Arbeit."
        },
        {
            "id": "verb_002",
            "category": "verbs",
            "level": "A1",
            "question": "Du ___ Deutsch.",
            "options": ["lerne", "lernst", "lernt"],
            "correct_answer": "lernst",
            "explanation": "Mit 'du' benutzt man 'lernst'",
            "example": "Du lernst sehr schnell."
        },
        {
            "id": "verb_003",
            "category": "verbs",
            "level": "A2",
            "question": "Er ___ ein Buch.",
            "options": ["lese", "liest", "lesen"],
            "correct_answer": "liest",
            "explanation": "Mit 'er' benutzt man 'liest'",
            "example": "Er liest gerne Romane."
        },
    ],
    "cases": [
        {
            "id": "case_001",
            "category": "cases",
            "level": "A2",
            "question": "Ich gebe ___ Mann das Buch. (Dativ)",
            "options": ["der", "dem", "den"],
            "correct_answer": "dem",
            "explanation": "Dativ maskulin: 'dem Mann'",
            "example": "Ich helfe dem Mann."
        },
        {
            "id": "case_002",
            "category": "cases",
            "level": "A2",
            "question": "Ich sehe ___ Frau. (Akkusativ)",
            "options": ["der", "die", "den"],
            "correct_answer": "die",
            "explanation": "Akkusativ feminin: 'die Frau'",
            "example": "Ich kenne die Frau."
        },
    ],
    "adjectives": [
        {
            "id": "adj_001",
            "category": "adjectives",
            "level": "A2",
            "question": "Das ist ein ___ Haus.",
            "options": ["große", "großes", "großen"],
            "correct_answer": "großes",
            "explanation": "Neutrum Nominativ: 'ein großes Haus'",
            "example": "Wir haben ein großes Haus gekauft."
        },
        {
            "id": "adj_002",
            "category": "adjectives",
            "level": "A2",
            "question": "Ich habe einen ___ Hund.",
            "options": ["kleine", "kleiner", "kleinen"],
            "correct_answer": "kleinen",
            "explanation": "Maskulin Akkusativ: 'einen kleinen Hund'",
            "example": "Mein kleiner Hund ist sehr süß."
        },
    ],
    "word_order": [
        {
            "id": "wo_001",
            "category": "word_order",
            "level": "B1",
            "question": "Ordne richtig: Ich / gestern / ins Kino / gegangen / bin",
            "options": [
                "Ich bin gestern ins Kino gegangen",
                "Ich gegangen gestern ins Kino bin",
                "Ich ins Kino gestern gegangen bin"
            ],
            "correct_answer": "Ich bin gestern ins Kino gegangen",
            "explanation": "Perfekt: Subjekt + Hilfsverb + Zeit + Ort + Partizip",
            "example": "Ich bin gestern ins Kino gegangen."
        },
    ],
}


@router.get("/categories")
async def get_categories():
    """Get available grammar exercise categories"""
    return {
        "categories": [
            {"id": "articles", "name": "Artikel (der/die/das)", "level": "A1-A2"},
            {"id": "verbs", "name": "Verben", "level": "A1-B1"},
            {"id": "cases", "name": "Fälle (Nominativ, Akkusativ, Dativ)", "level": "A2-B2"},
            {"id": "adjectives", "name": "Adjektivendungen", "level": "A2-B1"},
            {"id": "word_order", "name": "Wortstellung", "level": "B1-B2"},
        ]
    }


@router.get("/exercises/{category}")
async def get_exercises(
    category: str,
    level: Optional[str] = None,
    limit: int = 10
):
    """Get grammar exercises for a category"""
    if category not in GRAMMAR_EXERCISES:
        raise HTTPException(status_code=404, detail="Category not found")
    
    exercises = GRAMMAR_EXERCISES[category]
    
    # Filter by level if specified
    if level:
        exercises = [e for e in exercises if e["level"] == level]
    
    # Limit results
    exercises = exercises[:limit]
    
    # Remove correct answer from response
    safe_exercises = []
    for ex in exercises:
        safe_ex = ex.copy()
        safe_ex.pop("correct_answer", None)
        safe_ex.pop("explanation", None)
        safe_exercises.append(safe_ex)
    
    return {"exercises": safe_exercises, "total": len(safe_exercises)}


@router.post("/submit", response_model=ExerciseResult)
async def submit_exercise(
    submission: ExerciseSubmission,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Submit an exercise answer and get feedback"""
    # Find the exercise
    exercise = None
    for category_exercises in GRAMMAR_EXERCISES.values():
        for ex in category_exercises:
            if ex["id"] == submission.exercise_id:
                exercise = ex
                break
        if exercise:
            break
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    # Check answer
    correct = submission.user_answer == exercise["correct_answer"]
    xp_earned = 10 if correct else 0
    
    # Update user stats
    if correct:
        await db["user_stats"].update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "grammar_errors_fixed": 1,
                    "total_xp": xp_earned
                }
            },
            upsert=True
        )
    
    # Log the attempt
    await db["grammar_exercise_attempts"].insert_one({
        "user_id": user_id,
        "exercise_id": submission.exercise_id,
        "category": exercise["category"],
        "user_answer": submission.user_answer,
        "correct_answer": exercise["correct_answer"],
        "correct": correct,
        "timestamp": datetime.utcnow()
    })
    
    return ExerciseResult(
        correct=correct,
        correct_answer=exercise["correct_answer"],
        explanation=exercise["explanation"],
        xp_earned=xp_earned
    )


@router.get("/stats")
async def get_exercise_stats(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user's grammar exercise statistics"""
    # Get total attempts
    total_attempts = await db["grammar_exercise_attempts"].count_documents({"user_id": user_id})
    
    # Get correct attempts
    correct_attempts = await db["grammar_exercise_attempts"].count_documents({
        "user_id": user_id,
        "correct": True
    })
    
    # Calculate accuracy
    accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Get stats by category
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$category",
            "total": {"$sum": 1},
            "correct": {"$sum": {"$cond": ["$correct", 1, 0]}}
        }}
    ]
    
    category_stats = await db["grammar_exercise_attempts"].aggregate(pipeline).to_list(length=100)
    
    return {
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "accuracy": round(accuracy, 2),
        "category_stats": category_stats
    }


@router.get("/daily-challenge")
async def get_daily_challenge():
    """Get a random daily grammar challenge"""
    # Select random category
    category = random.choice(list(GRAMMAR_EXERCISES.keys()))
    exercises = GRAMMAR_EXERCISES[category]
    
    # Select random exercise
    exercise = random.choice(exercises)
    
    # Remove answer
    safe_exercise = exercise.copy()
    safe_exercise.pop("correct_answer", None)
    safe_exercise.pop("explanation", None)
    
    return {
        "challenge": safe_exercise,
        "xp_reward": 25,
        "expires_in": "24h"
    }
