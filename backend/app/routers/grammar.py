from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from ..security import auth_dep
from ..services.ai import grammar_check
from ..db import get_db
from ..services.typing_utils import SentenceResult
from ..utils.journey_utils import get_user_journey_level, get_level_range_for_content
from typing import List, Optional

router = APIRouter(prefix="/grammar")

class GrammarRequest(BaseModel):
    user_id: str
    sentence: str

@router.post('/check')
async def grammar(payload: GrammarRequest, db=Depends(get_db), _: str = Depends(auth_dep)):
    print(f"[GRAMMAR CHECK] Checking sentence: '{payload.sentence}'")
    try:
        res = await grammar_check(db, payload.sentence)
        print(f"[GRAMMAR CHECK] Result - is_correct: {res.source == 'ok'}, corrected: '{res.corrected}'")
        return res.model_dump()
    except ValueError as e:
        print(f"[GRAMMAR CHECK] ValueError: {e}")
        # For authenticated endpoint, return a friendly OK when no issues detected by rules/AI
        ok = SentenceResult(
            original=payload.sentence,
            corrected=payload.sentence,
            explanation="No issues detected by available checks.",
            suggested_variation=payload.sentence,
            source="ok",
        )
        return ok.model_dump()
    except Exception as e:
        print(f"[GRAMMAR CHECK] Unexpected error: {e}")
        raise

class GrammarRequestPublic(BaseModel):
    user_id: str | None = None
    sentence: str

@router.post('/check-public')
async def grammar_public(payload: GrammarRequestPublic, db=Depends(get_db)):
    """
    Public grammar check endpoint that does not require authentication.
    Intended for trial/unauthenticated usage from the Grammar Coach page.
    """
    try:
        res = await grammar_check(db, payload.sentence)
        return res.model_dump()
    except ValueError:
        raise HTTPException(status_code=503, detail="No grammar service available (AI off and no DB rule matched)")

class GrammarSaveRequest(BaseModel):
    original: str
    corrected: str
    explanation: str
    suggested_variation: str

class GrammarHistoryItem(BaseModel):
    original: str
    corrected: str
    explanation: str
    suggested_variation: str
    ts: str

@router.post('/save')
async def grammar_save(payload: GrammarSaveRequest, db=Depends(get_db), user_id: str = Depends(auth_dep)):
    try:
        doc = {
            'user_id': user_id,
            'original': payload.original,
            'corrected': payload.corrected,
            'explanation': payload.explanation,
            'suggested_variation': payload.suggested_variation,
            'ts': __import__('datetime').datetime.utcnow().isoformat(),
        }
        await db['grammar_history'].insert_one(doc)
        return {'status': 'ok'}
    except Exception:
        raise HTTPException(status_code=500, detail='Failed to save grammar item')

@router.get('/history', response_model=List[GrammarHistoryItem])
async def grammar_history(limit: int = 10, db=Depends(get_db), user_id: str = Depends(auth_dep)):
    try:
        cur = db['grammar_history'].find({'user_id': user_id}).sort('ts', -1).limit(int(limit))
        items = await cur.to_list(length=limit)
        out: List[GrammarHistoryItem] = []
        for it in items:
            out.append(GrammarHistoryItem(
                original=it.get('original',''),
                corrected=it.get('corrected',''),
                explanation=it.get('explanation',''),
                suggested_variation=it.get('suggested_variation',''),
                ts=str(it.get('ts','')),
            ))
        return out
    except Exception:
        return []

class ExampleItem(BaseModel):
    text: str
    source: str
    level: Optional[str] = None

@router.get('/examples', response_model=List[ExampleItem])
async def grammar_examples(
    size: int = 8, 
    level: Optional[str] = None, 
    track: Optional[str] = None,
    user_id: Optional[str] = Query(default=None),
    db=Depends(get_db)
):
    print(f"[GRAMMAR EXAMPLES] size={size}, level={level}, track={track}, user_id={user_id}")
    
    # Get user's journey level if user_id provided and no level specified
    if not level and user_id:
        journey_level = await get_user_journey_level(db, user_id)
        if journey_level:
            level = journey_level
            print(f"[GRAMMAR EXAMPLES] Using journey level: {level}")
    
    out: List[ExampleItem] = []
    try:
        # From seed_words examples - use exact level only
        match_stage = { 'examples': { '$type': 'array', '$ne': [] } }
        if level:
            # Use exact level match (B1 users see only B1 sentences)
            match_stage = { '$and': [match_stage, { 'level': level.upper() }] }
            print(f"[GRAMMAR EXAMPLES] Filtering by level: {level.upper()}")
        
        cursor = db['seed_words'].aggregate([
            { '$match': match_stage },
            { '$project': { 
                'ex': { '$arrayElemAt': [ '$examples', 0 ] },
                'level': 1
            } },
            { '$match': { 'ex': { '$type': 'string' } } },
            { '$sample': { 'size': int(size) } },
        ])
        items = await cursor.to_list(length=size)
        for it in items:
            t = (it.get('ex') or '').strip()
            if t:
                out.append(ExampleItem(
                    text=t, 
                    source='vocabulary',
                    level=it.get('level')
                ))
        
        print(f"[GRAMMAR EXAMPLES] Found {len(out)} examples from seed_words")
        
        # If not enough examples, get from quizzes (without level filtering for now)
        if len(out) < size:
            remain = size - len(out)
            q_match = { 'txt': { '$type': 'string' } }
            if track:
                q_match = { '$and': [ q_match, { 'questions.skills': track } ] }
            qitems = await db['quizzes'].aggregate([
                { '$unwind': '$questions' },
                { '$project': { 'txt': { '$ifNull': [ '$questions.sentence', '$questions.question' ] } } },
                { '$match': q_match },
                { '$sample': { 'size': int(remain) } },
            ]).to_list(length=remain)
            for it in qitems:
                t = (it.get('txt') or '').strip()
                if t:
                    out.append(ExampleItem(text=t, source='quiz', level=level))
            print(f"[GRAMMAR EXAMPLES] Added {len(qitems)} examples from quizzes")
    except Exception as e:
        print(f"[GRAMMAR EXAMPLES] Error: {e}")
        pass
    
    if not out:
        return []
    return out[: size]

