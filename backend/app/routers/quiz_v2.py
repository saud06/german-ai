from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from bson import ObjectId
from ..security import auth_dep, optional_auth_dep
from ..db import get_db
from ..ai import generate_questions
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quiz-v2", tags=["quiz-v2"])

# ===== Models =====

class QuizQuestion(BaseModel):
    id: str
    type: str  # mcq | fill_blank | translation | sentence_order | listening | reading | speaking
    question: Optional[str] = None
    sentence: Optional[str] = None
    english: Optional[str] = None
    options: Optional[List[str]] = None
    scrambled_words: Optional[List[str]] = None
    audio_text: Optional[str] = None  # For listening questions
    passage: Optional[str] = None  # For reading questions
    prompt: Optional[str] = None  # For speaking questions
    expected_text: Optional[str] = None  # For speaking questions
    answer: str
    acceptable_answers: Optional[List[str]] = None
    hint: Optional[str] = None
    explanation: Optional[str] = None
    skills: Optional[List[str]] = None

class QuizConfig(BaseModel):
    topic: Optional[str] = None  # articles, verbs, cases, vocabulary, etc.
    level: Optional[str] = "intermediate"  # beginner, intermediate, advanced
    size: int = 10
    question_types: Optional[List[str]] = None  # Filter specific types

class QuizStartResponse(BaseModel):
    quiz_id: str
    questions: List[QuizQuestion]
    config: QuizConfig
    source: str  # "ai", "cache", "mixed"

class QuizAnswer(BaseModel):
    question_id: str
    user_answer: str
    time_spent: Optional[int] = None  # seconds

class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: List[QuizAnswer]

class QuestionResult(BaseModel):
    question_id: str
    correct: bool
    user_answer: str
    correct_answer: str
    explanation: str

class QuizSubmitResponse(BaseModel):
    quiz_id: str
    score: int
    total: int
    percentage: float
    results: List[QuestionResult]
    strengths: List[str]
    weaknesses: List[str]
    time_taken: Optional[int] = None

# ===== Helper Functions =====

