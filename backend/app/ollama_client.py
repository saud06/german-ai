"""
Ollama client for self-hosted LLM integration
"""
import ollama
from typing import Optional, Dict, List, AsyncGenerator
import logging
from app.config import get_settings
from app.environment import get_ollama_host, get_backend_info

settings = get_settings()
logger = logging.getLogger(__name__)

class OllamaClient:
    """Async Ollama client wrapper for German language learning"""
    
    def __init__(self):
        # Auto-detect environment and set appropriate host
        self.host = get_ollama_host()
        self.model = settings.OLLAMA_MODEL
        self.client = None
        self.is_available = False
        
        # Log backend info
        backend_info = get_backend_info()
        logger.info(f"🔧 Backend Environment: {backend_info['environment']}")
        logger.info(f"🔧 Ollama Host: {backend_info['ollama_host']}")
        logger.info(f"🔧 GPU Available: {backend_info['gpu_available']}")
        logger.info(f"🔧 Platform: {backend_info['platform']} ({backend_info['machine']})")
    
    async def initialize(self):
        """Initialize Ollama client and check availability"""
        try:
            self.client = ollama.AsyncClient(host=self.host)
            # Test connection by listing models
            models = await self.client.list()
            self.is_available = True
            logger.info(f"✅ Ollama connected: {len(models.get('models', []))} models available")
            
            # Check if our model is available
            model_names = [m['name'] for m in models.get('models', [])]
            if self.model not in model_names and not any(self.model.split(':')[0] in name for name in model_names):
                logger.warning(f"⚠️  Model {self.model} not found. Available: {model_names}")
                logger.info(f"💡 Run: docker exec german_ollama ollama pull {self.model}")
            else:
                # Pre-load the model to keep it in memory
                try:
                    logger.info(f"🔥 Pre-loading {self.model} into memory...")
                    await self.chat([{"role": "user", "content": "Hallo"}], max_tokens=10)
                    logger.info(f"✅ Model {self.model} loaded and ready!")
                except Exception as e:
                    logger.warning(f"⚠️  Model pre-load failed: {e}")
        except Exception as e:
            logger.error(f"❌ Ollama connection failed: {e}")
            self.is_available = False
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        keep_alive: str = "30m"
    ) -> Dict | AsyncGenerator:
        """
        Send chat request to Ollama
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            keep_alive: How long to keep model in memory (e.g., "30m", "1h")
        
        Returns:
            Response dict or async generator for streaming
        """
        if not self.is_available:
            raise Exception("Ollama is not available")
        
        options = {
            'temperature': temperature or settings.OLLAMA_TEMPERATURE,
            'num_predict': max_tokens or settings.OLLAMA_MAX_TOKENS,
        }
        
        try:
            if stream:
                return self._stream_chat(messages, options, keep_alive)
            else:
                response = await self.client.chat(
                    model=self.model,
                    messages=messages,
                    options=options,
                    keep_alive=keep_alive
                )
                return response
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise
    
    async def _stream_chat(self, messages: List[Dict], options: Dict, keep_alive: str = "30m") -> AsyncGenerator:
        """Stream chat responses"""
        try:
            async for chunk in await self.client.chat(
                model=self.model,
                messages=messages,
                options=options,
                stream=True,
                keep_alive=keep_alive
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise
    
    async def generate_with_cache(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        cache_ttl: int = 3600
    ) -> str:
        """
        Generate response with Redis caching
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            cache_ttl: Cache time-to-live in seconds
        
        Returns:
            Generated text
        """
        # Create cache key
        cache_key = self._create_cache_key(prompt, system_prompt)
        
        # Check cache
        cached = await redis_client.get(cache_key)
        if cached:
            logger.info("✅ Cache hit for Ollama request")
            return cached
        
        # Generate response
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.chat(messages)
        result = response.get('message', {}).get('content', '')
        
        # Cache the result
        await redis_client.set(cache_key, result, expire=cache_ttl)
        
        return result
    
    def _create_cache_key(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Create cache key from prompt"""
        content = f"{system_prompt or ''}:{prompt}:{self.model}"
        hash_obj = hashlib.md5(content.encode())
        return f"ollama:{hash_obj.hexdigest()}"
    
    async def check_grammar(self, sentence: str, user_level: str = "B1") -> Dict:
        """
        Check German grammar using Ollama
        
        Args:
            sentence: German sentence to check
            user_level: CEFR level (A1, A2, B1, B2, C1, C2)
        
        Returns:
            Dict with corrected sentence, explanation, and tips
        """
        system_prompt = f"""You are a German language teacher helping a {user_level} level student.
Analyze the German sentence for grammar mistakes.
Respond in JSON format with:
- "is_correct": boolean
- "corrected": corrected sentence (or original if correct)
- "explanation": brief explanation of errors
- "tips": list of learning tips
- "confidence": confidence score 0-100

Be encouraging and educational."""

        prompt = f"Analyze this German sentence: '{sentence}'"
        
        try:
            response = await self.generate_with_cache(prompt, system_prompt, cache_ttl=86400)
            
            # Try to parse JSON response
            try:
                # Extract JSON from response (handle markdown code blocks)
                json_str = response
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '```' in response:
                    json_str = response.split('```')[1].split('```')[0].strip()
                
                result = json.loads(json_str)
                return result
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "is_correct": False,
                    "corrected": sentence,
                    "explanation": response,
                    "tips": ["Review the explanation above"],
                    "confidence": 50
                }
        except Exception as e:
            logger.error(f"Grammar check error: {e}")
            raise
    
    async def generate_conversation(
        self,
        context: str,
        user_message: str,
        conversation_history: List[Dict] = None,
        scenario: Optional[str] = None
    ) -> str:
        """
        Generate conversational response for language learning
        
        Args:
            context: Learning context (e.g., "hotel check-in", "restaurant")
            user_message: User's message in German
            conversation_history: Previous messages
            scenario: Optional scenario description
        
        Returns:
            AI response in German
        """
        # For voice chat, use concise responses
        if context == "voice_chat":
            system_prompt = """You are a friendly German conversation partner. 
Respond in German with SHORT, natural replies (maximum 2-3 sentences).
Keep it simple and conversational. No long explanations."""
        else:
            system_prompt = f"""You are a friendly German conversation partner helping someone learn German.

Context: {context}
{f'Scenario: {scenario}' if scenario else ''}

Guidelines:
- Respond naturally in German
- Match the user's language level
- Gently correct mistakes by using correct forms in your response
- Keep responses conversational and encouraging
- Use vocabulary appropriate for the context
- If user makes mistakes, model correct usage naturally"""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 3 exchanges
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        response = await self.chat(messages)
        return response.get('message', {}).get('content', '')
    
    async def generate_scenario(
        self,
        scenario_type: str,
        user_level: str,
        interests: List[str] = None
    ) -> Dict:
        """
        Generate a learning scenario
        
        Args:
            scenario_type: Type of scenario (hotel, restaurant, office, etc.)
            user_level: CEFR level
            interests: User interests to personalize
        
        Returns:
            Dict with scenario details
        """
        interests_str = f" User interests: {', '.join(interests)}" if interests else ""
        
        system_prompt = f"""Create a German language learning scenario.
Level: {user_level}
Type: {scenario_type}
{interests_str}

Respond in JSON format with:
- "title": scenario title
- "description": brief description
- "setting": where it takes place
- "characters": list of character names and roles
- "objectives": list of learning objectives
- "vocabulary": list of key words/phrases
- "difficulty": 1-5 rating"""

        prompt = f"Generate a {scenario_type} scenario for {user_level} level"
        
        try:
            response = await self.generate_with_cache(prompt, system_prompt, cache_ttl=3600)
            
            # Parse JSON
            json_str = response
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Scenario generation error: {e}")
            # Return fallback scenario
            return {
                "title": f"{scenario_type.title()} Practice",
                "description": f"Practice German in a {scenario_type} setting",
                "setting": scenario_type,
                "characters": ["AI Assistant"],
                "objectives": ["Practice conversation", "Learn vocabulary"],
                "vocabulary": [],
                "difficulty": 3
            }

# Global Ollama client instance
ollama_client = OllamaClient()

async def get_ollama() -> OllamaClient:
    """Dependency for FastAPI routes"""
    return ollama_client
