"""
AI-powered vocabulary generation service with smart caching
"""
from typing import List, Dict, Optional, Any
import datetime as dt
from ..ollama_client import ollama_client


class VocabAIService:
    """Service for AI-powered vocabulary generation with intelligent caching"""
    
    def __init__(self, db):
        self.db = db
        self.ollama = ollama_client
    
    async def generate_daily_words(self, level: str = "beginner", count: int = 10, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate daily vocabulary words - same words for the entire day, new words tomorrow
        
        Strategy:
        1. Check user's completed words for today
        2. Check if we have cached words for today
        3. If cache exists, return those same words (user sees their progress)
        4. If no cache, generate new words and cache them for the day
        5. Tomorrow = new cache = new words automatically
        """
        today = dt.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_str = today.date().isoformat()
        
        # Normalize level to lowercase
        level = level.lower()
        
        # Check cache first - same words all day
        cache_key = f"daily_{level}_{count}_{today_str}"
        cached = await self.db["ai_vocab_cache"].find_one({
            "cache_key": cache_key
        })
        
        if cached and cached.get("words"):
            # Return same words for the entire day
            return cached["words"][:count]
        
        # No cache - generate new words
        # Get words user has already learned (from all time, not just today)
        learned_words = set()
        if user_id:
            user_vocab = await self.db["user_vocab"].find(
                {"user_id": user_id},
                {"word": 1}
            ).to_list(length=10000)
            learned_words = {w["word"] for w in user_vocab}
        
        # Generate words, excluding already learned ones
        words = await self._generate_words_with_ai(level, count * 3, learned_words)  # Generate extra to filter
        
        # Filter out learned words
        words = [w for w in words if w["word"] not in learned_words][:count]
        
        # If not enough words, fill from database
        if len(words) < count:
            db_words = await self._fallback_to_db(level, count - len(words), learned_words)
            words.extend(db_words)
        
        # Cache for the entire day
        await self.db["ai_vocab_cache"].update_one(
            {"cache_key": cache_key},
            {
                "$set": {
                    "cache_key": cache_key,
                    "level": level,
                    "words": words,
                    "created_at": dt.datetime.utcnow(),
                    "date": today_str,
                    "expires_at": today + dt.timedelta(days=1)
                }
            },
            upsert=True
        )
        
        return words
    
    async def _generate_words_with_ai(self, level: str, count: int, exclude_words: set = None) -> List[Dict[str, Any]]:
        """Generate vocabulary words using AI model, excluding already learned words"""
        if exclude_words is None:
            exclude_words = set()
        
        level_description = {
            "beginner": "beginner level (A1-A2) - very basic everyday words and common phrases",
            "intermediate": "intermediate level (B1-B2) - more complex vocabulary for daily situations and abstract concepts",
            "advanced": "advanced level (C1-C2) - sophisticated vocabulary, nuanced expressions and idioms",
            # Legacy CEFR support
            "a1": "absolute beginner level - very basic everyday words",
            "a2": "elementary level - common everyday words and phrases",
            "b1": "intermediate level - more complex vocabulary for daily situations",
            "b2": "upper intermediate level - abstract concepts and specialized vocabulary",
            "c1": "advanced level - sophisticated vocabulary and nuanced expressions",
            "c2": "mastery level - native-like vocabulary including idioms and rare words"
        }
        
        exclude_text = ""
        if exclude_words:
            exclude_list = list(exclude_words)[:50]  # Limit to avoid huge prompts
            exclude_text = f"\n\nDo NOT include these words (user already knows them): {', '.join(exclude_list)}"
        
        prompt = f"""Generate {count} German vocabulary words at {level} level ({level_description.get(level, 'beginner level')}).{exclude_text}

For each word, provide:
1. The German word
2. English translation
3. A practical example sentence in German using the word

Format your response as a JSON array like this:
[
  {{"word": "Haus", "translation": "house", "example": "Ich wohne in einem großen Haus."}},
  {{"word": "Wasser", "translation": "water", "example": "Ich trinke jeden Tag viel Wasser."}}
]

Make sure the words are:
- Appropriate for {level} level
- Useful for everyday conversation
- Include a variety of word types (nouns, verbs, adjectives)
- Have natural, practical example sentences

Return ONLY the JSON array, no additional text."""

        try:
            # Check if Ollama is available
            if not self.ollama.is_available:
                print("Ollama not available, falling back to database")
                return await self._fallback_to_db(level, count)
            
            # Generate using Ollama
            messages = [{"role": "user", "content": prompt}]
            response = await self.ollama.chat(messages)
            response_text = response.get('message', {}).get('content', '')
            
            # Parse AI response
            import json
            import re
            
            # Extract JSON from response (in case AI adds extra text)
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                words_data = json.loads(json_match.group())
                
                # Validate and format
                formatted_words = []
                for w in words_data:
                    if isinstance(w, dict) and "word" in w and "translation" in w:
                        formatted_words.append({
                            "word": w["word"],
                            "translation": w["translation"],
                            "example": w.get("example", ""),
                            "level": level,
                            "source": "ai_generated",
                            "generated_at": dt.datetime.utcnow().isoformat()
                        })
                
                return formatted_words[:count]
            
        except Exception as e:
            print(f"AI generation failed: {e}")
        
        # Fallback: return from seed_words database
        return await self._fallback_to_db(level, count)
    
    async def _fallback_to_db(self, level: str, count: int, exclude_words: set = None) -> List[Dict[str, Any]]:
        """Fallback to database seed words if AI generation fails"""
        if exclude_words is None:
            exclude_words = set()
        
        # Convert difficulty level to CEFR for database query
        level_lower = level.lower()
        if level_lower == "beginner":
            match_criteria = {"level": {"$in": ["A1", "A2"]}}
        elif level_lower == "intermediate":
            match_criteria = {"level": {"$in": ["B1", "B2"]}}
        elif level_lower == "advanced":
            match_criteria = {"level": {"$in": ["C1", "C2"]}}
        else:
            match_criteria = {"level": level}
        
        if exclude_words:
            match_criteria["word"] = {"$nin": list(exclude_words)}
        
        pipeline = [
            {"$match": match_criteria},
            {"$sample": {"size": count}},
            {"$project": {
                "_id": 0,
                "word": 1,
                "level": 1,
                "translation": 1,
                "example": {"$arrayElemAt": ["$examples", 0]}
            }}
        ]
        
        items = await self.db["seed_words"].aggregate(pipeline).to_list(count)
        return [
            {
                "word": it.get("word", ""),
                "translation": it.get("translation", ""),
                "example": it.get("example", ""),
                "level": level,
                "source": "database"
            }
            for it in items
        ]
    
    async def generate_word_with_context(self, topic: str, level: str = "A1") -> Dict[str, Any]:
        """Generate a single word with rich context using AI"""
        
        prompt = f"""Generate 1 German vocabulary word related to "{topic}" at {level} level.

Provide:
1. The German word
2. English translation
3. A practical example sentence in German
4. A brief usage tip or context note

Format as JSON:
{{"word": "...", "translation": "...", "example": "...", "usage_tip": "..."}}

Return ONLY the JSON object."""

        try:
            if not self.ollama.is_available:
                fallback = await self._fallback_to_db(level, 1)
                return fallback[0] if fallback else {}
            
            messages = [{"role": "user", "content": prompt}]
            response = await self.ollama.chat(messages)
            response_text = response.get('message', {}).get('content', '')
            
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                word_data = json.loads(json_match.group())
                word_data["level"] = level
                word_data["source"] = "ai_generated"
                return word_data
        except Exception as e:
            print(f"AI generation failed: {e}")
        
        # Fallback
        fallback = await self._fallback_to_db(level, 1)
        return fallback[0] if fallback else {}
    
    async def enhance_word_with_ai(self, word: str) -> Dict[str, Any]:
        """Enhance an existing word with AI-generated examples and context"""
        
        prompt = f"""For the German word "{word}", provide:
1. English translation
2. 3 practical example sentences in German
3. Common collocations or phrases using this word
4. A usage tip

Format as JSON:
{{
  "word": "{word}",
  "translation": "...",
  "examples": ["...", "...", "..."],
  "collocations": ["...", "..."],
  "usage_tip": "..."
}}

Return ONLY the JSON object."""

        try:
            if not self.ollama.is_available:
                return {"word": word, "translation": "", "examples": [], "collocations": [], "usage_tip": ""}
            
            messages = [{"role": "user", "content": prompt}]
            response = await self.ollama.chat(messages)
            response_text = response.get('message', {}).get('content', '')
            
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"AI enhancement failed: {e}")
        
        return {"word": word, "translation": "", "examples": [], "collocations": [], "usage_tip": ""}
