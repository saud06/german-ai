"""
Spaced Repetition System using SM-2 Algorithm
Optimizes learning retention through intelligent review scheduling
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List
from enum import Enum

class ReviewQuality(Enum):
    """User's self-assessment of recall quality (0-5)"""
    BLACKOUT = 0      # Complete blackout
    INCORRECT = 1     # Incorrect response, but familiar
    HARD = 2          # Correct with serious difficulty
    GOOD = 3          # Correct with hesitation
    EASY = 4          # Correct with ease
    PERFECT = 5       # Perfect response

class SM2Algorithm:
    """
    SuperMemo 2 (SM-2) Algorithm Implementation
    
    The SM-2 algorithm calculates optimal review intervals based on:
    - Easiness Factor (EF): How easy the item is to remember (1.3 - 2.5)
    - Repetition Number (n): How many times reviewed successfully
    - Interval (I): Days until next review
    
    Formula:
    - If quality < 3: Reset to beginning (n=0, I=1)
    - If quality >= 3: 
        - n=1: I=1 day
        - n=2: I=6 days
        - n>2: I = I(n-1) * EF
    - EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
    """
    
    MIN_EF = 1.3
    MAX_EF = 2.5
    INITIAL_EF = 2.5
    
    @staticmethod
    def calculate_next_review(
        quality: int,
        repetitions: int,
        easiness_factor: float,
        interval: int
    ) -> Dict[str, any]:
        """
        Calculate next review parameters based on recall quality
        
        Args:
            quality: 0-5 (ReviewQuality enum value)
            repetitions: Current repetition count
            easiness_factor: Current EF (1.3-2.5)
            interval: Current interval in days
            
        Returns:
            Dict with: repetitions, easiness_factor, interval, next_review_date
        """
        # Ensure quality is in valid range
        quality = max(0, min(5, quality))
        
        # Calculate new easiness factor
        new_ef = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ef = max(SM2Algorithm.MIN_EF, min(SM2Algorithm.MAX_EF, new_ef))
        
        # If quality < 3, reset progress
        if quality < 3:
            new_repetitions = 0
            new_interval = 1
        else:
            new_repetitions = repetitions + 1
            
            # Calculate new interval
            if new_repetitions == 1:
                new_interval = 1
            elif new_repetitions == 2:
                new_interval = 6
            else:
                new_interval = round(interval * new_ef)
        
        # Calculate next review date
        next_review = datetime.now(timezone.utc) + timedelta(days=new_interval)
        
        return {
            "repetitions": new_repetitions,
            "easiness_factor": round(new_ef, 2),
            "interval": new_interval,
            "next_review_date": next_review.isoformat(),
            "last_reviewed": datetime.now(timezone.utc).isoformat()
        }

