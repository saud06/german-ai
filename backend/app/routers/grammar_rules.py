"""
Grammar Rules Router
API endpoints for grammar rules and exercises
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..db import get_db
from ..security import auth_dep
from ..services.grammar_service import GrammarService


router = APIRouter(prefix="/grammar-rules")


class ExerciseSubmission(BaseModel):
    rule_id: str
    exercise_id: str
    user_answer: str


@router.post("/initialize")
async def initialize_grammar_rules(db=Depends(get_db)):
    """Initialize grammar rules in database (admin only)"""
    service = GrammarService(db)
    result = await service.initialize_rules()
    return result


@router.get("/")
async def get_grammar_rules(
    level: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db=Depends(get_db)
):
    """Get grammar rules with optional filtering"""
    service = GrammarService(db)
    rules = await service.get_rules(level, category, skip, limit)
    
    return {
        "rules": rules,
        "total": len(rules)
    }


@router.get("/{rule_id}")
async def get_grammar_rule(
    rule_id: str,
    db=Depends(get_db)
):
    """Get a specific grammar rule"""
    service = GrammarService(db)
    rule = await service.get_rule_by_id(rule_id)
    
    if not rule:
        raise HTTPException(status_code=404, detail="Grammar rule not found")
    
    return {"rule": rule}


@router.get("/user/progress")
async def get_user_grammar_progress(
    user_id: str = Depends(auth_dep),
    db=Depends(get_db)
):
    """Get user's grammar progress"""
    service = GrammarService(db)
    progress = await service.get_user_progress(user_id)
    
    return {
        "progress": progress,
        "total": len(progress)
    }


@router.post("/exercise/submit")
async def submit_exercise(
    submission: ExerciseSubmission,
    user_id: str = Depends(auth_dep),
    db=Depends(get_db)
):
    """Submit an exercise answer"""
    service = GrammarService(db)
    
    # Get the rule to check the answer
    rule = await service.get_rule_by_id(submission.rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Grammar rule not found")
    
    # Find the exercise
    exercise = None
    for ex in rule.get("exercises", []):
        if ex.get("id") == submission.exercise_id:
            exercise = ex
            break
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    # Check answer
    correct = submission.user_answer.strip().lower() == exercise["correct_answer"].strip().lower()
    
    # Update progress
    progress = await service.update_progress(user_id, submission.rule_id, correct)
    
    return {
        "correct": correct,
        "correct_answer": exercise["correct_answer"],
        "explanation": exercise["explanation"],
        "progress": progress
    }


@router.get("/user/recommended")
async def get_recommended_rules(
    level: str = "A1",
    user_id: str = Depends(auth_dep),
    db=Depends(get_db)
):
    """Get recommended grammar rules for user"""
    service = GrammarService(db)
    rules = await service.get_recommended_rules(user_id, level)
    
    return {
        "recommended": rules,
        "total": len(rules)
    }


@router.get("/user/stats")
async def get_grammar_stats(
    user_id: str = Depends(auth_dep),
    db=Depends(get_db)
):
    """Get user's grammar statistics"""
    service = GrammarService(db)
    stats = await service.get_stats(user_id)
    
    return stats