# --- Micro-exercises ---
class MicroExercise(BaseModel):
    id: str
    type: str  # 'fill_in' | 'mcq'
    prompt: str
    options: List[str] | None = None
    answer: str

class MicroRequest(BaseModel):
    original: str
    corrected: str
    explanation: str | None = None
    rule_id: str | None = None

def _align_words_local(a: str, b: str) -> List[dict]:
    import re
    A = [t for t in re.findall(r"[\wäöüÄÖÜß]+", a or "", flags=re.UNICODE)]
    B = [t for t in re.findall(r"[\wäöüÄÖÜß]+", b or "", flags=re.UNICODE)]
    m, n = len(A), len(B)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i
    for j in range(n+1): dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = 0 if A[i-1].lower() == B[j-1].lower() else 1
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    out = []
    i, j = m, n
    while i > 0 or j > 0:
        if i>0 and j>0 and dp[i][j] == dp[i-1][j-1] + (0 if A[i-1].lower()==B[j-1].lower() else 1):
            op = 'ok' if A[i-1].lower()==B[j-1].lower() else 'sub'
            out.append({'op': op, 'before': A[i-1], 'after': B[j-1]})
            i -= 1; j -= 1
        elif i>0 and dp[i][j] == dp[i-1][j] + 1:
            out.append({'op': 'del', 'before': A[i-1]}); i -= 1
        else:
            out.append({'op': 'ins', 'after': B[j-1]}); j -= 1
    out.reverse()
    return out

@router.post('/micro', response_model=List[MicroExercise])
async def grammar_micro(payload: MicroRequest):
    """Generate a few micro-exercises from the provided correction.
    Heuristics only (no AI): we blank changed tokens and add simple distractors.
    """
    original = (payload.original or '').strip()
    corrected = (payload.corrected or '').strip()
    if not original or not corrected:
        return []
    aligned = _align_words_local(original, corrected)
    # Collect changed target tokens from 'sub' or 'ins' (prefer 'after')
    targets: List[str] = []
    for t in aligned:
        if t.get('op') in ('sub','ins') and t.get('after'):
            token = str(t.get('after'))
            if token not in targets:
                targets.append(token)
    # If nothing changed, create a single fill-in with a common token
    if not targets:
        import re
        toks = re.findall(r"[\wäöüÄÖÜß]+", corrected)
        if toks:
            targets = [toks[0]]
    exercises: List[MicroExercise] = []

    def make_distractors(tok: str) -> List[str]:
        low = tok.lower()
        if low in ('der','die','das','den','dem','des'):
            base = ['Der','Die','Das','Den','Dem']
            opts = [o for o in base if o.lower()!=low]
            return opts[:2]
        # naive verb endings set
        endings = [('e','st'),('e','t'),('e','en'),('st','t'),('t','en')]
        ds = set()
        for a,b in endings:
            if low.endswith(a): ds.add(low[:-len(a)]+b)
        # some common variants
        for suf in ('e','st','t','en'):
            ds.add(low[:-1]+suf if len(low)>1 else low+suf)
        out = [s for s in ds if s != low]
        # capitalize if original is capitalized
        if tok and tok[0].isupper():
            out = [s.capitalize() for s in out]
        return out[:3]

    # Build fill-in exercises
    import re as _re
    words = _re.findall(r"\S+", corrected)
    for i, tok in enumerate(words):
        if any(tok.strip('.,!?;:') == t for t in targets):
            blanked = words.copy()
            blanked[i] = '___'
            prompt = ' '.join(blanked)
            ex_id = f"fill_{i}"
            exercises.append(MicroExercise(id=ex_id, type='fill_in', prompt=prompt, answer=tok))
            if len(exercises) >= 3:
                break

    # Add one or two MCQs for article or verb choice
    for t in targets[:2]:
        opts = [t]
        opts += make_distractors(t)
        # ensure unique and 3 options minimum
        opts = list(dict.fromkeys(opts))
        if len(opts) < 3:
            continue
        # shuffle deterministic by id (avoid importing random; stable order is okay)
        # Just rotate list
        opts = opts[-1:] + opts[:-1]
        prompt = f"Choose the correct form for: {t}"
        exercises.append(MicroExercise(id=f"mcq_{t}", type='mcq', prompt=prompt, options=opts, answer=t))
        if len(exercises) >= 5:
            break

    return exercises[:5]
