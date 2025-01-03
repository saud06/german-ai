from fastapi import APIRouter, HTTPException, Depends
from ..config import settings, reload_settings
from ..startup import seed_collections, ensure_quiz_min
from ..db import get_db
import os, json
from ..startup import SEED_DIR
from ..config import settings
import csv
import io
import urllib.request
import time

router = APIRouter(prefix="/admin")

@router.post("/dev/reload-settings")
async def dev_reload_settings():
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    reload_settings()
    return {"status": "ok", "message": "Settings reloaded"}

@router.post("/dev/seed")
async def dev_seed():
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    await seed_collections()
    return {"status": "ok", "message": "Seeding triggered"}

@router.get("/dev/stats")
async def dev_stats(db=Depends(get_db)):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    seed_words = await db["seed_words"].count_documents({})
    quizzes_docs = await db["quizzes"].count_documents({})
    # total question count
    agg = await db['quizzes'].aggregate([
        {"$project": {"count": {"$size": {"$ifNull": ["$questions", []]}}}},
        {"$group": {"_id": None, "total": {"$sum": "$count"}}}
    ]).to_list(1)
    total_questions = int((agg[0]["total"]) if agg else 0)
    grammar_rules = await db["grammar_rules"].count_documents({})
    return {
        "seed_words": seed_words,
        "quizzes_docs": quizzes_docs,
        "quiz_questions_total": total_questions,
        "grammar_rules": grammar_rules,
    }

@router.post("/dev/cleanup-source")
async def dev_cleanup_source(db=Depends(get_db)):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    # Remove top-level 'source' in seed_words and quizzes
    sw = await db["seed_words"].update_many({"source": {"$exists": True}}, {"$unset": {"source": ""}})
    qz = await db["quizzes"].update_many({"source": {"$exists": True}}, {"$unset": {"source": ""}})
    # Also ensure nested questions do not have a 'source' (unlikely in current data, but safe)
    # This requires rewriting documents if found
    fixed_nested = 0
    async for doc in db["quizzes"].find({"questions.source": {"$exists": True}}):
        qs = doc.get("questions", [])
        changed = False
        for q in qs:
            if isinstance(q, dict) and "source" in q:
                q.pop("source", None)
                changed = True
        if changed:
            await db["quizzes"].update_one({"_id": doc["_id"]}, {"$set": {"questions": qs}})
            fixed_nested += 1
    return {
        "seed_words_unset": sw.modified_count,
        "quizzes_unset": qz.modified_count,
        "quizzes_nested_fixed": fixed_nested,
    }

@router.post("/dev/cleanup-synthetic-quizzes")
async def dev_cleanup_synthetic_quizzes(reseed: bool = True, db=Depends(get_db)):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    # Remove quizzes created by the old synthetic top-up step (ids like 'quiz_syn_*')
    res = await db["quizzes"].delete_many({"_id": {"$regex": r"^quiz_syn_"}})
    removed = res.deleted_count
    if reseed:
        # After removal, trigger seeding which will now top-up using real-world questions
        await seed_collections()
    # Return current totals
    # total question count after reseed
    agg = await db['quizzes'].aggregate([
        {"$project": {"count": {"$size": {"$ifNull": ["$questions", []]}}}},
        {"$group": {"_id": None, "total": {"$sum": "$count"}}}
    ]).to_list(1)
    total_questions = int((agg[0]["total"]) if agg else 0)
    return {"removed_docs": removed, "reseeded": bool(reseed), "quiz_questions_total": total_questions}

@router.post("/dev/ensure-quiz-min")
async def dev_ensure_quiz_min(min_total: int = 100):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    if min_total < 1:
        raise HTTPException(status_code=400, detail="min_total must be >= 1")
    result = await ensure_quiz_min(min_total=min_total)
    return result

