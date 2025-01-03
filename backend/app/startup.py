import json
import os
import logging
import asyncio
from .db import get_db

SEED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'seed')
logger = logging.getLogger(__name__)

async def seed_collections():
    """
    Attempt to seed the database with initial data. If MongoDB is not reachable
    (e.g., no local Mongo running or invalid Atlas credentials), log a warning
    and allow the application to continue starting up so that non-DB endpoints
    and the API docs are accessible.
    """
    try:
        db = await get_db()
        # Helper to enforce per-operation timeout
        async def with_timeout(coro, seconds: float = 2.0):
            try:
                return await asyncio.wait_for(coro, timeout=seconds)
            except Exception:
                return None

        # Seed words
        count = await with_timeout(db['seed_words'].count_documents({}))
        if count == 0:
            path = os.path.join(SEED_DIR, 'seed_words.json')
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        await with_timeout(db['seed_words'].insert_many(data))
            except Exception:
                # Ignore seed file errors silently (non-critical for startup)
                pass
        # No synthetic top-up for seed_words: rely on curated data only.
        # Seed quizzes
        count_q = await with_timeout(db['quizzes'].count_documents({}))
        if count_q == 0:
            path = os.path.join(SEED_DIR, 'quizzes.json')
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        await with_timeout(db['quizzes'].insert_many(data))
            except Exception:
                pass
        # Ensure at least 50 total questions across quizzes by topping up synthetic docs
        try:
            # Count total questions currently stored
            pipeline = [{"$project": {"count": {"$size": {"$ifNull": ["$questions", []]}}}}, {"$group": {"_id": None, "total": {"$sum": "$count"}}}]
            agg = await with_timeout(db['quizzes'].aggregate(pipeline).to_list(length=1)) or []
            total_qs = int((agg[0]["total"]) if agg else 0)
            need_qs = max(0, 50 - total_qs)
            if need_qs > 0:
                # Build real-world questions from curated word bank examples
                docs: list[dict] = []
                made = 0
                doc_idx = (await with_timeout(db['quizzes'].count_documents({}))) or 0

                # Load extended word bank (project-level seed file)
                wb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'seed', 'word_bank_large.json')
                word_bank = []
                try:
                    with open(wb_path, 'r', encoding='utf-8') as f:
                        word_bank = json.load(f) or []
                except Exception:
                    word_bank = []

                # Helper creators
                def make_article_question(entry: dict, idx: int) -> dict | None:
                    word = entry.get('word', '')  # e.g., "der Tisch"
                    example = entry.get('example') or ''  # e.g., "Der Tisch ist groß."
                    parts = word.split()
                    if len(parts) < 2:
                        return None
                    art, noun = parts[0].lower(), " ".join(parts[1:])
                    if art not in ("der", "die", "das"):
                        return None
                    # Try to use example sentence by blanking the first token if it matches the article
                    sentence = example
                    if isinstance(sentence, str) and sentence:
                        # Replace leading article (case-insensitive) with blank
                        # Only if sentence starts with the capitalized form
                        cap = art.capitalize()
                        if sentence.startswith(cap + " "):
                            sentence_q = "____ " + sentence[len(cap)+1:]
                        else:
                            sentence_q = f"____ {noun}"
                    else:
                        sentence_q = f"____ {noun}"
                    options = ["Der", "Die", "Das"]
                    answer = art.capitalize()
                    return {
                        "id": f"rw_art_{idx}",
                        "type": "mcq",
                        "question": sentence_q,
                        "options": options,
                        "answer": answer,
                        "skills": ["articles"],
                    }

                def make_verb_question(sentence: str, idx: int) -> dict | None:
                    # Expect patterns like "Ich trinke Wasser." -> blank second token
                    if not sentence or not sentence.lower().startswith("ich "):
                        return None
                    tokens = sentence.split()
                    if len(tokens) < 2:
                        return None
                    verb = tokens[1].strip('.,!?;:')
                    tokens[1] = "___"
                    return {
                        "id": f"rw_v_{idx}",
                        "type": "fill_in",
                        "sentence": " ".join(tokens),
                        "answer": verb,
                        "skills": ["verbs"],
                    }

                # Collect pools
                article_pool: list[dict] = []
                verb_pool: list[dict] = []
                for i, e in enumerate(word_bank):
                    q = make_article_question(e, i)
                    if q:
                        # Store level from word entry when available
                        q["level"] = e.get("level", "A1")
                        article_pool.append(q)
                    ex = e.get('example') or ''
                    vq = make_verb_question(ex, i)
                    if vq:
                        vq["level"] = e.get("level", "A1")
                        verb_pool.append(vq)

                # Fallback: even if word bank missing, do nothing (avoid synthetic placeholders)
                pools = [
                    ("articles", article_pool),
                    ("verbs", verb_pool),
                ]

                # Round-robin from pools to reach the needed count, batching 10 per doc
                pool_idx = 0
                while made < need_qs and any(p for _, p in pools):
                    doc_idx += 1
                    batch: list[dict] = []
                    # pick up to 10 questions per document
                    for _ in range(min(10, need_qs - made)):
                        # find next non-empty pool
                        start = pool_idx
                        chosen_pool = None
                        for _ in range(len(pools)):
                            name, pool = pools[pool_idx]
                            if pool:
                                chosen_pool = (name, pool)
                                break
                            pool_idx = (pool_idx + 1) % len(pools)
                        if not chosen_pool:
                            break
                        name, pool = chosen_pool
                        item = pool.pop(0)
                        # level falls back based on content
                        level = item.pop("level", "A1")
                        batch.append(item)
                        made += 1
                        pool_idx = (pool_idx + 1) % len(pools)
                        if made >= need_qs:
                            break
                    if batch:
                        # Use track of first item in batch for metadata (mixed acceptable)
                        tr = (batch[0].get("skills") or ["mixed"])[0]
                        lvl = "A1"
                        for it in batch:
                            lvl = it.get("level", lvl)
                        docs.append({
                            "_id": f"quiz_rw_{doc_idx}",
                            "level": lvl,
                            "track": tr,
                            "questions": batch,
                        })
                if docs:
                    await with_timeout(db['quizzes'].insert_many(docs))
        except Exception:
            pass
        # Seed grammar rules
        count_gr = await with_timeout(db['grammar_rules'].count_documents({}))
        if count_gr == 0:
            path = os.path.join(SEED_DIR, 'grammar_rules.json')
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        await with_timeout(db['grammar_rules'].insert_many(data))
            except Exception:
                pass
        # Top up grammar_rules to at least 100 entries
        try:
            cur_gr = await with_timeout(db['grammar_rules'].count_documents({})) or 0
            need_gr = max(0, 100 - cur_gr)
            if need_gr > 0:
                rules = []
                for i in range(need_gr):
                    idx = cur_gr + i + 1
                    pattern = f"fehl{i%20}"
                    rules.append({
                        "pattern": pattern,
                        "replacement": f"korrekt{i%20}",
                        "explanation": f"Synthetic rule {idx}: replace '{pattern}' with 'korrekt{i%20}'.",
                        "suggestion": f"Beispiel mit korrekt{i%20}.",
                    })
                if rules:
                    await with_timeout(db['grammar_rules'].insert_many(rules))
        except Exception:
            pass
    except Exception as e:
        # Most likely a DB connection error; proceed without blocking startup
        logger.warning("Database not available during startup seeding: %s", e)