def _create_fallback_questions(topic: Optional[str], level: str, size: int) -> List[Dict[str, Any]]:
    """Create fallback questions when AI and cache are unavailable - mixed with all 7 types"""
    fallback = [
        # MCQ
        {
            "id": "fb_1",
            "type": "mcq",
            "question": "Welcher Artikel ist richtig? ___ Buch ist interessant.",
            "options": ["Der", "Die", "Das", "Den"],
            "answer": "Das",
            "explanation": "'Buch' is neuter, so it uses 'das'",
            "skills": ["articles"]
        },
        # Listening
        {
            "id": "fb_2",
            "type": "listening",
            "audio_text": "Ich heiße Anna und ich komme aus Deutschland.",
            "question": "Where does Anna come from?",
            "options": ["France", "Germany", "Austria", "Switzerland"],
            "answer": "Germany",
            "explanation": "'Deutschland' means Germany",
            "skills": ["listening", "vocabulary"]
        },
        # Fill blank
        {
            "id": "fb_3",
            "type": "fill_blank",
            "sentence": "Ich ___ nach Berlin.",
            "answer": "gehe",
            "hint": "verb 'gehen' in present tense",
            "explanation": "First person singular of 'gehen' is 'gehe'",
            "skills": ["verbs"]
        },
        # Reading
        {
            "id": "fb_4",
            "type": "reading",
            "passage": "Peter geht jeden Morgen joggen. Er läuft im Park. Das ist gesund.",
            "question": "What does Peter do every morning?",
            "options": ["Swimming", "Jogging", "Cycling", "Walking"],
            "answer": "Jogging",
            "explanation": "'joggen' means jogging",
            "skills": ["reading", "vocabulary"]
        },
        # Translation
        {
            "id": "fb_5",
            "type": "translation",
            "english": "The cat is black",
            "answer": "Die Katze ist schwarz",
            "acceptable_answers": ["Die Katze ist schwarz", "die katze ist schwarz"],
            "explanation": "'Katze' is feminine, uses 'die'",
            "skills": ["vocabulary", "articles"]
        },
        # Speaking
        {
            "id": "fb_6",
            "type": "speaking",
            "prompt": "Say: 'Guten Tag'",
            "expected_text": "Guten Tag",
            "answer": "Guten Tag",
            "explanation": "This is a common German greeting meaning 'Good day'",
            "skills": ["speaking", "pronunciation"]
        },
        # Sentence order
        {
            "id": "fb_7",
            "type": "sentence_order",
            "scrambled_words": ["gehe", "Ich", "Schule", "zur"],
            "answer": "Ich gehe zur Schule",
            "explanation": "Subject-Verb-Object word order",
            "skills": ["word_order"]
        },
        # MCQ
        {
            "id": "fb_8",
            "type": "mcq",
            "question": "Wie heißt du?",
            "options": ["Ich heiße Maria", "Du heißt Maria", "Er heißt Maria", "Sie heißen Maria"],
            "answer": "Ich heiße Maria",
            "explanation": "Response to 'What is your name?' uses first person",
            "skills": ["verbs", "conversation"]
        },
        # Listening
        {
            "id": "fb_9",
            "type": "listening",
            "audio_text": "Guten Morgen! Wie geht es dir?",
            "question": "What greeting did you hear?",
            "options": ["Good morning", "Good evening", "Good night", "Good afternoon"],
            "answer": "Good morning",
            "explanation": "'Guten Morgen' means 'Good morning'",
            "skills": ["listening", "vocabulary"]
        },
        # Fill blank
        {
            "id": "fb_10",
            "type": "fill_blank",
            "sentence": "Der Hund ___ groß.",
            "answer": "ist",
            "hint": "verb 'sein' (to be)",
            "explanation": "Third person singular of 'sein' is 'ist'",
            "skills": ["verbs"]
        },
        # Reading
        {
            "id": "fb_11",
            "type": "reading",
            "passage": "Maria wohnt in Berlin. Sie ist Lehrerin. Jeden Tag geht sie zur Schule.",
            "question": "What is Maria's profession?",
            "options": ["Doctor", "Teacher", "Student", "Engineer"],
            "answer": "Teacher",
            "explanation": "'Lehrerin' means teacher (female)",
            "skills": ["reading", "vocabulary"]
        },
        # MCQ
        {
            "id": "fb_12",
            "type": "mcq",
            "question": "Welcher Artikel passt? ___ Frau ist nett.",
            "options": ["Der", "Die", "Das", "Den"],
            "answer": "Die",
            "explanation": "'Frau' is feminine, so it uses 'die'",
            "skills": ["articles"]
        },
        # Speaking
        {
            "id": "fb_13",
            "type": "speaking",
            "prompt": "Say: 'Ich lerne Deutsch'",
            "expected_text": "Ich lerne Deutsch",
            "answer": "Ich lerne Deutsch",
            "explanation": "This means 'I am learning German'",
            "skills": ["speaking", "pronunciation"]
        },
        # Translation
        {
            "id": "fb_14",
            "type": "translation",
            "english": "The house is big",
            "answer": "Das Haus ist groß",
            "acceptable_answers": ["Das Haus ist groß", "das haus ist groß"],
            "explanation": "'Haus' is neuter, uses 'das'",
            "skills": ["vocabulary", "articles"]
        },
        {
            "id": "fb_10",
            "type": "fill_blank",
            "sentence": "Sie ___ eine Lehrerin.",
            "answer": "ist",
            "hint": "verb 'sein' for 'she'",
            "explanation": "Third person singular of 'sein' is 'ist'",
            "skills": ["verbs"]
        },
        {
            "id": "fb_11",
            "type": "mcq",
            "question": "Welcher Artikel? ___ Auto ist schnell.",
            "options": ["Der", "Die", "Das", "Den"],
            "answer": "Das",
            "explanation": "'Auto' is neuter, so it uses 'das'",
            "skills": ["articles"]
        },
        {
            "id": "fb_12",
            "type": "translation",
            "english": "I have a dog",
            "answer": "Ich habe einen Hund",
            "acceptable_answers": ["Ich habe einen Hund", "ich habe einen hund"],
            "explanation": "'Hund' is masculine accusative, uses 'einen'",
            "skills": ["vocabulary", "cases"]
        },
        {
            "id": "fb_13",
            "type": "fill_blank",
            "sentence": "Du ___ sehr nett.",
            "answer": "bist",
            "hint": "verb 'sein' for 'you'",
            "explanation": "Second person singular of 'sein' is 'bist'",
            "skills": ["verbs"]
        },
        {
            "id": "fb_14",
            "type": "mcq",
            "question": "Was passt? ___ Tisch ist braun.",
            "options": ["Der", "Die", "Das", "Den"],
            "answer": "Der",
            "explanation": "'Tisch' is masculine, so it uses 'der'",
            "skills": ["articles"]
        },
        {
            "id": "fb_15",
            "type": "fill_blank",
            "sentence": "Er ___ Fußball.",
            "answer": "spielt",
            "hint": "verb 'spielen' (to play)",
            "explanation": "Third person singular of 'spielen' is 'spielt'",
            "skills": ["verbs"]
        },
        {
            "id": "fb_16",
            "type": "translation",
            "english": "The woman is beautiful",
            "answer": "Die Frau ist schön",
            "acceptable_answers": ["Die Frau ist schön", "die frau ist schön"],
            "explanation": "'Frau' is feminine, uses 'die'",
            "skills": ["vocabulary", "articles"]
        },
        {
            "id": "fb_17",
            "type": "mcq",
            "question": "Welches Verb? Wir ___ nach Hause.",
            "options": ["gehe", "gehst", "geht", "gehen"],
            "answer": "gehen",
            "explanation": "First person plural of 'gehen' is 'gehen'",
            "skills": ["verbs"]
        },
        {
            "id": "fb_18",
            "type": "fill_blank",
            "sentence": "Das Kind ___ klein.",
            "answer": "ist",
            "hint": "verb 'sein' for 'the child'",
            "explanation": "Third person singular of 'sein' is 'ist'",
            "skills": ["verbs"]
        },
        {
            "id": "fb_19",
            "type": "mcq",
            "question": "Artikel? ___ Mädchen ist jung.",
            "options": ["Der", "Die", "Das", "Den"],
            "answer": "Das",
            "explanation": "'Mädchen' is neuter, so it uses 'das'",
            "skills": ["articles"]
        },
        {
            "id": "fb_20",
            "type": "translation",
            "english": "He reads a book",
            "answer": "Er liest ein Buch",
            "acceptable_answers": ["Er liest ein Buch", "er liest ein buch"],
            "explanation": "'lesen' conjugated for 'er' is 'liest'",
            "skills": ["verbs", "vocabulary"]
        },
        {
            "id": "fb_21",
            "type": "listening",
            "audio_text": "Ich heiße Anna und ich komme aus Deutschland.",
            "question": "Where does Anna come from?",
            "options": ["France", "Germany", "Austria", "Switzerland"],
            "answer": "Germany",
            "explanation": "'Deutschland' means Germany",
            "skills": ["listening", "vocabulary"]
        },
        {
            "id": "fb_22",
            "type": "reading",
            "passage": "Peter geht jeden Morgen joggen. Er läuft im Park. Das ist gesund.",
            "question": "What does Peter do every morning?",
            "options": ["Swimming", "Jogging", "Cycling", "Walking"],
            "answer": "Jogging",
            "explanation": "'joggen' means jogging",
            "skills": ["reading", "vocabulary"]
        },
        {
            "id": "fb_23",
            "type": "speaking",
            "prompt": "Say: 'Guten Tag'",
            "expected_text": "Guten Tag",
            "explanation": "This is a common German greeting meaning 'Good day'",
            "skills": ["speaking", "pronunciation"]
        }
    ]
    # Randomize the fallback questions to provide variety
    import random
    shuffled = fallback.copy()
    random.shuffle(shuffled)
    return shuffled[:size]

