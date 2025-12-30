"""
Spaced Repetition Review System API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
from ..db import get_db
from ..security import auth_dep
from ..services.spaced_repetition import (
    ReviewCard, ReviewScheduler, SM2Algorithm,
    create_vocabulary_card, create_grammar_card
)

router = APIRouter(prefix="/reviews")

class ReviewRequest(BaseModel):
    card_id: str
    quality: int  # 0-5

class ReviewResponse(BaseModel):
    card_id: str
    repetitions: int
    easiness_factor: float
    interval: int
    next_review_date: str
    message: str

class CardResponse(BaseModel):
    card_id: str
    card_type: str
    content: Dict
    repetitions: int
    easiness_factor: float
    interval: int
    next_review_date: str
    last_reviewed: Optional[str]

class DailyStatsResponse(BaseModel):
    total_cards: int
    new_cards: int
    learning_cards: int
    mature_cards: int
    due_today: int
    reviewed_today: int
    retention_rate: float

class WorkloadPrediction(BaseModel):
    date: str
    due_cards: int

class AddCardRequest(BaseModel):
    card_type: str  # "vocabulary" or "grammar"
    content: Dict

@router.get('/due', response_model=List[CardResponse])
async def get_due_cards(
    limit: int = 20,
    card_type: Optional[str] = None,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Get cards due for review
    Supports filtering by card_type: vocabulary, grammar, quiz_mistake, scenario
    """
    
    # Build query
    query = {"user_id": user_id}
    if card_type:
        query["card_type"] = card_type
    
    # Fetch user's cards from database
    cards_data = await db["review_cards"].find(query).to_list(length=1000)
    
    # Convert to ReviewCard objects
    cards = [
        ReviewCard(
            card_id=c.get("card_id", str(c["_id"])),
            card_type=c.get("card_type", "vocabulary"),
            content=c.get("content", {}),
            user_id=c.get("user_id", user_id),
            repetitions=c.get("repetitions", 0),
            easiness_factor=c.get("easiness_factor", SM2Algorithm.INITIAL_EF),
            interval=c.get("interval", 0),
            next_review_date=c.get("next_review_date"),
            last_reviewed=c.get("last_reviewed"),
            created_at=c.get("created_at")
        )
        for c in cards_data
    ]
    
    # Get due cards
    due_cards = ReviewScheduler.get_due_cards(cards, limit=limit)
    
    return [
        CardResponse(
            card_id=card.card_id,
            card_type=card.card_type,
            content=card.content,
            repetitions=card.repetitions,
            easiness_factor=card.easiness_factor,
            interval=card.interval,
            next_review_date=card.next_review_date,
            last_reviewed=card.last_reviewed
        )
        for card in due_cards
    ]

