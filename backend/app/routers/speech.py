from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, Form
from pydantic import BaseModel
from ..security import auth_dep
from ..config import settings
from ..db import get_db
from typing import List, Dict

router = APIRouter(prefix="/speech")


def _tokenize(s: str) -> List[str]:
    import re
    return [t for t in re.findall(r"[\wäöüÄÖÜß]+", (s or ""), flags=re.UNICODE)]

def _alignment_score(expected: str, transcribed: str) -> Dict:
    # Simple word-level Levenshtein and backtrace to label ops
    exp = _tokenize(expected.lower())
    hyp = _tokenize(transcribed.lower())
    m, n = len(exp), len(hyp)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if exp[i - 1] == hyp[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost  # substitution
            )
    # backtrace
    i, j = m, n
    aligned: List[Dict] = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + (0 if exp[i - 1] == hyp[j - 1] else 1):
            op = "ok" if exp[i - 1] == hyp[j - 1] else "sub"
            aligned.append({"expected": exp[i - 1], "heard": hyp[j - 1], "op": op})
            i -= 1; j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            aligned.append({"expected": exp[i - 1], "heard": None, "op": "del"})
            i -= 1
        else:
            aligned.append({"expected": None, "heard": hyp[j - 1], "op": "ins"})
            j -= 1
    aligned.reverse()
    dist = dp[m][n]
    denom = max(1, m)
    score = int(round((1 - dist / denom) * 100))
    feedback = "Great!" if score >= 90 else ("Good try — watch endings and word order." if score >= 70 else "Try again slower; focus on vowels and final consonants.")
    return {"score": score, "aligned": aligned, "feedback": feedback}

@router.post('/check')
async def speech_check(expected: str = Form(..., min_length=1), file: UploadFile = File(None), _: str = Depends(auth_dep)):
    if not file:
        raise HTTPException(status_code=400, detail="audio file is required")
    expected = expected.strip()
    
    # Try local Whisper service first
    if settings.WHISPER_HOST:
        try:
            import httpx
            data = await file.read()
            
            # Send to local Whisper service
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {'audio_file': (file.filename or 'audio.webm', data, file.content_type or 'audio/webm')}
                response = await client.post(
                    f"{settings.WHISPER_HOST}/asr",
                    files=files,
                    params={'task': 'transcribe', 'language': 'de', 'output': 'txt'}
                )
                response.raise_for_status()
                text = response.text.strip()
                
            if not text:
                raise HTTPException(status_code=500, detail="Transcription returned empty")
            
            align = _alignment_score(expected, text)
            return {
                "expected": expected,
                "transcribed": text,
                "score": align["score"],
                "feedback": align["feedback"],
                "aligned": align["aligned"],
            }
        except HTTPException:
            raise
        except Exception as e:
            # Fall through to OpenAI if local Whisper fails
            pass
    
    # Fallback to OpenAI Whisper if available
    if settings.OPENAI_API_KEY:
        try:
            try:
                from openai import OpenAI
            except Exception:
                raise HTTPException(status_code=503, detail="openai package not installed on server")
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            data = await file.read()
            import io
            audio_file = io.BytesIO(data)
            audio_file.name = file.filename or 'audio.webm'
            resp = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="de"
            )
            text = (getattr(resp, 'text', None) or getattr(resp, 'text', '') or '').strip()
            if not text:
                raise HTTPException(status_code=500, detail="Transcription failed")
            align = _alignment_score(expected, text)
            return {
                "expected": expected,
                "transcribed": text,
                "score": align["score"],
                "feedback": align["feedback"],
                "aligned": align["aligned"],
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Speech service error: {e}")
    
    # No speech service available
    raise HTTPException(status_code=503, detail="Speech transcription service not configured")

class SuggestionItem(BaseModel):
    text: str
    source: str

@router.get('/suggestions', response_model=List[SuggestionItem])
async def speech_suggestions(size: int = 10, level: str | None = None, track: str | None = None, db=Depends(get_db)):
    out: List[SuggestionItem] = []
    try:
        # From seed_words examples
        match_stage = {"ex": {"$type": "string"}}
        if level:
            match_stage = {"$and": [match_stage, {"level": level}]}
        cursor = db['seed_words'].aggregate([
            {"$project": {"ex": {"$arrayElemAt": ["$examples", 0]}}},
            {"$match": match_stage},
            {"$sample": {"size": int(size)}},
        ])
        items = await cursor.to_list(length=size)
        for it in items:
            t = (it.get('ex') or '').strip()
            if t:
                out.append(SuggestionItem(text=t, source="seed_words"))
        if len(out) < size:
            # From quizzes (question or sentence)
            remain = size - len(out)
            q_match = {"txt": {"$type": "string"}}
            if track:
                q_match = {"$and": [q_match, {"questions.skills": track}]}
            qitems = await db['quizzes'].aggregate([
                {"$unwind": "$questions"},
                {"$project": {"txt": {"$ifNull": ["$questions.sentence", "$questions.question"]}}},
                {"$match": q_match},
                {"$sample": {"size": int(remain)}},
            ]).to_list(length=remain)
            for it in qitems:
                t = (it.get('txt') or '').strip()
                if t:
                    out.append(SuggestionItem(text=t, source="quizzes"))
    except Exception:
        pass
    if not out:
        # No DB items available and we avoid static fallbacks to keep outputs authentic
        return []
    return out[: size]

class SpeechSaveRequest(BaseModel):
    expected: str
    transcribed: str
    score: int
    feedback: str

@router.post('/save')
async def speech_save(payload: SpeechSaveRequest, db=Depends(get_db), user_id: str = Depends(auth_dep)):
    try:
        doc = {
            "user_id": user_id,
            "expected": payload.expected,
            "transcribed": payload.transcribed,
            "score": int(payload.score),
            "feedback": payload.feedback,
            "ts": __import__('datetime').datetime.utcnow().isoformat(),
        }
        await db['speech_history'].insert_one(doc)
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save speech attempt")

class SpeechHistoryItem(BaseModel):
    expected: str
    transcribed: str
    score: int
    feedback: str
    ts: str

@router.get('/history', response_model=List[SpeechHistoryItem])
async def speech_history(limit: int = 10, db=Depends(get_db), user_id: str = Depends(auth_dep)):
    try:
        cur = db['speech_history'].find({"user_id": user_id}).sort("ts", -1).limit(int(limit))
        items = await cur.to_list(length=limit)
        out: List[SpeechHistoryItem] = []
        for it in items:
            out.append(SpeechHistoryItem(
                expected=it.get('expected',''),
                transcribed=it.get('transcribed',''),
                score=int(it.get('score', 0)),
                feedback=it.get('feedback',''),
                ts=str(it.get('ts','')),
            ))
        return out
    except Exception:
        return []
