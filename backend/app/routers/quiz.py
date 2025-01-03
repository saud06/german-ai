from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta
from ..security import auth_dep
from ..db import get_db
from ..seed.utils import get_quiz_set

router = APIRouter(prefix="/quiz")

class QuizQuestion(BaseModel):
    id: str
    type: str  # mcq | fill_in
    question: Optional[str] = None
    sentence: Optional[str] = None
    options: Optional[List[str]] = None
    answer: str
    skills: Optional[List[str]] = None

class QuizStartResponse(BaseModel):
    quiz_id: str
    questions: List[QuizQuestion]
    source: str

class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: Dict[str, str]
    confidence: Optional[Dict[str, int]] = None  # 1-5 scale per question id

class QuizSubmitResponse(BaseModel):
    score: int
    total: int
    feedback: str
    weaknesses: List[str]
    per_skill: Optional[Dict[str, Dict[str, int]]] = None  # { skill: { correct, total } }

@router.get('/start', response_model=QuizStartResponse)
async def quiz_start(track: Optional[str] = None, size: int = 5, db=Depends(get_db)):
    # Public access for MVP: use a generic user id when no auth is enforced
    quiz = await get_quiz_set(db, user_id="anonymous", track=track, size=size)
    return quiz

@router.get('/start-public', response_model=QuizStartResponse)
async def quiz_start_public(track: Optional[str] = None, size: int = 5, db=Depends(get_db)):
    """
    Public variant of the quiz start endpoint. Does not require authentication
    and uses a generic user id. If the database is unavailable, the function
    will return a static fallback quiz from get_quiz_set.
    """
    quiz = await get_quiz_set(db, user_id="anonymous", track=track, size=size)
    return quiz

@router.post('/submit', response_model=QuizSubmitResponse)
async def quiz_submit(payload: QuizSubmitRequest, db=Depends(get_db), _: str = Depends(auth_dep)):
    sessions = db["quiz_sessions"]
    session = await sessions.find_one({"_id": payload.quiz_id})
    if not session:
        # For simplicity in MVP, allow evaluating against last quiz if not found
        session = await sessions.find_one(sort=[("_id", -1)])
    questions = session.get("questions", []) if session else []
    correct = 0
    total = len(questions)
    weaknesses = []
    per_skill: Dict[str, Dict[str, int]] = {}
    for q in questions:
        qid = q["id"]
        if payload.answers.get(qid, "") == q.get("answer", None):
            correct += 1
        else:
            if q.get("type") == "mcq":
                weaknesses.append("articles")
            else:
                weaknesses.append("verb conjugation")
        # per-skill aggregation
        for sk in (q.get("skills") or []):
            if sk not in per_skill:
                per_skill[sk] = {"correct": 0, "total": 0}
            per_skill[sk]["total"] += 1
            if payload.answers.get(qid, "") == q.get("answer", None):
                per_skill[sk]["correct"] += 1
    feedback = "Great job!" if correct == total else "Keep practicing!"
    return {"score": correct, "total": total, "feedback": feedback, "weaknesses": weaknesses or ["None detected"], "per_skill": per_skill or None}

# --- Game Mode (basic) ---
class GameSessionCreate(BaseModel):
    track: Optional[str] = None
    size: int = 5
    time_limit: int = 60  # seconds

class GameSession(BaseModel):
    session_id: str
    questions: List[QuizQuestion]
    time_limit: int
    started_at: float  # epoch seconds

@router.post('/session', response_model=GameSession)
async def create_game_session(payload: GameSessionCreate, db=Depends(get_db)):
    quiz = await get_quiz_set(db, user_id="anonymous", track=payload.track, size=payload.size)
    session_id = f"game_{quiz['quiz_id']}"
    now = datetime.now(timezone.utc)
    # Store game session metadata
    await db["quiz_sessions"].update_one(
        {"_id": session_id},
        {"$set": {
            "_id": session_id,
            "mode": "game",
            "questions": quiz["questions"],
            "time_limit": payload.time_limit,
            "started_at": now.isoformat(),
        }},
        upsert=True,
    )
    return {
        "session_id": session_id,
        "questions": quiz["questions"],
        "time_limit": payload.time_limit,
        "started_at": now.timestamp(),
    }

class GameAnswer(BaseModel):
    session_id: str
    question_id: str
    answer: str

class GameAnswerResult(BaseModel):
    correct: bool
    remaining_time: int
    score_delta: int

@router.post('/answer', response_model=GameAnswerResult)
async def answer_game_question(payload: GameAnswer, db=Depends(get_db)):
    sessions = db["quiz_sessions"]
    session = await sessions.find_one({"_id": payload.session_id})
    if not session:
        return {"correct": False, "remaining_time": 0, "score_delta": 0}
    # compute remaining time
    tl = int(session.get("time_limit", 60))
    try:
        started = datetime.fromisoformat(session.get("started_at"))
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
    except Exception:
        started = datetime.now(timezone.utc)
    elapsed = int((datetime.now(timezone.utc) - started).total_seconds())
    remaining = max(0, tl - elapsed)
    # find question
    q = next((qq for qq in (session.get("questions") or []) if qq.get("id") == payload.question_id), None)
    correct = bool(q and payload.answer == q.get("answer"))
    score_delta = 10 if correct else 0
    return {"correct": correct, "remaining_time": remaining, "score_delta": score_delta}
