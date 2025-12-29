"""
Voice conversation endpoints (STT + LLM + TTS)
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from ..whisper_client import whisper_client, get_whisper, WhisperClient
from ..piper_client import piper_client, get_piper, PiperClient
from ..ollama_client import ollama_client, get_ollama, OllamaClient
from ..config import settings
from ..security import auth_dep, get_current_user_id
from ..middleware.subscription import require_ai_access, track_ai_usage_minutes
from ..db import get_db
import logging
import base64

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class TranscribeRequest(BaseModel):
    audio_base64: str
    language: Optional[str] = "de"

class TranscribeResponse(BaseModel):
    text: str
    language: str
    confidence: Optional[float] = None

class SynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = None

class SynthesizeResponse(BaseModel):
    audio_base64: str
    duration: Optional[float] = None

class VoiceConversationRequest(BaseModel):
    audio_base64: str
    context: str = "general"
    conversation_history: Optional[List[dict]] = None
    use_fast_model: bool = True  # Use fast model for voice

class VoiceConversationResponse(BaseModel):
    transcribed_text: str
    ai_response_text: str
    ai_response_audio: str
    corrected_text: Optional[str] = None

class VoiceStatusResponse(BaseModel):
    whisper_available: bool
    piper_available: bool
    voice_features_enabled: bool
    whisper_model: str
    piper_voice: str

# Endpoints

@router.get("/status", response_model=VoiceStatusResponse)
async def voice_status():
    """Get voice pipeline status"""
    return VoiceStatusResponse(
        whisper_available=whisper_client.is_available,
        piper_available=piper_client.is_available,
        voice_features_enabled=settings.ENABLE_VOICE_FEATURES,
        whisper_model=settings.WHISPER_MODEL,
        piper_voice=settings.PIPER_VOICE
    )

@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    request: TranscribeRequest,
    whisper: WhisperClient = Depends(get_whisper),
    _user=Depends(auth_dep)
):
    """
    Transcribe audio to text using Whisper
    """
    if not settings.ENABLE_VOICE_FEATURES:
        raise HTTPException(status_code=403, detail="Voice features are disabled")
    
    if not whisper.is_available:
        raise HTTPException(status_code=503, detail="Whisper STT service is not available")
    
    try:
        result = await whisper.transcribe_base64(
            request.audio_base64,
            language=request.language
        )
        
        return TranscribeResponse(
            text=result.get('text', ''),
            language=request.language,
            confidence=result.get('confidence')
        )
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_speech(
    request: SynthesizeRequest,
    piper: PiperClient = Depends(get_piper),
    _user=Depends(auth_dep)
):
    """
    Synthesize text to speech using Piper
    """
    if not settings.ENABLE_VOICE_FEATURES:
        raise HTTPException(status_code=403, detail="Voice features are disabled")
    
    if not piper.is_available:
        raise HTTPException(status_code=503, detail="Piper TTS service is not available")
    
    try:
        audio_base64 = await piper.synthesize_to_base64(
            request.text,
            voice=request.voice
        )
        
        return SynthesizeResponse(
            audio_base64=audio_base64,
            duration=None  # TODO: Calculate duration
        )
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

@router.post("/conversation", response_model=VoiceConversationResponse)
async def voice_conversation(
    request: VoiceConversationRequest,
    whisper: WhisperClient = Depends(get_whisper),
    piper: PiperClient = Depends(get_piper),
    ollama: OllamaClient = Depends(get_ollama),
    user_id: str = Depends(require_ai_access),
    db = Depends(get_db)
):
    """
    Complete voice conversation pipeline: STT → LLM → TTS
    
    Flow:
    1. Transcribe user's audio (Whisper)
    2. Check grammar and get AI response (Ollama)
    3. Synthesize AI response to audio (Piper)
    """
    if not settings.ENABLE_VOICE_FEATURES:
        raise HTTPException(status_code=403, detail="Voice features are disabled")
    
    # Ensure services are initialized (workaround for lifespan not running)
    if not whisper.is_available:
        await whisper.initialize()
    if not piper.is_available:
        await piper.initialize()
    if not ollama.is_available:
        await ollama.initialize()
    
    if not whisper.is_available:
        raise HTTPException(status_code=503, detail="Whisper STT not available")
    
    if not piper.is_available:
        raise HTTPException(status_code=503, detail="Piper TTS not available")
    
    if not ollama.is_available:
        raise HTTPException(status_code=503, detail="Ollama LLM not available")
    
    try:
        import time
        start_time = time.time()
        
        # Step 1: Transcribe audio
        print("🎤 Transcribing audio...")  # Using print for visibility
        logger.info("🎤 Transcribing audio...")
        transcribe_start = time.time()
        # Force German language to avoid misdetection
        transcription = await whisper.transcribe_base64(request.audio_base64, language="de")
        transcribed_text = transcription.get('text', '').strip()
        transcribe_time = time.time() - transcribe_start
        
        if not transcribed_text:
            raise HTTPException(status_code=400, detail="No speech detected in audio")
        
        print(f"✅ Transcribed ({transcribe_time:.2f}s): {transcribed_text}")
        print(f"   Language detected by Whisper: {transcription.get('language', 'unknown')}")
        logger.info(f"✅ Transcribed: {transcribed_text}")
        
        # Strict German-only check
        # Detect non-German characters and common non-German words
        non_german_chars = ['é', 'è', 'ê', 'ñ', 'ç', 'à', 'ò', 'ù', 'í', 'ó', 'ú', 'ã', 'õ']
        non_german_words = [
            # Spanish/Portuguese
            'cosa', 'nome', 'hola', 'como', 'está', 'agora', 'você',
            # English
            'hello', 'yes', 'please', 'thank', 'you', 'what', 'where', 'when', 'how'
        ]
        
        text_lower = transcribed_text.lower()
        
        # Check for non-German characters
        has_non_german_char = any(char in text_lower for char in non_german_chars)
        
        # Check for non-German words (whole word match to avoid false positives like "bist" containing "is")
        import re
        words_in_text = re.findall(r'\b\w+\b', text_lower)
        has_non_german_word = any(word in non_german_words for word in words_in_text)
        
        if has_non_german_char or has_non_german_word:
            print(f"⚠️ Non-German detected in: {transcribed_text}")
            # Short, firm reminder in German
            ai_response = "Bitte nur auf Deutsch sprechen!"
            audio_base64 = await piper.synthesize_to_base64(ai_response)
            return VoiceConversationResponse(
                transcribed_text=transcribed_text,
                ai_response_text=ai_response,
                ai_response_audio=audio_base64,
                corrected_text=None
            )
        
        # Step 2: Generate AI response
        print("🤖 Generating AI response...")
        logger.info("🤖 Generating AI response...")
        generate_start = time.time()
        
        # Use fast model for voice if requested
        original_model = ollama.model
        if request.use_fast_model and hasattr(settings, 'OLLAMA_MODEL_FAST'):
            ollama.model = settings.OLLAMA_MODEL_FAST
        
        print(f"Using model: {ollama.model}")
        
        # For voice chat, use optimized settings for speed
        # Use direct Ollama API for better control
        response = await ollama.client.chat(
            model=ollama.model,
            messages=[
                {"role": "system", "content": "Antworte auf Deutsch. Nur 1 kurzer Satz."},
                {"role": "user", "content": transcribed_text}
            ],
            options={
                'temperature': 1.0,  # Max temperature for fastest generation
                'num_predict': 15,  # VERY strict: 15 tokens max (~10-12 words)
                'top_p': 0.9,
                'top_k': 10,  # Even fewer choices for faster sampling
                'stop': ['\n', '.', '!', '?'],  # Stop at first sentence end
            }
        )
        ai_response = response.get('message', {}).get('content', '').strip()
        
        # Ensure it ends with punctuation
        if ai_response and ai_response[-1] not in '.!?':
            ai_response += '.'
        
        # Restore original model
        ollama.model = original_model
        generate_time = time.time() - generate_start
        
        # HARD limit: max 50 chars for voice (1 short sentence)
        if len(ai_response) > 50:
            # Find last sentence within 50 chars
            truncated = ai_response[:50]
            last_period = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
            if last_period > 15:  # If we found a sentence end
                ai_response = truncated[:last_period + 1]
            else:
                # Cut at last space
                last_space = truncated.rfind(' ')
                if last_space > 15:
                    ai_response = truncated[:last_space] + "."
                else:
                    ai_response = truncated + "."
        
        print(f"📏 Response length: {len(ai_response)} chars (limit: 50)")
        
        print(f"✅ AI response ({generate_time:.2f}s, {len(ai_response)} chars): {ai_response[:100]}...")
        logger.info(f"✅ AI response: {ai_response[:100]}...")
        
        # Step 3: Synthesize response to audio
        print("🔊 Synthesizing audio...")
        logger.info("🔊 Synthesizing audio...")
        synthesize_start = time.time()
        audio_base64 = await piper.synthesize_to_base64(ai_response)
        synthesize_time = time.time() - synthesize_start
        
        total_time = time.time() - start_time
        print(f"✅ Audio synthesized ({synthesize_time:.2f}s): {len(audio_base64)} chars")
        print(f"⏱️  Total time: {total_time:.2f}s (Transcribe: {transcribe_time:.2f}s, Generate: {generate_time:.2f}s, Synthesize: {synthesize_time:.2f}s)")
        
        logger.info("✅ Voice conversation complete!")
        
        # Track AI usage (estimate 1 minute per conversation)
        await track_ai_usage_minutes(user_id, 1, db)
        
        return VoiceConversationResponse(
            transcribed_text=transcribed_text,
            ai_response_text=ai_response,
            ai_response_audio=audio_base64,
            corrected_text=None  # TODO: Add grammar correction
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice conversation error: {e}")
        raise HTTPException(status_code=500, detail=f"Voice conversation failed: {str(e)}")

@router.post("/upload-audio", response_model=TranscribeResponse)
async def upload_audio_file(
    file: UploadFile = File(...),
    language: str = "de",
    whisper: WhisperClient = Depends(get_whisper),
    _user=Depends(auth_dep)
):
    """
    Upload audio file and transcribe
    """
    if not settings.ENABLE_VOICE_FEATURES:
        raise HTTPException(status_code=403, detail="Voice features are disabled")
    
    if not whisper.is_available:
        raise HTTPException(status_code=503, detail="Whisper STT not available")
    
    try:
        # Read audio file
        audio_data = await file.read()
        
        # Transcribe
        result = await whisper.transcribe(audio_data, language=language)
        
        return TranscribeResponse(
            text=result.get('text', ''),
            language=language,
            confidence=result.get('confidence')
        )
    except Exception as e:
        logger.error(f"Upload transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