# ===== Endpoints =====

@router.post('/start', response_model=QuizStartResponse)
async def start_quiz(
    config: QuizConfig,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(optional_auth_dep)
):
    """
    Start a new quiz with AI-generated questions.
    Questions are cached in DB for reuse.
    """
    try:
        # Try to get cached questions first
        cached_questions = []
        if config.topic:
            # Look for cached questions matching criteria
            cache_query = {
                "skills": config.topic,
                "level": config.level,
                "cached": True
            }
            cached = await db["quiz_questions"].aggregate([
                {"$match": cache_query},
                {"$sample": {"size": config.size}}
            ]).to_list(config.size)
            
            for q in cached:
                q.pop("_id", None)
                q.pop("cached", None)
                q.pop("created_at", None)
                cached_questions.append(q)
        
        # Generate new questions if not enough cached
        questions = []
        source = "cache"
        
        if len(cached_questions) < config.size:
            # Generate missing questions with AI (with timeout protection)
            needed = config.size - len(cached_questions)
            try:
                import asyncio
                # Set 15 second timeout for AI generation
                ai_questions = await asyncio.wait_for(
                    generate_questions(
                        track=config.topic,
                        size=needed,
                        level=config.level
                    ),
                    timeout=15.0
                )
                
                # Cache the AI-generated questions for future use
                if ai_questions:
                    for q in ai_questions:
                        q_copy = q.copy()
                        q_copy["cached"] = True
                        q_copy["level"] = config.level
                        q_copy["created_at"] = datetime.now(timezone.utc)
                        await db["quiz_questions"].insert_one(q_copy)
                    
                    questions = cached_questions + ai_questions
                    source = "mixed" if cached_questions else "ai"
                else:
                    questions = cached_questions
            except asyncio.TimeoutError:
                logger.warning(f"AI generation timed out, using cached questions only")
                questions = cached_questions
            except Exception as e:
                logger.error(f"AI generation failed: {e}")
                questions = cached_questions
        else:
            questions = cached_questions
        
        # Filter by question types if specified
        if config.question_types:
            questions = [q for q in questions if q.get("type") in config.question_types]
        
        # Limit to requested size
        questions = questions[:config.size]
        
        # If still no questions, create fallback questions
        if not questions:
            logger.warning("No cached or AI questions available, using fallback questions")
            questions = _create_fallback_questions(config.topic, config.level, config.size)
        
        # Create quiz session
        quiz_id = str(ObjectId())
        session = {
            "_id": quiz_id,
            "user_id": user_id or "anonymous",
            "config": config.model_dump(),
            "questions": questions,
            "started_at": datetime.now(timezone.utc),
            "completed": False
        }
        await db["quiz_sessions"].insert_one(session)
        
        return QuizStartResponse(
            quiz_id=quiz_id,
            questions=[QuizQuestion(**q) for q in questions],
            config=config,
            source=source
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quiz start failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to start quiz")

@router.post('/submit', response_model=QuizSubmitResponse)
async def submit_quiz(
    submission: QuizSubmitRequest,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(optional_auth_dep)
):
    """
    Submit quiz answers and get detailed results with feedback.
    """
    try:
        # Get quiz session
        session = await db["quiz_sessions"].find_one({"_id": submission.quiz_id})
        if not session:
            raise HTTPException(status_code=404, detail="Quiz session not found")
        
        questions = session.get("questions", [])
        if not questions:
            raise HTTPException(status_code=400, detail="No questions in quiz session")
        
        # Create answer lookup
        answer_map = {a.question_id: a for a in submission.answers}
        
        # Evaluate answers
        results = []
        correct_count = 0
        skill_stats: Dict[str, Dict[str, int]] = {}
        
        for q in questions:
            qid = q["id"]
            user_answer_obj = answer_map.get(qid)
            user_answer = user_answer_obj.user_answer.strip() if user_answer_obj else ""
            correct_answer = q["answer"]
            
            # Check correctness based on question type
            is_correct = False
            if q["type"] == "translation":
                # Check against acceptable answers (case-insensitive)
                acceptable = q.get("acceptable_answers", [correct_answer])
                is_correct = any(
                    user_answer.lower() == acc.lower() 
                    for acc in acceptable
                )
            elif q["type"] == "sentence_order":
                # Exact match for sentence order
                is_correct = user_answer.strip() == correct_answer.strip()
            else:
                # Exact match for MCQ and fill_blank
                is_correct = user_answer == correct_answer
            
            if is_correct:
                correct_count += 1
            
            # Track skills
            for skill in q.get("skills", []):
                if skill not in skill_stats:
                    skill_stats[skill] = {"correct": 0, "total": 0}
                skill_stats[skill]["total"] += 1
                if is_correct:
                    skill_stats[skill]["correct"] += 1
            
            results.append(QuestionResult(
                question_id=qid,
                correct=is_correct,
                user_answer=user_answer,
                correct_answer=correct_answer,
                explanation=q.get("explanation", "")
            ))
        
        # Calculate stats
        total = len(questions)
        percentage = round((correct_count / total * 100), 1) if total > 0 else 0
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        for skill, stats in skill_stats.items():
            accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            if accuracy >= 0.7:
                strengths.append(skill)
            elif accuracy < 0.5:
                weaknesses.append(skill)
        
        # Calculate time taken
        started_at = session.get("started_at")
        time_taken = None
        if started_at:
            # Ensure started_at is timezone-aware
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)
            time_taken = int((datetime.now(timezone.utc) - started_at).total_seconds())
        
        # Update session
        await db["quiz_sessions"].update_one(
            {"_id": submission.quiz_id},
            {
                "$set": {
                    "completed": True,
                    "completed_at": datetime.now(timezone.utc),
                    "score": correct_count,
                    "total": total,
                    "percentage": percentage,
                    "answers": [a.model_dump() for a in submission.answers],
                    "time_taken": time_taken
                }
            }
        )
        
        # Save to user history
        if user_id and user_id != "anonymous":
            history_entry = {
                "user_id": user_id,
                "quiz_id": submission.quiz_id,
                "config": session.get("config"),
                "score": correct_count,
                "total": total,
                "percentage": percentage,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "time_taken": time_taken,
                "completed_at": datetime.now(timezone.utc)
            }
            await db["quiz_history"].insert_one(history_entry)
        
        return QuizSubmitResponse(
            quiz_id=submission.quiz_id,
            score=correct_count,
            total=total,
            percentage=percentage,
            results=results,
            strengths=strengths or ["Keep practicing!"],
            weaknesses=weaknesses or ["None identified"],
            time_taken=time_taken
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quiz submit failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit quiz")

@router.get('/history')
async def get_quiz_history(
    limit: int = 10,
    db=Depends(get_db),
    user_id: str = Depends(auth_dep)
):
    """Get user's quiz history with stats."""
    try:
        history = await db["quiz_history"].find(
            {"user_id": user_id}
        ).sort("completed_at", -1).limit(limit).to_list(limit)
        
        # Calculate overall stats
        if history:
            total_quizzes = len(history)
            avg_score = sum(h["percentage"] for h in history) / total_quizzes
            best_score = max(h["percentage"] for h in history)
            
            # Aggregate skills
            all_strengths = []
            all_weaknesses = []
            for h in history:
                all_strengths.extend(h.get("strengths", []))
                all_weaknesses.extend(h.get("weaknesses", []))
            
            # Count frequency
            from collections import Counter
            strength_counts = Counter(all_strengths)
            weakness_counts = Counter(all_weaknesses)
            
            return {
                "history": history,
                "stats": {
                    "total_quizzes": total_quizzes,
                    "average_score": round(avg_score, 1),
                    "best_score": round(best_score, 1),
                    "top_strengths": [s for s, _ in strength_counts.most_common(3)],
                    "top_weaknesses": [w for w, _ in weakness_counts.most_common(3)]
                }
            }
        
        return {"history": [], "stats": None}
        
    except Exception as e:
        logger.error(f"Failed to get quiz history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quiz history")

@router.get('/topics')
async def get_available_topics():
    """Get list of available quiz topics."""
    return {
        "topics": [
            {"id": "articles", "name": "Articles (der/die/das)", "icon": "📰"},
            {"id": "verbs", "name": "Verb Conjugation", "icon": "🔄"},
            {"id": "cases", "name": "Cases (Nominativ/Akkusativ/Dativ/Genitiv)", "icon": "📦"},
            {"id": "vocabulary", "name": "Vocabulary", "icon": "📚"},
            {"id": "prepositions", "name": "Prepositions", "icon": "🔗"},
            {"id": "pluralization", "name": "Pluralization", "icon": "👥"},
            {"id": "word_order", "name": "Word Order", "icon": "🔀"},
            {"id": "adjectives", "name": "Adjective Declension", "icon": "✨"},
            {"id": "pronouns", "name": "Pronouns", "icon": "👤"},
            {"id": "mixed", "name": "Mixed Grammar", "icon": "🎯"}
        ],
        "levels": [
            {"id": "beginner", "name": "Beginner", "description": "Basic phrases and vocabulary"},
            {"id": "intermediate", "name": "Intermediate", "description": "Everyday situations and conversations"},
            {"id": "advanced", "name": "Advanced", "description": "Complex topics and nuanced grammar"}
        ],
        "question_types": [
            {"id": "mcq", "name": "Multiple Choice", "icon": "☑️"},
            {"id": "fill_blank", "name": "Fill in the Blank", "icon": "✍️"},
            {"id": "translation", "name": "Translation", "icon": "🌐"},
            {"id": "sentence_order", "name": "Sentence Building", "icon": "🧩"}
        ]
    }
