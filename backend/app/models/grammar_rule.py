"""
Grammar Rules Model
Advanced German grammar rules with examples and exercises
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class GrammarExample(BaseModel):
    """Example sentence demonstrating a grammar rule"""
    german: str
    english: str
    highlight: Optional[str] = None  # Part to highlight
    explanation: Optional[str] = None


class GrammarExercise(BaseModel):
    """Exercise for practicing a grammar rule"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    type: str  # fill_blank, multiple_choice, transform, translate
    question: str
    options: Optional[List[str]] = None  # For multiple choice
    correct_answer: str
    explanation: str
    difficulty: int = 1  # 1-5


class GrammarRule(BaseModel):
    """German grammar rule with explanations and exercises"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str  # e.g., "Nominative Case"
    title_de: str  # German title
    category: str  # cases, verbs, articles, adjectives, word_order, etc.
    level: str  # A1, A2, B1, B2, C1, C2
    difficulty: int = 1  # 1-5
    
    # Rule explanation
    description: str  # English explanation
    description_de: str  # German explanation
    
    # When to use
    usage: List[str]  # List of usage scenarios
    
    # Examples
    examples: List[GrammarExample]
    
    # Common mistakes
    common_mistakes: List[Dict[str, str]]  # wrong -> correct with explanation
    
    # Exercises
    exercises: List[GrammarExercise]
    
    # Related rules
    related_rules: List[str] = []  # IDs of related rules
    
    # Tags for searching
    tags: List[str] = []
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserGrammarProgress(BaseModel):
    """Track user's progress with grammar rules"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    rule_id: str
    
    # Progress tracking
    studied: bool = False
    mastered: bool = False
    exercises_completed: int = 0
    exercises_correct: int = 0
    accuracy: float = 0.0
    
    # Last interaction
    last_studied: Optional[datetime] = None
    times_reviewed: int = 0
    
    # Notes
    user_notes: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
