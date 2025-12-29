"""
Writing Practice Router
AI-powered writing practice with feedback
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..db import get_db
from .auth import get_current_user

router = APIRouter(prefix="/writing", tags=["Writing Practice"])


class WritingPrompt(BaseModel):
    """Writing prompt model"""
    id: str
    title: str
    prompt: str
    level: str
    category: str
    word_count_min: int
    word_count_max: int
    keywords: List[str]


class WritingSubmission(BaseModel):
    """User's writing submission"""
    prompt_id: str
    text: str


class WritingFeedback(BaseModel):
    """AI feedback on writing"""
    score: int  # 0-100
    grammar_errors: List[dict]
    vocabulary_suggestions: List[dict]
    structure_feedback: str
    strengths: List[str]
    improvements: List[str]
    xp_earned: int


# Writing prompts database
WRITING_PROMPTS = [
    {
        "id": "wp_001",
        "title": "Meine Familie",
        "prompt": "Schreiben Sie über Ihre Familie. Beschreiben Sie die Personen und was sie gerne machen.",
        "level": "A1",
        "category": "personal",
        "word_count_min": 50,
        "word_count_max": 100,
        "keywords": ["Familie", "Mutter", "Vater", "Geschwister"]
    },
    {
        "id": "wp_002",
        "title": "Mein Tagesablauf",
        "prompt": "Beschreiben Sie einen typischen Tag in Ihrem Leben. Was machen Sie morgens, mittags und abends?",
        "level": "A2",
        "category": "daily_life",
        "word_count_min": 100,
        "word_count_max": 150,
        "keywords": ["aufstehen", "frühstücken", "arbeiten", "schlafen"]
    },
    {
        "id": "wp_003",
        "title": "Meine Traumreise",
        "prompt": "Wohin möchten Sie gerne reisen? Beschreiben Sie Ihr Traumziel und was Sie dort machen möchten.",
        "level": "A2",
        "category": "travel",
        "word_count_min": 100,
        "word_count_max": 200,
        "keywords": ["reisen", "Land", "Stadt", "Sehenswürdigkeiten"]
    },
    {
        "id": "wp_004",
        "title": "Ein Brief an einen Freund",
        "prompt": "Schreiben Sie einen Brief an einen Freund. Erzählen Sie, was Sie in letzter Zeit gemacht haben.",
        "level": "B1",
        "category": "correspondence",
        "word_count_min": 150,
        "word_count_max": 250,
        "keywords": ["Lieber", "Grüße", "erzählen", "Neuigkeiten"]
    },
    {
        "id": "wp_005",
        "title": "Meine Meinung zu Social Media",
        "prompt": "Was denken Sie über soziale Medien? Diskutieren Sie Vor- und Nachteile.",
        "level": "B2",
        "category": "opinion",
        "word_count_min": 200,
        "word_count_max": 300,
        "keywords": ["Vorteil", "Nachteil", "meiner Meinung nach", "einerseits"]
    },
    {
        "id": "wp_006",
        "title": "Bewerbungsschreiben",
        "prompt": "Schreiben Sie ein Bewerbungsschreiben für eine Stelle als Softwareentwickler.",
        "level": "B2",
        "category": "professional",
        "word_count_min": 200,
        "word_count_max": 300,
        "keywords": ["Bewerbung", "Qualifikation", "Erfahrung", "Anlagen"]
    },
    {
        "id": "wp_007",
        "title": "Umweltschutz",
        "prompt": "Schreiben Sie einen Essay über Umweltschutz. Was können wir tun, um die Umwelt zu schützen?",
        "level": "B2",
        "category": "essay",
        "word_count_min": 250,
        "word_count_max": 400,
        "keywords": ["Umwelt", "Klimawandel", "Nachhaltigkeit", "Maßnahmen"]
    },
    {
        "id": "wp_008",
        "title": "Eine Geschichte",
        "prompt": "Schreiben Sie eine kurze Geschichte. Sie beginnt mit: 'Es war einmal...'",
        "level": "B1",
        "category": "creative",
        "word_count_min": 150,
        "word_count_max": 300,
        "keywords": ["Geschichte", "Charakter", "Handlung", "Ende"]
    },
]