def _load_word_bank_from_project() -> list[dict]:
    # Load from project-level seed file to get richer examples
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'seed', 'word_bank_large.json')
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def _make_article_question(entry: dict, idx: int) -> dict | None:
    word = entry.get('word', '')
    example = entry.get('example') or ''
    parts = word.split()
    if len(parts) < 2:
        return None
    art, noun = parts[0].lower(), " ".join(parts[1:])
    if art not in ("der", "die", "das"):
        return None
    sentence = example or ''
    if sentence:
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

def _make_verb_question(sentence: str, idx: int, level: str = "A1") -> dict | None:
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
        "level": level,
    }

def _split_article_noun(word: str) -> tuple[str|None, str]:
    parts = (word or '').split()
    if len(parts) >= 2 and parts[0].lower() in ("der","die","das"):
        return parts[0].lower(), " ".join(parts[1:])
    return None, word or ''

def _make_noun_translation_mcq(entry: dict, idx: int, distractors: list[str]) -> dict | None:
    de = entry.get('word') or ''
    en = entry.get('translation') or ''
    if not de or not en:
        return None
    # pick two distinct distractors
    opts = [en]
    for d in distractors:
        if d and d != en and d not in opts:
            opts.append(d)
        if len(opts) >= 3:
            break
    if len(opts) < 3:
        return None
    import random
    random.shuffle(opts)
    return {
        "id": f"rw_n_{idx}",
        "type": "mcq",
        "question": f"Was bedeutet '{de}'?",
        "options": opts,
        "answer": en,
        "skills": ["nouns"],
        "level": entry.get("level", "A1"),
    }

def _definite_article(gender: str, case: str) -> str:
    tbl = {
        'nominative': {'m': 'der', 'f': 'die', 'n': 'das'},
        'accusative': {'m': 'den', 'f': 'die', 'n': 'das'},
        'dative': {'m': 'dem', 'f': 'der', 'n': 'dem'},
    }
    return tbl[case][gender]

def _make_cases_mcq(entry: dict, idx: int, preposition: str, req_case: str) -> dict | None:
    # Build a sentence requiring a specific case and ask for the correct article
    word = entry.get('word') or ''
    art, noun = _split_article_noun(word)
    if not art:
        return None
    gender = {'der': 'm', 'die': 'f', 'das': 'n'}[art]
    correct = _definite_article(gender, req_case)
    # distractors are the other case forms for the same gender
    cases = ['nominative', 'accusative', 'dative']
    options = []
    for c in cases:
        options.append(_definite_article(gender, c))
    # de-duplicate and shuffle
    options = list(dict.fromkeys(options))
    import random
    random.shuffle(options)
    # Template sentence
    sentence = f"{preposition} ____ {noun}"
    return {
        "id": f"rw_case_{idx}",
        "type": "mcq",
        "question": sentence,
        "options": options,
        "answer": correct,
        "skills": ["cases"],
        "level": entry.get("level", "A1"),
    }

def _make_pluralization_mcq(entry: dict, idx: int) -> dict | None:
    # Conservative: only handle feminine nouns ending with -e => +n (Lampe -> Lampen)
    word = entry.get('word') or ''
    art, noun = _split_article_noun(word)
    if art != 'die' or not noun or not noun.endswith('e'):
        return None
    plural = noun + 'n'
    correct = f"die {plural}"
    # simple distractors
    distractors = [f"die {noun}e", f"die {noun}er"]
    options = [correct] + distractors
    import random
    random.shuffle(options)
    return {
        "id": f"rw_pl_{idx}",
        "type": "mcq",
        "question": f"Wähle die richtige Pluralform von '{word}'.",
        "options": options,
        "answer": correct,
        "skills": ["pluralization"],
        "level": entry.get("level", "A1"),
    }

