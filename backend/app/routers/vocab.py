from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Any
from ..db import get_db
from ..security import auth_dep
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


@router.get("/today")
async def vocab_today(db=Depends(get_db), user_id: Optional[str] = None):
    try:
        # If user_id provided and due items exist, return the next due
        if user_id:
            due = await db["user_vocab"].find_one(
                {"user_id": user_id, "srs.due": {"$lte": _iso_now()}}, sort=[("srs.due", 1)]
            )
            if due:
                seed = await db["seed_words"].find_one({"_id": due.get("seed_id")}) if due.get("seed_id") else None
                word = seed.get("word") if seed else (due.get("word") or "")
                example = ((seed or {}).get("examples") or [None])[0]
                result = {
                    "word": str(word) if word is not None else "",
                    "level": str((seed or {}).get("level")) if (seed or {}).get("level") is not None else None,
                    "translation": str((seed or {}).get("translation")) if (seed or {}).get("translation") is not None else None,
                    "example": str(example) if example is not None else None,
                    "source": "due",
                }
                return JSONResponse(content=result)
        # fallback: random seed word (prefer A1/A2)
        pipeline = [
            {"$match": {"level": {"$in": ["A1", "A2"]}}},
            {"$sample": {"size": 1}},
            {"$project": {"_id": 0, "word": 1, "level": 1, "translation": 1, "example": {"$arrayElemAt": ["$examples", 0]}}},
        ]
        items = await db["seed_words"].aggregate(pipeline).to_list(1)
        if items:
            it = items[0]
            # Ensure no ObjectId leaks; build a clean dict explicitly
            result = {
                "word": str(it.get("word")) if it.get("word") is not None else "",
                "level": str(it.get("level")) if it.get("level") is not None else None,
                "translation": str(it.get("translation")) if it.get("translation") is not None else None,
                "example": str(it.get("example")) if it.get("example") is not None else None,
            }
            return JSONResponse(content=result)
        # final attempt: any word (DB-only)
        anyw = await db["seed_words"].find_one({}, {"_id": 0, "word": 1, "level": 1, "translation": 1, "examples": 1})
        if anyw:
            example2 = ((anyw.get("examples") or [None])[0])
            result = {
                "word": str(anyw.get("word")) if anyw.get("word") is not None else "",
                "level": str(anyw.get("level")) if anyw.get("level") is not None else None,
                "translation": str(anyw.get("translation")) if anyw.get("translation") is not None else None,
                "example": str(example2) if example2 is not None else None,
            }
            return JSONResponse(content=result)
        # No DB data available
        raise HTTPException(status_code=503, detail="No vocabulary available (database empty or unavailable)")
    except HTTPException:
        raise
    except Exception:
        # No static fallback; signal service unavailability
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
