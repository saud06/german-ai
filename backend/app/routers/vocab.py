from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Any
from ..db import get_db
from ..security import auth_dep
from ..services.vocab_ai_service import VocabAIService
import datetime as dt
import re

router = APIRouter(prefix="/vocab")


def _iso_now() -> str:
    return dt.datetime.utcnow().isoformat()


def _srs_update(ease: float, interval: int, reps: int, grade: int) -> tuple[float, int, int]:
    # Simple SM-2 style adjustments
    ease = max(1.3, ease + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)))
    if grade < 3:
        return ease, 1, 0
    reps += 1
    if reps == 1:
        interval = 1
    elif reps == 2:
        interval = 6
    else:
        interval = int(round(interval * ease))
    return ease, interval, reps


def _due_date_from(days: int) -> str:
    return (dt.datetime.utcnow() + dt.timedelta(days=days)).isoformat()


class SaveRequest(BaseModel):
    user_id: Optional[str] = None
    word: Optional[str] = None
    seed_id: Optional[str] = None
    status: Optional[str] = "learning"  # learning|known


class MarkCompleteRequest(BaseModel):
    word: str
    date: str


@router.get("/today")
async def vocab_today(db=Depends(get_db), user_id: Optional[str] = None):
    """
    Get today's vocabulary word - now AI-powered with smart caching
    Returns a single word for backward compatibility
    """
    try:
        # Use AI service to generate daily words
        vocab_ai = VocabAIService(db)
        
        # Generate 10 words for the day (cached), return first one
        words = await vocab_ai.generate_daily_words(level="A1", count=10, user_id=user_id)
        
        if words:
            word = words[0]
            result = {
                "word": str(word.get("word", "")),
                "level": str(word.get("level", "A1")),
                "translation": str(word.get("translation", "")),
                "example": str(word.get("example", "")),
                "source": word.get("source", "ai_generated")
            }
            return JSONResponse(content=result)
        
        # Fallback to database if AI fails
        pipeline = [
            {"$match": {"level": {"$in": ["A1", "A2"]}}},
            {"$sample": {"size": 1}},
            {"$project": {"_id": 0, "word": 1, "level": 1, "translation": 1, "example": {"$arrayElemAt": ["$examples", 0]}}},
        ]
        items = await db["seed_words"].aggregate(pipeline).to_list(1)
        if items:
            it = items[0]
            result = {
                "word": str(it.get("word", "")),
                "level": str(it.get("level", "")),
                "translation": str(it.get("translation", "")),
                "example": str(it.get("example", "")),
                "source": "database"
            }
            return JSONResponse(content=result)
        
        raise HTTPException(status_code=503, detail="No vocabulary available")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in vocab_today: {e}")
        raise HTTPException(status_code=503, detail="Vocabulary service unavailable")


@router.get("/today/batch")
async def vocab_today_batch(
    count: int = Query(default=10, ge=1, le=20),
    level: str = Query(default="A1"),
    db=Depends(get_db),
    user_id: Optional[str] = None
):
    """
    Get vocabulary words for today - same words all day, new words tomorrow
    Words are cached per day and exclude already learned vocabulary
    """
    try:
        vocab_ai = VocabAIService(db)
        words = await vocab_ai.generate_daily_words(level=level, count=count, user_id=user_id)
        
        # Format for frontend
        formatted_words = [
            {
                "word": str(w.get("word", "")),
                "level": str(w.get("level", level)),
                "translation": str(w.get("translation", "")),
                "example": str(w.get("example", "")),
                "source": w.get("source", "ai_generated")
            }
            for w in words
        ]
        
        return JSONResponse(content=formatted_words)
    except Exception as e:
        print(f"Error in vocab_today_batch: {e}")
        raise HTTPException(status_code=503, detail="Vocabulary service unavailable")