@router.post("/dev/generate-quizzes")
async def dev_generate_quizzes(num_quizzes: int = 12, per_quiz: int = 6, clear_existing: bool = False, db=Depends(get_db)):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    if num_quizzes < 1 or per_quiz < 2:
        raise HTTPException(status_code=400, detail="num_quizzes>=1 and per_quiz>=2 required")
    if clear_existing:
        await db['quizzes'].delete_many({})

    bank = _load_word_bank_from_project()
    if not bank:
        raise HTTPException(status_code=400, detail="word_bank_large.json not found or empty")

    article_pool: list[dict] = []
    verb_pool: list[dict] = []
    nouns_pool: list[dict] = []
    cases_pool: list[dict] = []
    plur_pool: list[dict] = []
    for i, e in enumerate(bank):
        aq = _make_article_question(e, i)
        if aq:
            article_pool.append(aq)
        vq = _make_verb_question(e.get('example') or '', i, level=e.get('level', 'A1'))
        if vq:
            verb_pool.append(vq)
        # nouns translation
        nouns_pool.append(e)
    # build nouns MCQs with distractors from translations
    translations = [it.get('translation') or '' for it in bank if (it.get('translation') or '')]
    built_nouns: list[dict] = []
    for i, e in enumerate(bank):
        qn = _make_noun_translation_mcq(e, i, distractors=translations)
        if qn:
            built_nouns.append(qn)
    nouns_pool = built_nouns

    # cases: use prepositions with fixed case
    PREP_CASES = [
        ("mit", "dative"), ("zu", "dative"), ("bei", "dative"), ("aus", "dative"), ("nach", "dative"), ("von", "dative"),
        ("für", "accusative"), ("ohne", "accusative"), ("gegen", "accusative"), ("um", "accusative"),
    ]
    for i, e in enumerate(bank):
        prep, req = PREP_CASES[i % len(PREP_CASES)]
        qc = _make_cases_mcq(e, i, prep, req)
        if qc:
            cases_pool.append(qc)

    # pluralization pool (conservative)
    for i, e in enumerate(bank):
        qp = _make_pluralization_mcq(e, i)
        if qp:
            plur_pool.append(qp)

    pools = [("articles", article_pool), ("verbs", verb_pool), ("nouns", nouns_pool), ("cases", cases_pool), ("pluralization", plur_pool)]
    if not any(p for _, p in pools):
        raise HTTPException(status_code=400, detail="No questions could be generated from the word bank")

    docs: list[dict] = []
    pool_idx = 0
    ts = int(time.time())
    for qi in range(num_quizzes):
        batch: list[dict] = []
        lvl = "A1"
        for _ in range(per_quiz):
            # find next non-empty pool
            chosen = None
            for _ in range(len(pools)):
                name, pool = pools[pool_idx]
                if pool:
                    chosen = (name, pool)
                    break
                pool_idx = (pool_idx + 1) % len(pools)
            if not chosen:
                break
            name, pool = chosen
            item = pool.pop(0)
            lvl = item.get("level", lvl)
            batch.append(item)
            pool_idx = (pool_idx + 1) % len(pools)
        if not batch:
            break
        track = (batch[0].get("skills") or ["mixed"])[0]
        docs.append({
            "_id": f"quiz_rw_batch_{ts}_{qi}",
            "level": lvl,
            "track": track,
            "questions": batch,
        })
    if not docs:
        raise HTTPException(status_code=400, detail="No quiz documents were built")
    await db['quizzes'].insert_many(docs)
    # stats
    total_docs = await db['quizzes'].count_documents({})
    agg = await db['quizzes'].aggregate([
        {"$project": {"count": {"$size": {"$ifNull": ["$questions", []]}}}},
        {"$group": {"_id": None, "total": {"$sum": "$count"}}}
    ]).to_list(1)
    total_questions = int((agg[0]["total"]) if agg else 0)
    return {"inserted_docs": len(docs), "total_quiz_docs": total_docs, "total_questions": total_questions, "ids": [d["_id"] for d in docs]}

@router.get("/dev/list-quizzes")
async def dev_list_quizzes(db=Depends(get_db)):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    docs = await db['quizzes'].find({}, {"_id": 1, "level": 1, "track": 1, "questions": {"$slice": 1}}).to_list(200)
    agg = await db['quizzes'].aggregate([
        {"$project": {"count": {"$size": {"$ifNull": ["$questions", []]}}}},
        {"$group": {"_id": None, "total": {"$sum": "$count"}}}
    ]).to_list(1)
    total_questions = int((agg[0]["total"]) if agg else 0)
    return {"count": len(docs), "total_questions": total_questions, "sample": docs[:5]}