@router.get("/prompts")
async def get_prompts(
    level: Optional[str] = None,
    category: Optional[str] = None
):
    """Get writing prompts"""
    prompts = WRITING_PROMPTS
    
    # Filter by level
    if level:
        prompts = [p for p in prompts if p["level"] == level]
    
    # Filter by category
    if category:
        prompts = [p for p in prompts if p["category"] == category]
    
    return {"prompts": prompts, "total": len(prompts)}


@router.get("/categories")
async def get_categories():
    """Get writing categories"""
    return {
        "categories": [
            {"id": "personal", "name": "Persönliches"},
            {"id": "daily_life", "name": "Alltag"},
            {"id": "travel", "name": "Reisen"},
            {"id": "correspondence", "name": "Briefe"},
            {"id": "opinion", "name": "Meinung"},
            {"id": "professional", "name": "Beruflich"},
            {"id": "essay", "name": "Essay"},
            {"id": "creative", "name": "Kreativ"},
        ]
    }


@router.post("/submit", response_model=WritingFeedback)
async def submit_writing(
    submission: WritingSubmission,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Submit writing and get AI feedback"""
    # Find prompt
    prompt = next((p for p in WRITING_PROMPTS if p["id"] == submission.prompt_id), None)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Count words
    word_count = len(submission.text.split())
    
    # Basic scoring
    score = 50  # Base score
    
    # Word count check
    if word_count >= prompt["word_count_min"] and word_count <= prompt["word_count_max"]:
        score += 20
    
    # Check for keywords
    keywords_found = sum(1 for kw in prompt["keywords"] if kw.lower() in submission.text.lower())
    score += min(keywords_found * 5, 20)
    
    # Simple grammar check (in production, use AI)
    grammar_errors = []
    if "ich gehen" in submission.text.lower():
        grammar_errors.append({
            "error": "ich gehen",
            "correction": "ich gehe",
            "explanation": "Verb muss konjugiert werden"
        })
    
    # Generate feedback
    feedback = WritingFeedback(
        score=min(score, 100),
        grammar_errors=grammar_errors,
        vocabulary_suggestions=[
            {"word": "interessant", "alternative": "spannend, faszinierend"},
            {"word": "gut", "alternative": "hervorragend, ausgezeichnet"}
        ],
        structure_feedback="Ihre Struktur ist klar. Versuchen Sie, mehr Verbindungswörter zu verwenden.",
        strengths=[
            "Gute Verwendung von Vokabular",
            "Klare Satzstruktur",
            "Passende Länge"
        ],
        improvements=[
            "Mehr Verbindungswörter verwenden",
            "Komplexere Satzstrukturen ausprobieren",
            "Mehr beschreibende Adjektive nutzen"
        ],
        xp_earned=score
    )
    
    # Save submission
    await db["writing_submissions"].insert_one({
        "user_id": user_id,
        "prompt_id": submission.prompt_id,
        "text": submission.text,
        "word_count": word_count,
        "score": score,
        "timestamp": datetime.utcnow()
    })
    
    # Update user stats
    await db["user_stats"].update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "essays_written": 1,
                "total_xp": score
            }
        },
        upsert=True
    )
    
    return feedback


@router.get("/submissions")
async def get_submissions(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db),
    limit: int = 10
):
    """Get user's writing submissions"""
    submissions = await db["writing_submissions"].find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(limit).to_list(length=limit)
    
    # Convert ObjectId to string
    for sub in submissions:
        sub["_id"] = str(sub["_id"])
    
    return {"submissions": submissions, "total": len(submissions)}


@router.get("/stats")
async def get_writing_stats(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user's writing statistics"""
    # Get total submissions
    total = await db["writing_submissions"].count_documents({"user_id": user_id})
    
    # Get average score
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": None,
            "avg_score": {"$avg": "$score"},
            "total_words": {"$sum": "$word_count"}
        }}
    ]
    
    stats = await db["writing_submissions"].aggregate(pipeline).to_list(length=1)
    
    avg_score = stats[0]["avg_score"] if stats else 0
    total_words = stats[0]["total_words"] if stats else 0
    
    return {
        "total_submissions": total,
        "average_score": round(avg_score, 2),
        "total_words_written": total_words
    }