@router.get("/search")
async def vocab_search(q: str = "", level: Optional[str] = None, limit: int = 25, db=Depends(get_db)):
    term = q.strip()
    rx = re.compile(re.escape(term), re.IGNORECASE) if term else None
    criteria: dict[str, Any] = {}
    if rx:
        criteria["$or"] = [{"word": rx}, {"translation": rx}, {"examples": rx}]
    if level:
        criteria["level"] = level
    cur = db["seed_words"].find(criteria or {}).limit(int(limit))
    items = await cur.to_list(length=limit)
    out = []
    for it in items:
        out.append({
            "_id": str(it.get("_id")),
            "word": it.get("word"),
            "level": it.get("level"),
            "translation": it.get("translation"),
            "example": ((it.get("examples") or [None])[0]),
        })
    return out


@router.get("/progress/today")
async def get_vocab_progress(
    db=Depends(get_db),
    user_id: str = Depends(auth_dep)
):
    """
    Get today's vocabulary progress - which words have been completed
    """
    try:
        today = dt.datetime.utcnow().date().isoformat()
        progress_docs = await db["vocab_progress"].find({
            "user_id": user_id,
            "date": today
        }).to_list(length=100)
        
        completed_words = [doc.get("word") for doc in progress_docs if doc.get("word")]
        
        return JSONResponse(content={
            "date": today,
            "completed_words": completed_words,
            "count": len(completed_words)
        })
    except Exception as e:
        print(f"Error in get_vocab_progress: {e}")
        return JSONResponse(content={"completed_words": [], "count": 0})


@router.post("/progress/mark-complete")
async def mark_word_complete(
    payload: MarkCompleteRequest,
    db=Depends(get_db),
    user_id: str = Depends(auth_dep)
):
    """
    Mark a vocabulary word as completed for today
    """
    try:
        doc = {
            "user_id": user_id,
            "word": payload.word,
            "date": payload.date,
            "completed_at": _iso_now()
        }
        
        await db["vocab_progress"].update_one(
            {"user_id": user_id, "word": payload.word, "date": payload.date},
            {"$set": doc},
            upsert=True
        )
        
        return JSONResponse(content={"status": "ok", "word": payload.word})
    except Exception as e:
        print(f"Error in mark_word_complete: {e}")
        raise HTTPException(status_code=500, detail="Failed to save progress")


@router.post("/save")
async def vocab_save(payload: SaveRequest, db=Depends(get_db), user_id: str = Depends(auth_dep)):
    # Resolve seed
    seed = None
    if payload.seed_id:
        seed = await db["seed_words"].find_one({"_id": payload.seed_id})
    elif payload.word:
        seed = await db["seed_words"].find_one({"word": payload.word})
    if not seed and not payload.word:
        raise HTTPException(status_code=400, detail="word or seed_id required")
    doc = {
        "user_id": user_id,
        "seed_id": seed.get("_id") if seed else None,
        "word": (seed or {}).get("word") or payload.word,
        "level": (seed or {}).get("level"),
        "translation": (seed or {}).get("translation"),
        "example": ((seed or {}).get("examples") or [None])[0],
        "status": payload.status or "learning",
        "srs": {
            "ease": 2.5,
            "interval": 0,
            "repetitions": 0,
            "due": _iso_now(),
        },
        "ts": _iso_now(),
    }
    await db["user_vocab"].update_one(
        {"user_id": user_id, "word": doc["word"]}, {"$set": doc}, upsert=True
    )
    return {"status": "ok"}