@router.post("/dev/cleanup-synthetic-words")
async def dev_cleanup_synthetic_words(db=Depends(get_db)):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    # Remove words like "das Wort12" that were created by previous synthetic top-up
    # Regex for exact pattern: starts with 'das Wort' followed by digits only
    res = await db["seed_words"].delete_many({"word": {"$regex": r"^das Wort\\d+$", "$options": "i"}})
    return {"deleted": res.deleted_count}

@router.post("/dev/reset-seed-words")
async def dev_reset_seed_words(db=Depends(get_db)):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    # Danger: destructive. Clear collection and reload from seed/seed_words.json
    await db["seed_words"].delete_many({})
    path = os.path.join(SEED_DIR, 'seed_words.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list) and data:
                await db['seed_words'].insert_many(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load seed words: {e}")
    count = await db['seed_words'].count_documents({})
    return {"status": "ok", "reloaded": count}

@router.post("/dev/reset-grammar-rules")
async def dev_reset_grammar_rules(db=Depends(get_db)):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    # Danger: destructive. Clear collection and reload from seed/grammar_rules.json
    await db["grammar_rules"].delete_many({})
    path = os.path.join(SEED_DIR, 'grammar_rules.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list) and data:
                await db['grammar_rules'].insert_many(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load grammar rules: {e}")
    count = await db['grammar_rules'].count_documents({})
    return {"status": "ok", "reloaded": count}

# Minimal curated bank of real-life German words (expandable)
WORD_BANK = [
    {"level": "A1", "word": "der Tisch", "translation": "the table", "example": "Der Tisch ist groß."},
    {"level": "A1", "word": "das Haus", "translation": "the house", "example": "Ich gehe nach Hause."},
    {"level": "A1", "word": "die Schule", "translation": "the school", "example": "Ich gehe zur Schule."},
    {"level": "A1", "word": "der Stuhl", "translation": "the chair", "example": "Der Stuhl ist bequem."},
    {"level": "A1", "word": "die Lampe", "translation": "the lamp", "example": "Die Lampe ist hell."},
    {"level": "A1", "word": "das Buch", "translation": "the book", "example": "Das Buch ist interessant."},
    {"level": "A1", "word": "die Tür", "translation": "the door", "example": "Die Tür ist offen."},
    {"level": "A1", "word": "das Fenster", "translation": "the window", "example": "Das Fenster ist sauber."},
    {"level": "A1", "word": "der Apfel", "translation": "the apple", "example": "Der Apfel ist rot."},
    {"level": "A1", "word": "das Wasser", "translation": "the water", "example": "Ich trinke Wasser."},
    {"level": "A1", "word": "das Brot", "translation": "the bread", "example": "Ich esse Brot."},
    {"level": "A1", "word": "die Milch", "translation": "the milk", "example": "Die Milch ist kalt."},
    {"level": "A1", "word": "die Stadt", "translation": "the city", "example": "Die Stadt ist groß."},
    {"level": "A1", "word": "der Zug", "translation": "the train", "example": "Der Zug kommt pünktlich."},
    {"level": "A1", "word": "das Auto", "translation": "the car", "example": "Das Auto ist schnell."},
    {"level": "A1", "word": "die Straße", "translation": "the street", "example": "Die Straße ist lang."},
    {"level": "A1", "word": "die Hand", "translation": "the hand", "example": "Meine Hand ist kalt."},
    {"level": "A1", "word": "der Freund", "translation": "the friend (m)", "example": "Mein Freund heißt Max."},
    {"level": "A1", "word": "die Freundin", "translation": "the friend (f)", "example": "Meine Freundin heißt Anna."},
    {"level": "A2", "word": "die Wohnung", "translation": "the apartment", "example": "Die Wohnung ist neu."},
    {"level": "A2", "word": "der Kollege", "translation": "the colleague (m)", "example": "Mein Kollege hilft mir."},
    {"level": "A2", "word": "die Zeit", "translation": "the time", "example": "Ich habe keine Zeit."},
    {"level": "A2", "word": "das Wetter", "translation": "the weather", "example": "Das Wetter ist schön."},
    {"level": "A2", "word": "die Reise", "translation": "the trip", "example": "Die Reise dauert zwei Stunden."},
    {"level": "A2", "word": "der Urlaub", "translation": "the vacation", "example": "Ich mache Urlaub am Meer."},
    {"level": "A2", "word": "die Gesundheit", "translation": "health", "example": "Gesundheit ist wichtig."},
    {"level": "A2", "word": "der Besuch", "translation": "the visit", "example": "Wir bekommen Besuch."},
    {"level": "B1", "word": "die Herausforderung", "translation": "the challenge", "example": "Das ist eine große Herausforderung."},
    {"level": "B1", "word": "die Erfahrung", "translation": "experience", "example": "Ich habe viel Erfahrung."},
    {"level": "B1", "word": "die Verantwortung", "translation": "responsibility", "example": "Er übernimmt Verantwortung."},
    {"level": "B1", "word": "die Gesellschaft", "translation": "society", "example": "Die Gesellschaft verändert sich."},
    {"level": "B1", "word": "die Möglichkeit", "translation": "possibility", "example": "Das ist eine gute Möglichkeit."},
    {"level": "B1", "word": "die Voraussetzung", "translation": "requirement", "example": "Deutschkenntnisse sind Voraussetzung."},
    {"level": "B2", "word": "der Fortschritt", "translation": "progress", "example": "Es gibt großen Fortschritt."},
    {"level": "B2", "word": "die Nachhaltigkeit", "translation": "sustainability", "example": "Nachhaltigkeit ist wichtig."},
    {"level": "B2", "word": "die Herausforderung", "translation": "the challenge", "example": "Das stellt uns vor eine Herausforderung."},
    {"level": "B2", "word": "die Entwicklung", "translation": "development", "example": "Die Entwicklung ist positiv."},
]

@router.post("/dev/seed-random-real-words")
async def dev_seed_random_real_words(count: int = 200, db=Depends(get_db)):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    if count <= 0:
        raise HTTPException(status_code=400, detail="count must be > 0")
    # Use only curated words; cap at bank size to keep words real and unique
    items = WORD_BANK.copy()
    # Deduplicate by word
    seen = set()
    unique = []
    for it in items:
        if it["word"] in seen:
            continue
        seen.add(it["word"])
        unique.append(it)
    if count > len(unique):
        count = len(unique)
    # Clear and insert
    await db['seed_words'].delete_many({})
    docs = [{
        "level": it.get("level", "A1"),
        "word": it["word"],
        "translation": it.get("translation", ""),
        "examples": [it.get("example", "")],
    } for it in unique[:count]]
    if docs:
        await db['seed_words'].insert_many(docs)
    return {"seeded": len(docs), "cap": len(unique)}

@router.post("/dev/seed-ai-words")
async def dev_seed_ai_words(count: int = 500, level: str | None = None, db=Depends(get_db)):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not configured")
    if count <= 0:
        raise HTTPException(status_code=400, detail="count must be > 0")
    try:
        try:
            from openai import OpenAI
        except Exception:
            raise HTTPException(status_code=500, detail="openai package not installed in backend env")
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        system = (
            "You are a German language content generator. Return strictly valid JSON."
        )
        schema = {
            "level": "A1|A2|B1|B2",
            "word": "German word with article where applicable (e.g., 'der Tisch')",
            "translation": "English translation",
            "example": "A short example sentence in German using the word",
        }
        user = {
            "instruction": "Generate distinct, real-life German vocabulary entries.",
            "level": level or "A1-B2 mix",
            "count": min(1000, int(count)),
            "schema": schema,
        }
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user)},
            ],
            temperature=0.5,
        )
        content = resp.choices[0].message.content or "[]"
        try:
            data = json.loads(content)
        except Exception:
            # try bracket extraction
            s = content.find("[")
            e = content.rfind("]")
            if s != -1 and e != -1 and e > s:
                data = json.loads(content[s:e+1])
            else:
                raise HTTPException(status_code=500, detail="AI did not return valid JSON")
        if not isinstance(data, list):
            raise HTTPException(status_code=500, detail="AI response not a list")
        # Normalize and dedupe
        seen = set()
        docs = []
        for it in data:
            if not isinstance(it, dict):
                continue
            word = (it.get("word") or "").strip()
            if not word or word in seen:
                continue
            seen.add(word)
            docs.append({
                "level": (it.get("level") or (level or "A1")).strip(),
                "word": word,
                "translation": (it.get("translation") or "").strip(),
                "examples": [ (it.get("example") or "").strip() ],
            })
            if len(docs) >= count:
                break
        if not docs:
            raise HTTPException(status_code=500, detail="No usable entries from AI")
        await db['seed_words'].delete_many({})
        await db['seed_words'].insert_many(docs)
        return {"seeded": len(docs)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI seeding failed: {e}")

@router.post("/dev/seed-from-file")
async def dev_seed_from_file(filename: str = "word_bank_large.json", count: int = 500, db=Depends(get_db)):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    path = os.path.join(SEED_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found or invalid JSON: {path} ({e})")
    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="File must contain a JSON array of entries")
    # normalize & dedupe
    seen = set()
    docs = []
    for it in data:
        if not isinstance(it, dict):
            continue
        word = (it.get("word") or "").strip()
        if not word or word in seen:
            continue
        seen.add(word)
        docs.append({
            "level": (it.get("level") or "A1").strip(),
            "word": word,
            "translation": (it.get("translation") or "").strip(),
            "examples": [ (it.get("example") or "").strip() ],
        })
        if len(docs) >= count:
            break
    if not docs:
        raise HTTPException(status_code=400, detail="No valid entries in file")
    await db['seed_words'].delete_many({})
    await db['seed_words'].insert_many(docs)
    return {"seeded": len(docs), "file": filename}

@router.post("/dev/seed-from-url")
def dev_seed_from_url(url: str, count: int = 500, db=Depends(get_db)):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Not allowed in production")
    if not url:
        raise HTTPException(status_code=400, detail="url is required")
    try:
        with urllib.request.urlopen(url) as resp:
            raw = resp.read()
            ctype = resp.headers.get('Content-Type', '')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

    entries: list[dict] = []
    # Try JSON first
    try:
        text = raw.decode('utf-8')
        data = json.loads(text)
        if isinstance(data, list):
            for it in data:
                if not isinstance(it, dict):
                    continue
                entries.append(it)
    except Exception:
        # Try CSV
        try:
            text = raw.decode('utf-8')
            reader = csv.DictReader(io.StringIO(text))
            for row in reader:
                entries.append(row)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Unsupported content; expected JSON array or CSV with header: {e}")

    if not entries:
        raise HTTPException(status_code=400, detail="No entries parsed from URL")

    # Normalize and dedupe
    seen = set()
    docs = []
    for it in entries:
        if not isinstance(it, dict):
            continue
        word = (it.get('word') or it.get('term') or '').strip()
        if not word or word in seen:
            continue
        seen.add(word)
        level = (it.get('level') or 'A1').strip()
        translation = (it.get('translation') or it.get('en') or '').strip()
        example = (it.get('example') or it.get('sentence') or '').strip()
        docs.append({
            'level': level,
            'word': word,
            'translation': translation,
            'examples': [example] if example else [],
        })
        if len(docs) >= count:
            break

    if not docs:
        raise HTTPException(status_code=400, detail="No valid entries after normalization")

    # Clear and insert
    import anyio
    async def _write():
        await db['seed_words'].delete_many({})
        await db['seed_words'].insert_many(docs)
    anyio.run(_write)
    return {"seeded": len(docs), "source": url}
