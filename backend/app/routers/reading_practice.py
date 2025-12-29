"""
Reading Practice Router
German articles and stories with comprehension questions
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..db import get_db
from .auth import get_current_user

router = APIRouter(prefix="/reading", tags=["Reading Practice"])


class ReadingArticle(BaseModel):
    """Reading article model"""
    id: str
    title: str
    content: str
    level: str
    category: str
    word_count: int
    reading_time: int  # minutes
    vocabulary_highlights: List[dict]


class ComprehensionQuestion(BaseModel):
    """Comprehension question"""
    id: str
    question: str
    options: List[str]
    correct_answer: str


class ReadingSubmission(BaseModel):
    """User's answers to comprehension questions"""
    article_id: str
    answers: dict  # question_id: answer


class ReadingResult(BaseModel):
    """Result of reading comprehension"""
    score: int
    total_questions: int
    correct_answers: int
    xp_earned: int
    feedback: List[dict]


# Reading articles database
READING_ARTICLES = [
    {
        "id": "ra_001",
        "title": "Ein Tag in Berlin",
        "content": """Berlin ist die Hauptstadt von Deutschland. Die Stadt hat etwa 3,7 Millionen Einwohner. 
        Berlin ist bekannt für seine Geschichte, Kultur und Kunst. Viele Touristen besuchen das Brandenburger Tor, 
        die Berliner Mauer und das Reichstagsgebäude. In Berlin gibt es auch viele Parks und Seen. 
        Die Stadt ist sehr international und multikulturell. Man kann hier Menschen aus der ganzen Welt treffen.""",
        "level": "A2",
        "category": "culture",
        "word_count": 65,
        "reading_time": 2,
        "vocabulary_highlights": [
            {"word": "Hauptstadt", "translation": "capital", "level": "A2"},
            {"word": "Einwohner", "translation": "inhabitants", "level": "A2"},
            {"word": "bekannt", "translation": "famous", "level": "A2"},
        ],
        "questions": [
            {
                "id": "q1",
                "question": "Wie viele Einwohner hat Berlin?",
                "options": ["2,7 Millionen", "3,7 Millionen", "4,7 Millionen"],
                "correct_answer": "3,7 Millionen"
            },
            {
                "id": "q2",
                "question": "Was können Touristen in Berlin besuchen?",
                "options": ["Nur Parks", "Brandenburger Tor und Berliner Mauer", "Nur Museen"],
                "correct_answer": "Brandenburger Tor und Berliner Mauer"
            },
        ]
    },
    {
        "id": "ra_002",
        "title": "Deutsches Essen",
        "content": """Die deutsche Küche ist sehr vielfältig. Jede Region hat ihre eigenen Spezialitäten. 
        Im Süden isst man gerne Schweinshaxe und Knödel. Im Norden sind Fischgerichte sehr beliebt. 
        Bratwurst und Sauerkraut sind in ganz Deutschland bekannt. Zum Frühstück essen viele Deutsche 
        Brötchen mit Marmelade oder Käse. Bier ist das beliebteste Getränk in Deutschland. 
        Es gibt über 1.300 Brauereien im Land.""",
        "level": "A2",
        "category": "food",
        "word_count": 60,
        "reading_time": 2,
        "vocabulary_highlights": [
            {"word": "vielfältig", "translation": "diverse", "level": "B1"},
            {"word": "Spezialitäten", "translation": "specialties", "level": "A2"},
            {"word": "beliebt", "translation": "popular", "level": "A2"},
        ],
        "questions": [
            {
                "id": "q1",
                "question": "Was isst man im Süden Deutschlands?",
                "options": ["Fischgerichte", "Schweinshaxe und Knödel", "Nur Brot"],
                "correct_answer": "Schweinshaxe und Knödel"
            },
            {
                "id": "q2",
                "question": "Wie viele Brauereien gibt es in Deutschland?",
                "options": ["Über 1.300", "Über 500", "Über 2.000"],
                "correct_answer": "Über 1.300"
            },
        ]
    },
    {
        "id": "ra_003",
        "title": "Umweltschutz in Deutschland",
        "content": """Deutschland ist führend im Umweltschutz. Das Land investiert viel in erneuerbare Energien. 
        Windkraft und Solarenergie sind sehr wichtig. Viele Deutsche trennen ihren Müll in verschiedene Kategorien: 
        Papier, Plastik, Glas und Biomüll. Das Recycling-System ist sehr effizient. 
        In vielen Städten gibt es Fahrradwege und öffentliche Verkehrsmittel sind gut ausgebaut. 
        Die Regierung hat das Ziel, bis 2045 klimaneutral zu sein.""",
        "level": "B1",
        "category": "environment",
        "word_count": 70,
        "reading_time": 3,
        "vocabulary_highlights": [
            {"word": "führend", "translation": "leading", "level": "B1"},
            {"word": "erneuerbare Energien", "translation": "renewable energy", "level": "B1"},
            {"word": "klimaneutral", "translation": "climate neutral", "level": "B2"},
        ],
        "questions": [
            {
                "id": "q1",
                "question": "In welche Kategorien trennen Deutsche ihren Müll?",
                "options": [
                    "Nur Papier und Plastik",
                    "Papier, Plastik, Glas und Biomüll",
                    "Nur Glas"
                ],
                "correct_answer": "Papier, Plastik, Glas und Biomüll"
            },
            {
                "id": "q2",
                "question": "Wann möchte Deutschland klimaneutral sein?",
                "options": ["2030", "2045", "2050"],
                "correct_answer": "2045"
            },
        ]
    },
]