@router.post('/submit', response_model=ReviewResponse)
async def submit_review(
    review: ReviewRequest,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Submit a review for a card
    """
    
    # Validate quality
    if not 0 <= review.quality <= 5:
        raise HTTPException(status_code=400, detail="Quality must be between 0 and 5")
    
    # Fetch card
    card_data = await db["review_cards"].find_one({
        "card_id": review.card_id,
        "user_id": user_id
    })
    
    if not card_data:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Create ReviewCard object
    card = ReviewCard(
        card_id=card_data.get("card_id", str(card_data["_id"])),
        card_type=card_data.get("card_type", "vocabulary"),
        content=card_data.get("content", {}),
        user_id=card_data.get("user_id", user_id),
        repetitions=card_data.get("repetitions", 0),
        easiness_factor=card_data.get("easiness_factor", SM2Algorithm.INITIAL_EF),
        interval=card_data.get("interval", 0),
        next_review_date=card_data.get("next_review_date"),
        last_reviewed=card_data.get("last_reviewed"),
        created_at=card_data.get("created_at")
    )
    
    # Process review
    result = card.review(review.quality)
    
    # Update database
    await db["review_cards"].update_one(
        {"card_id": review.card_id, "user_id": user_id},
        {"$set": card.to_dict()}
    )
    
    # Generate message
    if review.quality < 3:
        message = "Keep practicing! This card will be shown again soon."
    elif result["interval"] == 1:
        message = "Good! You'll see this again tomorrow."
    elif result["interval"] == 6:
        message = "Great! Next review in 6 days."
    else:
        message = f"Excellent! Next review in {result['interval']} days."
    
    return ReviewResponse(
        card_id=card.card_id,
        repetitions=result["repetitions"],
        easiness_factor=result["easiness_factor"],
        interval=result["interval"],
        next_review_date=result["next_review_date"],
        message=message
    )

@router.get('/stats', response_model=DailyStatsResponse)
async def get_daily_stats(
    card_type: Optional[str] = None,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Get daily review statistics
    Supports filtering by card_type: vocabulary, grammar, quiz_mistake, scenario
    """
    
    # Build query
    query = {"user_id": user_id}
    if card_type:
        query["card_type"] = card_type
    
    # Fetch all user's cards
    cards_data = await db["review_cards"].find(query).to_list(length=10000)
    
    # Convert to ReviewCard objects
    cards = [
        ReviewCard(
            card_id=c.get("card_id", str(c["_id"])),
            card_type=c.get("card_type", "vocabulary"),
            content=c.get("content", {}),
            user_id=c.get("user_id", user_id),
            repetitions=c.get("repetitions", 0),
            easiness_factor=c.get("easiness_factor", SM2Algorithm.INITIAL_EF),
            interval=c.get("interval", 0),
            next_review_date=c.get("next_review_date"),
            last_reviewed=c.get("last_reviewed"),
            created_at=c.get("created_at")
        )
        for c in cards_data
    ]
    
    # Calculate stats
    stats = ReviewScheduler.get_daily_stats(cards)
    
    return DailyStatsResponse(**stats)

@router.get('/workload', response_model=List[WorkloadPrediction])
async def get_workload_prediction(
    days: int = 7,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Predict review workload for upcoming days
    """
    
    # Fetch all user's cards
    cards_data = await db["review_cards"].find(
        {"user_id": user_id}
    ).to_list(length=10000)
    
    # Convert to ReviewCard objects
    cards = [
        ReviewCard(
            card_id=c.get("card_id", str(c["_id"])),
            card_type=c.get("card_type", "vocabulary"),
            content=c.get("content", {}),
            user_id=c.get("user_id", user_id),
            repetitions=c.get("repetitions", 0),
            easiness_factor=c.get("easiness_factor", SM2Algorithm.INITIAL_EF),
            interval=c.get("interval", 0),
            next_review_date=c.get("next_review_date"),
            last_reviewed=c.get("last_reviewed"),
            created_at=c.get("created_at")
        )
        for c in cards_data
    ]
    
    # Get predictions
    predictions = ReviewScheduler.predict_workload(cards, days=min(days, 30))
    
    return [WorkloadPrediction(**p) for p in predictions]

@router.post('/add-card', response_model=CardResponse)
async def add_card(
    request: AddCardRequest,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Add a new card to the review system
    """
    
    # Create card based on type
    if request.card_type == "vocabulary":
        card = create_vocabulary_card(request.content, user_id)
    elif request.card_type == "grammar":
        card = create_grammar_card(request.content, user_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid card type")
    
    # Check if card already exists
    existing = await db["review_cards"].find_one({
        "card_id": card.card_id,
        "user_id": user_id
    })
    
    if existing:
        raise HTTPException(status_code=409, detail="Card already exists")
    
    # Insert into database
    await db["review_cards"].insert_one(card.to_dict())
    
    return CardResponse(
        card_id=card.card_id,
        card_type=card.card_type,
        content=card.content,
        repetitions=card.repetitions,
        easiness_factor=card.easiness_factor,
        interval=card.interval,
        next_review_date=card.next_review_date,
        last_reviewed=card.last_reviewed
    )

@router.post('/bulk-add')
async def bulk_add_cards(
    card_type: str,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Bulk add cards from vocabulary or grammar collections
    """
    added_count = 0
    
    if card_type == "vocabulary":
        # Get user's learned words
        words = await db["seed_words"].find({}).limit(50).to_list(length=50)
        
        for word in words:
            card = create_vocabulary_card(word, user_id)
            
            # Check if exists
            existing = await db["review_cards"].find_one({
                "card_id": card.card_id
            })
            
            if not existing:
                await db["review_cards"].insert_one(card.to_dict())
                added_count += 1
    
    elif card_type == "grammar":
        # Get grammar rules
        rules = await db["grammar_rules"].find({}).limit(30).to_list(length=30)
        
        for rule in rules:
            card = create_grammar_card(rule, user_id)
            
            # Check if exists
            existing = await db["review_cards"].find_one({
                "card_id": card.card_id
            })
            
            if not existing:
                await db["review_cards"].insert_one(card.to_dict())
                added_count += 1
    
    else:
        raise HTTPException(status_code=400, detail="Invalid card type")
    
    return {
        "message": f"Added {added_count} {card_type} cards",
        "count": added_count
    }

@router.post('/add-quiz-mistakes')
async def add_quiz_mistakes(
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Add quiz mistakes as review cards
    """
    added_count = 0
    
    # Get user's quiz sessions with wrong answers
    sessions = await db["quiz_sessions"].find({
        "user_id": user_id,
        "completed": True
    }).limit(50).to_list(length=50)
    
    for session in sessions:
        answers = session.get("answers", [])
        for answer in answers:
            if not answer.get("correct", False):
                # Create card from wrong answer
                question_id = answer.get("question_id")
                if not question_id:
                    continue
                
                # Get question details
                question = await db["quiz_questions"].find_one({"_id": question_id})
                if not question:
                    continue
                
                card_id = f"quiz_{user_id}_{question_id}"
                
                # Check if exists
                existing = await db["review_cards"].find_one({"card_id": card_id})
                if existing:
                    continue
                
                # Create review card
                from ..services.spaced_repetition import ReviewCard
                card = ReviewCard(
                    card_id=card_id,
                    card_type="quiz_mistake",
                    content={
                        "question": question.get("question", ""),
                        "correct_answer": question.get("answer", ""),
                        "user_answer": answer.get("answer", ""),
                        "explanation": question.get("explanation", ""),
                        "skill": question.get("skill", "")
                    },
                    user_id=user_id
                )
                
                await db["review_cards"].insert_one(card.to_dict())
                added_count += 1
    
    return {
        "message": f"Added {added_count} quiz mistake cards",
        "count": added_count
    }

@router.post('/add-scenario-objectives')
async def add_scenario_objectives(
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Add incomplete scenario objectives as review cards
    """
    added_count = 0
    
    # Get user's conversation states
    states = await db["conversation_states"].find({
        "user_id": user_id
    }).limit(50).to_list(length=50)
    
    for state in states:
        scenario_id = state.get("scenario_id")
        objectives_progress = state.get("objectives_progress", [])
        
        # Get scenario details
        scenario = await db["scenarios"].find_one({"_id": scenario_id})
        if not scenario:
            continue
        
        # Find incomplete objectives
        for obj_progress in objectives_progress:
            if not obj_progress.get("completed", False):
                objective_id = obj_progress.get("objective_id")
                objective = next(
                    (obj for obj in scenario.get("objectives", []) 
                     if obj.get("id") == objective_id),
                    None
                )
                
                if not objective:
                    continue
                
                card_id = f"scenario_{user_id}_{scenario_id}_{objective_id}"
                
                # Check if exists
                existing = await db["review_cards"].find_one({"card_id": card_id})
                if existing:
                    continue
                
                # Create review card
                from ..services.spaced_repetition import ReviewCard
                card = ReviewCard(
                    card_id=card_id,
                    card_type="scenario",
                    content={
                        "scenario_name": scenario.get("name", ""),
                        "objective": objective.get("description", ""),
                        "hint": objective.get("hint", ""),
                        "keywords": objective.get("keywords", []),
                        "scenario_id": str(scenario_id)
                    },
                    user_id=user_id
                )
                
                await db["review_cards"].insert_one(card.to_dict())
                added_count += 1
    
    return {
        "message": f"Added {added_count} scenario objective cards",
        "count": added_count
    }

@router.delete('/card/{card_id}')
async def delete_card(
    card_id: str,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Delete a review card
    """
    
    result = await db["review_cards"].delete_one({
        "card_id": card_id,
        "user_id": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Card not found")
    
    return {"message": "Card deleted successfully"}

@router.get('/all', response_model=List[CardResponse])
async def get_all_cards(
    card_type: Optional[str] = None,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Get all user's review cards
    """
    
    query = {"user_id": user_id}
    if card_type:
        query["card_type"] = card_type
    
    cards_data = await db["review_cards"].find(query).to_list(length=10000)
    
    return [
        CardResponse(
            card_id=c.get("card_id", str(c["_id"])),
            card_type=c.get("card_type", "vocabulary"),
            content=c.get("content", {}),
            repetitions=c.get("repetitions", 0),
            easiness_factor=c.get("easiness_factor", SM2Algorithm.INITIAL_EF),
            interval=c.get("interval", 0),
            next_review_date=c.get("next_review_date"),
            last_reviewed=c.get("last_reviewed")
        )
        for c in cards_data
    ]
