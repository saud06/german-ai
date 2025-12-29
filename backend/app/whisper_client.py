"""
Whisper STT client for speech-to-text transcription
"""
import httpx
import logging
from typing import Optional
from .config import settings
import base64

logger = logging.getLogger(__name__)

class WhisperClient:
    """Async Whisper client wrapper for German speech recognition"""
    
    def __init__(self):
        self.host = settings.WHISPER_HOST
        self.model = settings.WHISPER_MODEL
        self.language = settings.WHISPER_LANGUAGE
        self.is_available = False
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def initialize(self):
        """Initialize Whisper client and check availability"""
        try:
            # Check if service is reachable (405 is OK - means endpoint exists)
            response = await self.client.get(f"{self.host}/asr", timeout=5.0)
            # 405 Method Not Allowed means service is up, just doesn't accept GET
            if response.status_code in [200, 405]:
                self.is_available = True
                logger.info(f"✅ Whisper STT connected: {self.host} (model: {self.model})")
            else:
                logger.warning(f"⚠️  Whisper responded with status {response.status_code}")
                self.is_available = False
        except Exception as e:
            logger.error(f"❌ Whisper connection failed: {e}")
            self.is_available = False
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> dict:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio file bytes (WAV, MP3, etc.)
            language: Language code (default: de)
            task: "transcribe" or "translate"
        
        Returns:
            Dict with transcription results
        """
        if not self.is_available:
            raise Exception("Whisper is not available")
        
        lang = language or self.language
        
        try:
            # Prepare multipart form data
            files = {
                'audio_file': ('audio.wav', audio_data, 'audio/wav')
            }
            
            # Use query parameters for language and task
            params = {
                'task': task,
                'language': lang,
                'output': 'json',
                'encode': 'true'
            }
            
            response = await self.client.post(
                f"{self.host}/asr",
                files=files,
                params=params
            )
            
            if response.status_code == 200:
                # Log raw response for debugging
                logger.info(f"Whisper response status: {response.status_code}")
                logger.debug(f"Whisper response text: {response.text[:200]}")
                
                # Try to parse as JSON first
                try:
                    result = response.json()
                    logger.info(f"✅ Transcription successful: {len(result.get('text', ''))} chars")
                    return result
                except Exception as json_error:
                    # If JSON parsing fails, treat as plain text
                    logger.warning(f"Failed to parse JSON, treating as plain text: {json_error}")
                    text_result = response.text.strip()
                    result = {'text': text_result}
                    logger.info(f"✅ Transcription successful: {len(result.get('text', ''))} chars")
                    return result
            else:
                logger.error(f"Whisper error: {response.status_code} - {response.text}")
                raise Exception(f"Whisper transcription failed: {response.status_code}")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Whisper HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Whisper HTTP error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Whisper transcription error: {type(e).__name__}: {e}")
            raise
    
    async def transcribe_base64(
        self,
        audio_base64: str,
        language: Optional[str] = None
    ) -> dict:
        """
        Transcribe base64-encoded audio
        
        Args:
            audio_base64: Base64-encoded audio data
            language: Language code (default: de)
        
        Returns:
            Dict with transcription results
        """
        try:
            # Decode base64
            audio_data = base64.b64decode(audio_base64)
            return await self.transcribe(audio_data, language)
        except Exception as e:
            logger.error(f"Base64 transcription error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if Whisper service is healthy"""
        try:
            response = await self.client.get(f"{self.host}/asr", timeout=5.0)
            # 405 is OK - service is up, just doesn't accept GET on /asr
            return response.status_code in [200, 405]
        except:
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Global Whisper client instance
whisper_client = WhisperClient()

async def get_whisper() -> WhisperClient:
    """Dependency for FastAPI routes"""
    return whisper_client