@router.get("/list")
async def vocab_list(status: Optional[str] = None, limit: int = 50, db=Depends(get_db), user_id: str = Depends(auth_dep)):
    criteria: dict[str, Any] = {"user_id": user_id}
    if status == "due":
        criteria["srs.due"] = {"$lte": _iso_now()}
    elif status:
        criteria["status"] = status
    cur = db["user_vocab"].find(criteria).sort("srs.due", 1).limit(int(limit))
    docs = await cur.to_list(length=limit)
    # Build a clean, JSON-serializable list
    result: list[dict] = []
    for it in docs:
        srs = it.get("srs") or {}
        clean = {
            "_id": str(it.get("_id")) if it.get("_id") is not None else None,
            "user_id": str(it.get("user_id")) if it.get("user_id") is not None else None,
            "seed_id": str(it.get("seed_id")) if it.get("seed_id") is not None else None,
            "word": str(it.get("word")) if it.get("word") is not None else None,
            "level": str(it.get("level")) if it.get("level") is not None else None,
            "translation": str(it.get("translation")) if it.get("translation") is not None else None,
            "example": str(it.get("example")) if it.get("example") is not None else None,
            "status": str(it.get("status")) if it.get("status") is not None else None,
            "srs": {
                "ease": float(srs.get("ease", 2.5)) if srs.get("ease") is not None else 2.5,
                "interval": int(srs.get("interval", 0)) if srs.get("interval") is not None else 0,
                "repetitions": int(srs.get("repetitions", 0)) if srs.get("repetitions") is not None else 0,
                "due": str(srs.get("due")) if srs.get("due") is not None else None,
            },
            "ts": str(it.get("ts")) if it.get("ts") is not None else None,
        }
        result.append(clean)
    from fastapi.responses import JSONResponse
    return JSONResponse(content=result)


class ReviewStartRequest(BaseModel):
    size: int = 10


@router.post("/review/start")
async def review_start(payload: ReviewStartRequest, db=Depends(get_db), user_id: str = Depends(auth_dep)):
    now = _iso_now()
    due = await db["user_vocab"].find({"user_id": user_id, "srs.due": {"$lte": now}}).sort("srs.due", 1).limit(int(payload.size)).to_list(length=payload.size)
    if len(due) < payload.size:
        remain = payload.size - len(due)
        learning = await db["user_vocab"].find({"user_id": user_id, "status": "learning"}).sort("ts", -1).limit(remain).to_list(length=remain)
        pool = due + [w for w in learning if all(w.get("_id") != d.get("_id") for d in due)]
    else:
        pool = due

    def build_prompt(it: dict) -> dict:
        word = it.get("word") or ""
        translation = it.get("translation") or ""
        example = it.get("example") or ""
        # 1) example fill-in if possible
        if example and word:
            ex_q = example.replace(word, "___") if word in example else ("___ " + example)
            return {"mode": "fill_in", "prompt": ex_q, "answer": word}
        # 2) mcq with distractors from translations
        return {"mode": "mcq", "prompt": word, "options": [translation, "food", "house", "time"], "answer": translation}

    items = [{
        "id": str(it.get("_id")),
        "word": it.get("word"),
        "translation": it.get("translation"),
        "example": it.get("example"),
        "prompt": build_prompt(it),
    } for it in pool]

    return {"count": len(items), "items": items}


class ReviewResult(BaseModel):
    id: str
    grade: int  # 0-5


class ReviewSubmitRequest(BaseModel):
    results: List[ReviewResult]


@router.post("/review/submit")
async def review_submit(payload: ReviewSubmitRequest, db=Depends(get_db), user_id: str = Depends(auth_dep)):
    total = 0
    correct = 0
    for r in payload.results:
        doc = await db["user_vocab"].find_one({"_id": r.id, "user_id": user_id})
        # If _id is ObjectId type, fallback to matching by string conversion
        if not doc:
            from bson import ObjectId
            try:
                doc = await db["user_vocab"].find_one({"_id": ObjectId(r.id), "user_id": user_id})
            except Exception:
                doc = None
        if not doc:
            continue
        srs = doc.get("srs") or {"ease": 2.5, "interval": 0, "repetitions": 0}
        ease, interval, reps = _srs_update(float(srs.get("ease", 2.5)), int(srs.get("interval", 0)), int(srs.get("repetitions", 0)), int(r.grade))
        due = _due_date_from(interval)
        await db["user_vocab"].update_one({"_id": doc["_id"]}, {"$set": {"srs": {"ease": ease, "interval": interval, "repetitions": reps, "due": due}}})
        total += 1
        if r.grade >= 3:
            correct += 1
    return {"updated": total, "correct_rate": (correct / total if total else 0)}


# ============================================================================
# VOCABULARY SETS (for Learning Path Integration)
# ============================================================================