class ReviewCard:
    """
    Represents a single item to be reviewed (word, grammar rule, etc.)
    """
    
    def __init__(
        self,
        card_id: str,
        card_type: str,  # "vocabulary", "grammar", "sentence"
        content: Dict,
        user_id: str,
        repetitions: int = 0,
        easiness_factor: float = SM2Algorithm.INITIAL_EF,
        interval: int = 0,
        next_review_date: Optional[str] = None,
        last_reviewed: Optional[str] = None,
        created_at: Optional[str] = None
    ):
        self.card_id = card_id
        self.card_type = card_type
        self.content = content
        self.user_id = user_id
        self.repetitions = repetitions
        self.easiness_factor = easiness_factor
        self.interval = interval
        self.next_review_date = next_review_date or datetime.now(timezone.utc).isoformat()
        self.last_reviewed = last_reviewed
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage"""
        return {
            "card_id": self.card_id,
            "card_type": self.card_type,
            "content": self.content,
            "user_id": self.user_id,
            "repetitions": self.repetitions,
            "easiness_factor": self.easiness_factor,
            "interval": self.interval,
            "next_review_date": self.next_review_date,
            "last_reviewed": self.last_reviewed,
            "created_at": self.created_at
        }
    
    def review(self, quality: int) -> Dict:
        """
        Process a review and update card parameters
        
        Args:
            quality: 0-5 rating of recall quality
            
        Returns:
            Updated card parameters
        """
        result = SM2Algorithm.calculate_next_review(
            quality=quality,
            repetitions=self.repetitions,
            easiness_factor=self.easiness_factor,
            interval=self.interval
        )
        
        # Update card state
        self.repetitions = result["repetitions"]
        self.easiness_factor = result["easiness_factor"]
        self.interval = result["interval"]
        self.next_review_date = result["next_review_date"]
        self.last_reviewed = result["last_reviewed"]
        
        return result

class ReviewScheduler:
    """
    Manages review scheduling and card selection
    """
    
    @staticmethod
    def get_due_cards(cards: List[ReviewCard], limit: int = 20) -> List[ReviewCard]:
        """
        Get cards that are due for review
        
        Args:
            cards: List of all user's cards
            limit: Maximum number of cards to return
            
        Returns:
            List of cards due for review, sorted by priority
        """
        now = datetime.now(timezone.utc)
        
        # Filter due cards
        due_cards = [
            card for card in cards
            if datetime.fromisoformat(card.next_review_date.replace('Z', '+00:00')) <= now
        ]
        
        # Sort by priority:
        # 1. Cards with lower repetitions (new/struggling items)
        # 2. Cards overdue the longest
        due_cards.sort(key=lambda c: (
            c.repetitions,
            datetime.fromisoformat(c.next_review_date.replace('Z', '+00:00'))
        ))
        
        return due_cards[:limit]
    
    @staticmethod
    def get_daily_stats(cards: List[ReviewCard]) -> Dict:
        """
        Calculate daily review statistics
        
        Returns:
            Dict with review stats
        """
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count cards by status
        new_cards = sum(1 for c in cards if c.repetitions == 0)
        learning_cards = sum(1 for c in cards if 0 < c.repetitions < 3)
        mature_cards = sum(1 for c in cards if c.repetitions >= 3)
        
        # Count due cards
        due_today = sum(
            1 for c in cards
            if datetime.fromisoformat(c.next_review_date.replace('Z', '+00:00')) <= now
        )
        
        # Count reviewed today
        reviewed_today = sum(
            1 for c in cards
            if c.last_reviewed and 
            datetime.fromisoformat(c.last_reviewed.replace('Z', '+00:00')) >= today_start
        )
        
        return {
            "total_cards": len(cards),
            "new_cards": new_cards,
            "learning_cards": learning_cards,
            "mature_cards": mature_cards,
            "due_today": due_today,
            "reviewed_today": reviewed_today,
            "retention_rate": round(
                (mature_cards / max(len(cards), 1)) * 100, 1
            )
        }
    
    @staticmethod
    def predict_workload(cards: List[ReviewCard], days: int = 7) -> List[Dict]:
        """
        Predict review workload for upcoming days
        
        Args:
            cards: List of all cards
            days: Number of days to predict
            
        Returns:
            List of daily workload predictions
        """
        now = datetime.now(timezone.utc)
        predictions = []
        
        for day in range(days):
            target_date = now + timedelta(days=day)
            target_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            target_end = target_start + timedelta(days=1)
            
            due_count = sum(
                1 for c in cards
                if target_start <= datetime.fromisoformat(c.next_review_date.replace('Z', '+00:00')) < target_end
            )
            
            predictions.append({
                "date": target_date.date().isoformat(),
                "due_cards": due_count
            })
        
        return predictions

def create_vocabulary_card(word: Dict, user_id: str) -> ReviewCard:
    """
    Create a review card from a vocabulary word
    
    Args:
        word: Word dict with 'word', 'translation', 'example'
        user_id: User ID
        
    Returns:
        ReviewCard instance
    """
    card_id = f"vocab_{word.get('word', 'unknown')}_{user_id}"
    
    return ReviewCard(
        card_id=card_id,
        card_type="vocabulary",
        content={
            "word": word.get("word"),
            "translation": word.get("translation"),
            "example": word.get("example"),
            "level": word.get("level", "A1")
        },
        user_id=user_id
    )

def create_grammar_card(rule: Dict, user_id: str) -> ReviewCard:
    """
    Create a review card from a grammar rule
    
    Args:
        rule: Grammar rule dict
        user_id: User ID
        
    Returns:
        ReviewCard instance
    """
    card_id = f"grammar_{rule.get('id', 'unknown')}_{user_id}"
    
    return ReviewCard(
        card_id=card_id,
        card_type="grammar",
        content={
            "rule": rule.get("rule"),
            "explanation": rule.get("explanation"),
            "examples": rule.get("examples", []),
            "category": rule.get("category")
        },
        user_id=user_id
    )
