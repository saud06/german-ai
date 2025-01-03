from fastapi import APIRouter, Depends
from ..security import auth_dep
from ..db import get_db

router = APIRouter(prefix="/progress")

@router.get('/{user_id}')
async def progress(user_id: str, db=Depends(get_db), _: str = Depends(auth_dep)):
    # Aggregate minimal MVP stats
    vocab = db["vocab"]
    sessions = db["quiz_sessions"]
    mistakes = db["mistakes"]

    words_learned = await vocab.count_documents({"user_id": user_id})
    quizzes_completed = await sessions.count_documents({"user_id": user_id})
    # naive common errors for MVP
    common_errors = ["articles", "verb conjugation"]

    return {
        "user_id": user_id,
        "streak": 0,
        "words_learned": words_learned,
        "quizzes_completed": quizzes_completed,
        "common_errors": common_errors,
        "badges": ["Getting Started"],
    }

@router.get('/{user_id}/weekly')
async def weekly_activity(user_id: str, db=Depends(get_db), _: str = Depends(auth_dep)):
    """
    Return 7 integers representing activity intensity for the last 7 days (Mon->Sun style array).
    For MVP/portfolio, we return a deterministic mock based on the user's current words_learned count,
    so the UI has stable, plausible data without extra DB shape assumptions.
    """
    vocab = db["vocab"]
    words_learned = await vocab.count_documents({"user_id": user_id})
    seed = words_learned % 7
    values = [int((i + seed) % 5) for i in range(7)]
    return {"values": values}