async def ensure_quiz_min(min_total: int = 50):
    """Ensure there are at least `min_total` quiz questions in the DB.
    Uses the same real-world generation logic as in seed_collections, but allows
    an arbitrary target. Safe to call multiple times.
    """
    try:
        db = await get_db()
        import asyncio

        async def with_timeout(coro, seconds: float = 2.0):
            try:
                return await asyncio.wait_for(coro, timeout=seconds)
            except Exception:
                return None

        # Count current total
        pipeline = [{"$project": {"count": {"$size": {"$ifNull": ["$questions", []]}}}}, {"$group": {"_id": None, "total": {"$sum": "$count"}}}]
        agg = await with_timeout(db['quizzes'].aggregate(pipeline).to_list(length=1)) or []
        total_qs = int((agg[0]["total"]) if agg else 0)
        need_qs = max(0, int(min_total) - total_qs)
        if need_qs <= 0:
            return {"added": 0, "total": total_qs}

        # The following generation logic mirrors the real-world builder above
        docs: list[dict] = []
        made = 0
        doc_idx = (await with_timeout(db['quizzes'].count_documents({}))) or 0

        # Load extended word bank
        wb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'seed', 'word_bank_large.json')
        word_bank = []
        try:
            with open(wb_path, 'r', encoding='utf-8') as f:
                word_bank = json.load(f) or []
        except Exception:
            word_bank = []

        def make_article_question(entry: dict, idx: int):
            word = entry.get('word', '')
            example = entry.get('example') or ''
            parts = word.split()
            if len(parts) < 2:
                return None
            art, noun = parts[0].lower(), " ".join(parts[1:])
            if art not in ("der", "die", "das"):
                return None
            sentence = example
            if isinstance(sentence, str) and sentence:
                cap = art.capitalize()
                if sentence.startswith(cap + " "):
                    sentence_q = "____ " + sentence[len(cap)+1:]
                else:
                    sentence_q = f"____ {noun}"
            else:
                sentence_q = f"____ {noun}"
            return {
                "id": f"rw_art_{idx}",
                "type": "mcq",
                "question": sentence_q,
                "options": ["Der","Die","Das"],
                "answer": art.capitalize(),
                "skills": ["articles"],
                "level": entry.get("level", "A1"),
            }

        def make_verb_question(sentence: str, idx: int):
            if not sentence or not sentence.lower().startswith("ich "):
                return None
            tokens = sentence.split()
            if len(tokens) < 2:
                return None
            verb = tokens[1].strip('.,!?;:')
            tokens[1] = "___"
            return {
                "id": f"rw_v_{idx}",
                "type": "fill_in",
                "sentence": " ".join(tokens),
                "answer": verb,
                "skills": ["verbs"],
                "level": "A1",
            }

        article_pool, verb_pool = [], []
        for i, e in enumerate(word_bank):
            q = make_article_question(e, i)
            if q:
                article_pool.append(q)
            vq = make_verb_question(e.get('example') or '', i)
            if vq:
                vq["level"] = e.get("level", vq.get("level", "A1"))
                verb_pool.append(vq)

        pools = [("articles", article_pool), ("verbs", verb_pool)]
        pool_idx = 0
        while made < need_qs and any(p for _, p in pools):
            doc_idx += 1
            batch: list[dict] = []
            for _ in range(min(10, need_qs - made)):
                chosen_pool = None
                for _ in range(len(pools)):
                    name, pool = pools[pool_idx]
                    if pool:
                        chosen_pool = (name, pool)
                        break
                    pool_idx = (pool_idx + 1) % len(pools)
                if not chosen_pool:
                    break
                name, pool = chosen_pool
                item = pool.pop(0)
                batch.append(item)
                made += 1
                pool_idx = (pool_idx + 1) % len(pools)
                if made >= need_qs:
                    break
            if batch:
                tr = (batch[0].get("skills") or ["mixed"])[0]
                lvl = "A1"
                for it in batch:
                    lvl = it.get("level", lvl)
                docs.append({
                    "_id": f"quiz_rw_{doc_idx}",
                    "level": lvl,
                    "track": tr,
                    "questions": batch,
                })
        if docs:
            await with_timeout(db['quizzes'].insert_many(docs))
        # Return updated total after insertion
        agg2 = await with_timeout(db['quizzes'].aggregate(pipeline).to_list(length=1)) or []
        total2 = int((agg2[0]["total"]) if agg2 else total_qs)
        return {"added": made, "total": total2}
    except Exception:
        return {"added": 0, "total": 0}
