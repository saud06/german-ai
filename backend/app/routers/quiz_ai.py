"""
AI-powered quiz generation endpoint for testing Mistral 7B
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from ..ai import generate_questions

router = APIRouter(prefix="/quiz-ai")

class QuizGenerateRequest(BaseModel):
    track: Optional[str] = "articles"
    size: int = 5
    level: Optional[str] = "A2"

class QuizQuestion(BaseModel):
    id: str
    type: str
    question: str
    options: List[str]
    answer: str
    skills: List[str]

class QuizGenerateResponse(BaseModel):
    questions: List[QuizQuestion]
    count: int
    source: str

@router.post('/generate', response_model=QuizGenerateResponse)
async def generate_quiz(payload: QuizGenerateRequest):
    """
    Generate quiz questions using Mistral 7B AI
    """
    questions = await generate_questions(
        track=payload.track,
        size=payload.size,
        level=payload.level
    )
    
    return {
        "questions": questions,
        "count": len(questions),
        "source": "mistral_7b" if questions else "none"
    }