@router.get("/articles")
async def get_articles(
    level: Optional[str] = None,
    category: Optional[str] = None
):
    """Get reading articles"""
    articles = READING_ARTICLES
    
    # Filter by level
    if level:
        articles = [a for a in articles if a["level"] == level]
    
    # Filter by category
    if category:
        articles = [a for a in articles if a["category"] == category]
    
    # Remove questions from response
    safe_articles = []
    for article in articles:
        safe_article = article.copy()
        safe_article.pop("questions", None)
        safe_articles.append(safe_article)
    
    return {"articles": safe_articles, "total": len(safe_articles)}


@router.get("/articles/{article_id}")
async def get_article(article_id: str):
    """Get a specific article with questions"""
    article = next((a for a in READING_ARTICLES if a["id"] == article_id), None)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Remove correct answers from questions
    safe_article = article.copy()
    safe_questions = []
    for q in article.get("questions", []):
        safe_q = q.copy()
        safe_q.pop("correct_answer", None)
        safe_questions.append(safe_q)
    safe_article["questions"] = safe_questions
    
    return safe_article


@router.post("/submit", response_model=ReadingResult)
async def submit_reading(
    submission: ReadingSubmission,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Submit reading comprehension answers"""
    # Find article
    article = next((a for a in READING_ARTICLES if a["id"] == submission.article_id), None)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Check answers
    questions = article.get("questions", [])
    correct_count = 0
    feedback = []
    
    for question in questions:
        user_answer = submission.answers.get(question["id"])
        correct = user_answer == question["correct_answer"]
        
        if correct:
            correct_count += 1
        
        feedback.append({
            "question_id": question["id"],
            "question": question["question"],
            "your_answer": user_answer,
            "correct_answer": question["correct_answer"],
            "correct": correct
        })
    
    # Calculate score and XP
    total_questions = len(questions)
    score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
    xp_earned = score
    
    # Save submission
    await db["reading_submissions"].insert_one({
        "user_id": user_id,
        "article_id": submission.article_id,
        "answers": submission.answers,
        "score": score,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "timestamp": datetime.utcnow()
    })
    
    # Update user stats
    await db["user_stats"].update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "articles_read": 1,
                "total_xp": xp_earned
            }
        },
        upsert=True
    )
    
    return ReadingResult(
        score=score,
        total_questions=total_questions,
        correct_answers=correct_count,
        xp_earned=xp_earned,
        feedback=feedback
    )


@router.get("/stats")
async def get_reading_stats(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user's reading statistics"""
    # Get total articles read
    total = await db["reading_submissions"].count_documents({"user_id": user_id})
    
    # Get average score
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": None,
            "avg_score": {"$avg": "$score"}
        }}
    ]
    
    stats = await db["reading_submissions"].aggregate(pipeline).to_list(length=1)
    avg_score = stats[0]["avg_score"] if stats else 0
    
    return {
        "articles_read": total,
        "average_score": round(avg_score, 2)
    }


@router.get("/categories")
async def get_categories():
    """Get reading categories"""
    return {
        "categories": [
            {"id": "culture", "name": "Kultur"},
            {"id": "food", "name": "Essen"},
            {"id": "environment", "name": "Umwelt"},
            {"id": "technology", "name": "Technologie"},
            {"id": "history", "name": "Geschichte"},
            {"id": "travel", "name": "Reisen"},
        ]
    }
