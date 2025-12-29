import random
from typing import Dict, Any
from bson import ObjectId
from ..ai import generate_questions
from hashlib import sha1
from ..config import settings

async def get_word_of_day(db, user_id: str) -> Dict[str, Any]:
    """Return a deterministic Word of the Day per (user_id, UTC date).

    We avoid extra cache collections by selecting a stable index:
    index = hash(user_id + YYYY-MM-DD) % total_docs
    This guarantees the same word throughout the day and varies across users.
    """
    import hashlib
    from datetime import datetime, timezone

    seed = db["seed_words"]
    total = await seed.count_documents({})
    if not total:
        raise ValueError("No seed words available in database")

    # Stable key: user_id may be None; normalize
    uid = user_id or "anonymous"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    key = f"{uid}:{today}".encode("utf-8")
    idx = int.from_bytes(hashlib.sha256(key).digest()[:8], "big") % total

    cursor = seed.find({}, {"_id": 0}).skip(idx).limit(1)
    docs = await cursor.to_list(length=1)
    if not docs:
        # Fallback to sampling if skip failed due to concurrent changes
        doc = await seed.aggregate([{ "$sample": {"size": 1}}]).to_list(1)
        docs = doc
    w = docs[0]
    return {
        "word": w.get("word", "der Tisch"),
        "translation": w.get("translation", "the table"),
        "example": (w.get("examples") or ["Der Tisch ist groß."])[0],
        "level": w.get("level", "A1"),
        # Always mark as coming from DB rather than passing through legacy labels
        "source": "db",
    }

async def get_quiz_set(db, user_id: str, track: str | None = None, size: int = 5):
    """
    DB-first: aggregate questions across all quizzes, preferring those with the
    requested `track` in their `skills`. Backfill with non-matching questions to
    reach `size`. Fall back to static only if DB returns nothing.
    """
    try:
        quizzes = db["quizzes"]

        # Single aggregation: optional match by track, sample requested size
        pipeline: list[dict] = [
            {"$unwind": "$questions"},
        ]
        if track:
            pipeline.append({"$match": {"questions.skills": track}})
        pipeline.extend([
            {"$sample": {"size": int(size)}},
            {"$replaceRoot": {"newRoot": "$questions"}},
        ])
        combined = await quizzes.aggregate(pipeline).to_list(length=size)
        # Deduplicate by id if present
        seen = set()
        deduped = []
        for q in combined:
            # Build a deterministic per-question ID if none exists.
            # Do NOT use parent document _id, as multiple questions can share it.
            existing = q.get("id")
            if existing and isinstance(existing, str):
                qid = existing
            else:
                text = q.get("question") or q.get("sentence") or ""
                opts = "|".join((q.get("options") or []))
                raw = f"{text}::{opts}"
                qid = "db_" + sha1(raw.encode("utf-8")).hexdigest()[:12]
            if qid in seen:
                continue
            seen.add(qid)
            # ensure stable shape
            q.setdefault("id", qid)
            
            # Map database fields to API schema
            if "correct_answer" in q and "answer" not in q:
                q["answer"] = q["correct_answer"]
            if "type" not in q:
                # Infer type from question structure
                if q.get("options"):
                    q["type"] = "mcq"
                else:
                    q["type"] = "fill_in"
            
            deduped.append(q)

        used_ai = False
        # If DB yielded fewer than requested, try AI top-up to reach requested size (only if enabled)
        need_after_db = int(size) - len(deduped)
        if settings.ENABLE_AI_QUIZ_TOPUP and settings.OPENAI_API_KEY and need_after_db > 0:
            ai_items = await generate_questions(track=track, size=need_after_db)
            if ai_items:
                used_ai = True
                for fq in ai_items:
                    if len(deduped) >= int(size):
                        break
                    # ensure an id for AI items as well
                    aqid = fq.get("id") or ("ai_" + sha1((fq.get("question") or fq.get("sentence") or "").encode("utf-8")).hexdigest()[:12])
                    if aqid not in seen:
                        fq.setdefault("id", aqid)
                        deduped.append(fq)
                        seen.add(aqid)

        # Return DB (+AI) items only, no shuffle to keep DB items first
        selected = deduped[: int(size)] if deduped else []
        session_id = str(ObjectId())
        await db["quiz_sessions"].insert_one({
            "_id": session_id,
            "user_id": user_id,
            "quiz_id": None,
            "questions": selected,
            "track": track,
            "size": len(selected),
        })
        if selected:
            if used_ai and len(deduped) and len(deduped) < int(size):
                # Some AI added but still fewer than requested
                source = "db+ai_topup"
            else:
                source = "db+ai_topup" if used_ai else "db"
            return {"quiz_id": session_id, "questions": selected, "source": source}
    except Exception:
        # If DB is unreachable or any error occurs, return empty (strict mode)
        pass
    # Strict mode: DB and AI only. If nothing could be retrieved/generated, return empty set.
    return {
        "quiz_id": str(ObjectId()),
        "questions": [],
        "source": "none",
    }
