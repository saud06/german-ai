"""
AI-powered conversation endpoints using Ollama
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import logging
from ..ollama_client import get_ollama, OllamaClient
from ..security import auth_dep
from ..db import get_db
from ..config import settings
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai")

# Request/Response Models
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = "general conversation"
    scenario: Optional[str] = None
    conversation_history: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    response: str
    context: str
    timestamp: str

class GrammarCheckRequest(BaseModel):
    sentence: str
    user_level: Optional[str] = "B1"

class GrammarCheckResponse(BaseModel):
    is_correct: bool
    corrected: str
    explanation: str
    tips: List[str]
    confidence: int
    source: str

class ScenarioRequest(BaseModel):
    scenario_type: str  # hotel, restaurant, office, shop, social
    user_level: Optional[str] = "B1"
    interests: Optional[List[str]] = None

@router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    payload: ChatRequest,
    ollama: OllamaClient = Depends(get_ollama),
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    AI-powered German conversation
    
    Requires ENABLE_AI_CONVERSATION=true in settings
    """
    if not settings.ENABLE_AI_CONVERSATION:
        raise HTTPException(
            status_code=503,
            detail="AI conversation feature is not enabled. Set ENABLE_AI_CONVERSATION=true"
        )
    
    if not ollama.is_available:
        raise HTTPException(
            status_code=503,
            detail="Ollama service is not available. Please ensure Ollama is running and model is pulled."
        )
    
    try:
        # Convert conversation history to dict format
        history = []
        if payload.conversation_history:
            history = [{"role": msg.role, "content": msg.content} for msg in payload.conversation_history]
        
        # Generate response
        response = await ollama.generate_conversation(
            context=payload.context,
            user_message=payload.message,
            conversation_history=history,
            scenario=payload.scenario
        )
        
        # Save conversation to database
        conversation_doc = {
            "user_id": user_id,
            "context": payload.context,
            "scenario": payload.scenario,
            "user_message": payload.message,
            "ai_response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        await db.ai_conversations.insert_one(conversation_doc)
        
        return ChatResponse(
            response=response,
            context=payload.context,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"AI chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def ai_chat_stream(
    payload: ChatRequest,
    ollama: OllamaClient = Depends(get_ollama),
    user_id: str = Depends(auth_dep)
):
    """
    Streaming AI conversation for real-time responses
    """
    if not settings.ENABLE_AI_CONVERSATION:
        raise HTTPException(status_code=503, detail="AI conversation not enabled")
    
    if not ollama.is_available:
        raise HTTPException(status_code=503, detail="Ollama not available")
    
    async def generate():
        try:
            # Prepare messages
            system_prompt = f"""You are a friendly German conversation partner.
Context: {payload.context}
{f'Scenario: {payload.scenario}' if payload.scenario else ''}

Respond naturally in German, matching the user's level."""
            
            messages = [{"role": "system", "content": system_prompt}]
            
            if payload.conversation_history:
                messages.extend([{"role": msg.role, "content": msg.content} for msg in payload.conversation_history])
            
            messages.append({"role": "user", "content": payload.message})
            
            # Stream response
            async for chunk in await ollama.chat(messages, stream=True):
                content = chunk.get('message', {}).get('content', '')
                if content:
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            yield "data: [DONE]\n\n"
        
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@router.post("/grammar/check", response_model=GrammarCheckResponse)
async def ai_grammar_check(
    payload: GrammarCheckRequest,
    ollama: OllamaClient = Depends(get_ollama),
    user_id: str = Depends(auth_dep)
):
    """
    AI-powered grammar checking
    
    More intelligent than rule-based checking
    """
    if not settings.ENABLE_AI_CONVERSATION:
        raise HTTPException(status_code=503, detail="AI features not enabled")
    
    if not ollama.is_available:
        raise HTTPException(status_code=503, detail="Ollama not available")
    
    try:
        result = await ollama.check_grammar(
            sentence=payload.sentence,
            user_level=payload.user_level
        )
        
        return GrammarCheckResponse(
            is_correct=result.get('is_correct', False),
            corrected=result.get('corrected', payload.sentence),
            explanation=result.get('explanation', ''),
            tips=result.get('tips', []),
            confidence=result.get('confidence', 50),
            source="ollama"
        )
    
    except Exception as e:
        logger.error(f"AI grammar check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scenario/generate")
async def generate_scenario(
    payload: ScenarioRequest,
    ollama: OllamaClient = Depends(get_ollama),
    user_id: str = Depends(auth_dep)
):
    """
    Generate personalized learning scenario using AI
    """
    if not settings.ENABLE_LIFE_SIMULATION:
        raise HTTPException(status_code=503, detail="Life simulation not enabled")
    
    if not ollama.is_available:
        raise HTTPException(status_code=503, detail="Ollama not available")
    
    try:
        scenario = await ollama.generate_scenario(
            scenario_type=payload.scenario_type,
            user_level=payload.user_level,
            interests=payload.interests
        )
        
        return scenario
    
    except Exception as e:
        logger.error(f"Scenario generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def ai_status(ollama: OllamaClient = Depends(get_ollama)):
    """
    Check AI service status
    """
    return {
        "ollama_available": ollama.is_available,
        "ollama_host": ollama.host,
        "ollama_model": ollama.model,
        "features": {
            "conversation": settings.ENABLE_AI_CONVERSATION,
            "voice": settings.ENABLE_VOICE_FEATURES,
            "simulation": settings.ENABLE_LIFE_SIMULATION
        }
    }

@router.get("/conversation/history")
async def get_conversation_history(
    limit: int = 20,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """
    Get user's AI conversation history
    """
    try:
        conversations = await db.ai_conversations.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        # Convert ObjectId to string
        for conv in conversations:
            conv['_id'] = str(conv['_id'])
        
        return {"conversations": conversations, "count": len(conversations)}
    
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