@router.get("/sets/{vocab_set_id}")
async def get_vocab_set(
    vocab_set_id: str,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Get a specific vocabulary set with user progress"""
    from bson import ObjectId
    
    # Get vocabulary set
    vocab_set = await db.vocab_sets.find_one({"_id": ObjectId(vocab_set_id)})
    if not vocab_set:
        raise HTTPException(status_code=404, detail="Vocabulary set not found")
    
    # Get user progress for this set
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    set_progress = {}
    if progress_doc:
        set_progress = progress_doc.get("vocab_set_progress", {}).get(vocab_set_id, {})
    
    # Convert ObjectId to string
    vocab_set["_id"] = str(vocab_set["_id"])
    if vocab_set.get("location_id"):
        vocab_set["location_id"] = str(vocab_set["location_id"])
    if vocab_set.get("chapter_id"):
        vocab_set["chapter_id"] = str(vocab_set["chapter_id"])
    
    return {
        "vocab_set": vocab_set,
        "progress": {
            "words_learned": set_progress.get("words_learned", 0),
            "reviews_completed": set_progress.get("reviews_completed", 0),
            "is_completed": set_progress.get("is_completed", False),
            "last_review": set_progress.get("last_review")
        }
    }


@router.post("/sets/{vocab_set_id}/learn")
async def mark_word_learned(
    vocab_set_id: str,
    word: str,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Mark a word as learned in a vocabulary set"""
    
    # Update user progress
    await db.user_progress.update_one(
        {"user_id": user_id},
        {
            "$inc": {f"vocab_set_progress.{vocab_set_id}.words_learned": 1},
            "$set": {"updated_at": dt.datetime.utcnow()}
        },
        upsert=True
    )
    
    # Also save to user_vocab for SRS
    await db.user_vocab.update_one(
        {"user_id": user_id, "word": word},
        {
            "$set": {
                "word": word,
                "status": "learning",
                "vocab_set_id": vocab_set_id,
                "srs": {
                    "ease": 2.5,
                    "interval": 0,
                    "repetitions": 0,
                    "due": _iso_now()
                },
                "updated_at": _iso_now()
            },
            "$setOnInsert": {"created_at": _iso_now()}
        },
        upsert=True
    )
    
    return {"success": True, "word": word}


@router.post("/sets/{vocab_set_id}/complete-review")
async def complete_vocab_set_review(
    vocab_set_id: str,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Mark a review session as complete for a vocabulary set"""
    from bson import ObjectId
    
    # Increment reviews completed
    await db.user_progress.update_one(
        {"user_id": user_id},
        {
            "$inc": {f"vocab_set_progress.{vocab_set_id}.reviews_completed": 1},
            "$set": {
                f"vocab_set_progress.{vocab_set_id}.last_review": dt.datetime.utcnow(),
                "updated_at": dt.datetime.utcnow()
            }
        },
        upsert=True
    )
    
    # Check if completion criteria met
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    if not progress_doc:
        return {"success": True, "completed": False}
    
    set_progress = progress_doc.get("vocab_set_progress", {}).get(vocab_set_id, {})
    
    # Get vocabulary set to check criteria
    vocab_set = await db.vocab_sets.find_one({"_id": ObjectId(vocab_set_id)})
    if vocab_set:
        criteria = vocab_set.get("completion_criteria", {})
        min_words = criteria.get("min_words_learned", 10)
        min_reviews = criteria.get("min_reviews", 1)
        
        words_learned = set_progress.get("words_learned", 0)
        reviews_completed = set_progress.get("reviews_completed", 0)
        
        if words_learned >= min_words and reviews_completed >= min_reviews:
            # Mark as completed
            await db.user_progress.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        f"vocab_set_progress.{vocab_set_id}.is_completed": True,
                        f"vocab_set_progress.{vocab_set_id}.completed_at": dt.datetime.utcnow(),
                        "updated_at": dt.datetime.utcnow()
                    }
                }
            )
            
            # Update Learning Path progress
            await _update_learning_path_for_vocab(user_id, vocab_set_id, vocab_set, db)
            
            return {"success": True, "completed": True, "xp_earned": vocab_set.get("xp_reward", 50)}
    
    return {"success": True, "completed": False}


async def _update_learning_path_for_vocab(user_id: str, vocab_set_id: str, vocab_set: dict, db):
    """Update Learning Path progress when vocabulary set is completed"""
    from bson import ObjectId
    
    # Get the location this vocab set belongs to
    location_id = vocab_set.get("location_id")
    if not location_id:
        return
    
    if isinstance(location_id, str):
        location_id = ObjectId(location_id)
    
    location = await db.locations.find_one({"_id": location_id})
    if not location:
        return
    
    chapter_id = str(location["chapter_id"])
    location_id_str = str(location_id)
    
    # Get user progress
    progress_doc = await db.user_progress.find_one({"user_id": user_id})
    if not progress_doc:
        progress_doc = {
            "user_id": user_id,
            "current_chapter": chapter_id,
            "total_xp": 0,
            "level": 1,
            "chapter_progress": {},
            "created_at": dt.datetime.utcnow(),
            "updated_at": dt.datetime.utcnow()
        }
        await db.user_progress.insert_one(progress_doc)
        progress_doc = await db.user_progress.find_one({"user_id": user_id})
    
    # Initialize chapter progress
    if "chapter_progress" not in progress_doc:
        progress_doc["chapter_progress"] = {}
    
    if chapter_id not in progress_doc["chapter_progress"]:
        progress_doc["chapter_progress"][chapter_id] = {
            "scenarios_completed": [],
            "vocab_sets_completed": [],
            "locations_completed": [],
            "progress_percent": 0,
            "xp_earned": 0
        }
    
    chapter_progress = progress_doc["chapter_progress"][chapter_id]
    
    # Add vocab set to completed list if not already there
    if "vocab_sets_completed" not in chapter_progress:
        chapter_progress["vocab_sets_completed"] = []
    
    if vocab_set_id not in chapter_progress["vocab_sets_completed"]:
        chapter_progress["vocab_sets_completed"].append(vocab_set_id)
        
        # Award XP
        xp_reward = vocab_set.get("xp_reward", 50)
        progress_doc["total_xp"] = progress_doc.get("total_xp", 0) + xp_reward
        chapter_progress["xp_earned"] = chapter_progress.get("xp_earned", 0) + xp_reward
        
        # Update level
        total_xp = progress_doc["total_xp"]
        new_level = 1
        while total_xp >= (new_level * 100):
            new_level += 1
        progress_doc["level"] = new_level
    
    # Check if location is complete (both scenario AND vocab set done)
    location_scenarios = [str(sid) for sid in location.get("scenarios", [])]
    location_vocab_set = str(location.get("vocab_set_id", ""))
    
    scenarios_done = all(
        str(sid) in chapter_progress.get("scenarios_completed", [])
        for sid in location_scenarios
    )
    vocab_done = location_vocab_set in chapter_progress.get("vocab_sets_completed", [])
    
    location_complete = scenarios_done and vocab_done
    
    if location_complete and location_id_str not in chapter_progress.get("locations_completed", []):
        if "locations_completed" not in chapter_progress:
            chapter_progress["locations_completed"] = []
        
        chapter_progress["locations_completed"].append(location_id_str)
        
        # Award location completion XP
        location_xp = location.get("rewards", {}).get("xp", 100)
        progress_doc["total_xp"] = progress_doc.get("total_xp", 0) + location_xp
        chapter_progress["xp_earned"] = chapter_progress.get("xp_earned", 0) + location_xp
    
    # Calculate chapter progress percentage
    chapter = await db.learning_paths.find_one({"_id": ObjectId(chapter_id)})
    if chapter:
        total_locations = len(chapter.get("locations", []))
        completed_locations = len(chapter_progress.get("locations_completed", []))
        chapter_progress["progress_percent"] = int((completed_locations / total_locations * 100)) if total_locations > 0 else 0
    
    # Update database
    progress_doc["updated_at"] = dt.datetime.utcnow()
    await db.user_progress.update_one(
        {"user_id": user_id},
        {"$set": progress_doc},
        upsert=True
    )
