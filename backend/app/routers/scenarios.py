"""
API routes for life simulation scenarios
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List, Optional
from pydantic import BaseModel
import json
import asyncio

from app.models.scenario import (
    Scenario,
    ScenarioListResponse,
    ScenarioDetailResponse
)
from app.models.conversation_state import (
    ConversationState,
    ConversationStateResponse,
    ConversationMessageRequest,
    ConversationMessageResponse
)
from app.db import get_db
from app.security import auth_dep, get_current_user_id
from app.services.scenario_service import ScenarioService
from app.services.conversation_engine import ConversationEngine
from app.ollama_client import get_ollama
from app.piper_client import piper_client
from app.whisper_client import whisper_client
from app.middleware.subscription import require_scenario_access, track_scenario_usage, require_ai_access, track_ai_usage_minutes
from app.utils.journey_utils import get_user_journey_level, get_level_range_for_content

router = APIRouter(prefix="/api/v1/scenarios", tags=["scenarios"])


class VoiceMessageRequest(BaseModel):
    audio_base64: str


@router.get("/", response_model=ScenarioListResponse)
async def list_scenarios(
    difficulty: Optional[str] = None,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Get all available scenarios - filtered by user's journey level if no difficulty specified"""
    # If no difficulty filter, use user's journey level
    if not difficulty:
        journey_level = await get_user_journey_level(db, user_id)
        if journey_level:
            difficulty = journey_level
    
    service = ScenarioService(db)
    scenarios = await service.get_all_scenarios(difficulty=difficulty)
    
    return ScenarioListResponse(
        scenarios=scenarios,
        total=len(scenarios)
    )


@router.get("/progress")
async def get_user_progress(
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Get user's progress on all scenarios"""
    service = ScenarioService(db)
    progress = await service.get_all_user_progress(user_id=user_id)
    
    return {"progress": progress}


@router.get("/{scenario_id}", response_model=ScenarioDetailResponse)
async def get_scenario(
    scenario_id: str,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Get scenario details"""
    service = ScenarioService(db)
    scenario = await service.get_scenario_by_id(scenario_id)
    
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )
    
    # Get user's progress on this scenario
    user_progress = await service.get_user_progress(
        user_id=user_id,
        scenario_id=scenario_id
    )
    
    return ScenarioDetailResponse(
        scenario=scenario,
        user_progress=user_progress
    )


@router.post("/{scenario_id}/start", response_model=ConversationStateResponse)
async def start_scenario(
    scenario_id: str,
    character_id: str,
    user_id: str = Depends(require_scenario_access),
    db = Depends(get_db)
):
    """Start a new scenario conversation"""
    service = ScenarioService(db)
    
    # Track scenario usage
    await track_scenario_usage(user_id, db)
    
    # Check if user already has an active conversation for this scenario
    existing_state = await service.get_conversation_state(
        user_id=user_id,
        scenario_id=scenario_id
    )
    
    if existing_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active conversation for this scenario. Complete or abandon it first."
        )
    
    # Start new conversation
    state = await service.start_scenario(
        user_id=user_id,
        scenario_id=scenario_id,
        character_id=character_id
    )
    
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario or character not found"
        )
    
    # Get scenario for response
    scenario = await service.get_scenario_by_id(scenario_id)
    character = next((c for c in scenario.characters if c.id == character_id), None)
    
    # Calculate completion stats
    objectives_completed = sum(1 for obj in state.objectives_progress if obj.completed)
    objectives_total = len(state.objectives_progress)
    completion_percentage = (objectives_completed / objectives_total * 100) if objectives_total > 0 else 0
    
    return ConversationStateResponse(
        state=state,
        scenario_name=scenario.name,
        character_name=character.name if character else "Unknown",
        objectives_completed=objectives_completed,
        objectives_total=objectives_total,
        completion_percentage=completion_percentage
    )


@router.get("/{scenario_id}/state", response_model=ConversationStateResponse)
async def get_conversation_state(
    scenario_id: str,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Get current conversation state"""
    service = ScenarioService(db)
    
    state = await service.get_conversation_state(
        user_id=user_id,
        scenario_id=scenario_id
    )
    
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active conversation found for this scenario"
        )
    
    # Get scenario and character
    scenario = await service.get_scenario_by_id(scenario_id)
    character = next((c for c in scenario.characters if c.id == state.character_id), None)
    
    # Calculate completion stats
    objectives_completed = sum(1 for obj in state.objectives_progress if obj.completed)
    objectives_total = len(state.objectives_progress)
    completion_percentage = (objectives_completed / objectives_total * 100) if objectives_total > 0 else 0
    
    return ConversationStateResponse(
        state=state,
        scenario_name=scenario.name,
        character_name=character.name if character else "Unknown",
        objectives_completed=objectives_completed,
        objectives_total=objectives_total,
        completion_percentage=completion_percentage
    )


@router.post("/{scenario_id}/message", response_model=ConversationMessageResponse)
async def send_message(
    scenario_id: str,
    request: ConversationMessageRequest,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db),
    ollama = Depends(get_ollama)
):
    """Send a message in scenario conversation"""
    service = ScenarioService(db)
    engine = ConversationEngine(ollama)
    
    # Get conversation state
    state = await service.get_conversation_state(
        user_id=user_id,
        scenario_id=scenario_id
    )
    
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active conversation found. Start the scenario first."
        )
    
    # Get scenario and character
    scenario = await service.get_scenario_by_id(scenario_id)
    character = next((c for c in scenario.characters if c.id == state.character_id), None)
    
    if not scenario or not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario or character not found"
        )
    
    # Add user message to state
    await service.add_message(state, "user", request.message)
    
    # Check objectives
    completed_objectives = engine.check_objectives(request.message, scenario, state)
    
    # Update objectives
    for obj_id in completed_objectives:
        await service.complete_objective(state, obj_id)
    
    # Generate AI response
    character_response = await engine.generate_response(
        user_message=request.message,
        scenario=scenario,
        character=character,
        state=state
    )
    
    # Add character response to state
    await service.add_message(state, "character", character_response)
    
    # Generate audio for character response
    character_audio = None
    try:
        character_audio = await piper_client.synthesize_to_base64(character_response)
    except Exception as e:
        print(f"Warning: Failed to generate audio: {e}")
    
    # Check if scenario is complete
    is_complete = engine.is_scenario_complete(scenario, state)
    if is_complete:
        await service.complete_scenario(state)
    
    # Get grammar feedback
    grammar_feedback = engine.extract_grammar_feedback(request.message)
    
    # Calculate score change
    score_change = engine.calculate_score_change(completed_objectives)
    
    # Update state in database
    await service.update_conversation_state(state)
    
    return ConversationMessageResponse(
        character_message=character_response,
        character_audio=character_audio,
        objectives_updated=completed_objectives,
        grammar_feedback=grammar_feedback,
        score_change=score_change,
        conversation_complete=is_complete
    )


@router.post("/{scenario_id}/message/stream")
async def send_message_stream(
    scenario_id: str,
    request: ConversationMessageRequest,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db),
    ollama = Depends(get_ollama)
):
    """Send a message and stream the AI response"""
    service = ScenarioService(db)
    engine = ConversationEngine(ollama)
    
    # Get conversation state
    state = await service.get_conversation_state(
        user_id=user_id,
        scenario_id=scenario_id
    )
    
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active conversation found. Start the scenario first."
        )
    
    # Get scenario and character
    scenario = await service.get_scenario_by_id(scenario_id)
    character = next((c for c in scenario.characters if c.id == state.character_id), None)
    
    if not scenario or not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario or character not found"
        )
    
    # Add user message to state
    await service.add_message(state, "user", request.message)
    
    # Check objectives
    completed_objectives = engine.check_objectives(request.message, scenario, state)
    
    # Update objectives
    for obj_id in completed_objectives:
        await service.complete_objective(state, obj_id)
    
    # Stream generator
    async def generate_stream():
        try:
            # Send initial metadata
            yield f"data: {json.dumps({'type': 'metadata', 'objectives_completed': completed_objectives, 'score_change': engine.calculate_score_change(completed_objectives)})}\n\n"
            
            # Generate and stream AI response
            full_response = ""
            async for chunk in engine.generate_response_stream(
                user_message=request.message,
                scenario=scenario,
                character=character,
                state=state
            ):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
                await asyncio.sleep(0.01)  # Small delay for smoother streaming
            
            # Add character response to state
            await service.add_message(state, "character", full_response)
            
            # Check if scenario is complete
            is_complete = engine.is_scenario_complete(scenario, state)
            if is_complete:
                await service.complete_scenario(state)
            
            # Update state in database
            await service.update_conversation_state(state)
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'complete', 'conversation_complete': is_complete})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/{scenario_id}/complete")
async def complete_scenario(
    scenario_id: str,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db)
):
    """Manually complete/abandon a scenario"""
    service = ScenarioService(db)
    
    state = await service.get_conversation_state(
        user_id=user_id,
        scenario_id=scenario_id
    )
    
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active conversation found"
        )
    
    await service.complete_scenario(state)
    await service.update_conversation_state(state)
    
    return {"message": "Scenario completed", "final_score": state.score}


@router.post("/{scenario_id}/voice-message")
async def send_voice_message(
    scenario_id: str,
    request: VoiceMessageRequest,
    user_id: str = Depends(auth_dep),
    db = Depends(get_db),
    ollama = Depends(get_ollama)
):
    """
    Send a voice message in a scenario conversation.
    Flow: Audio → Transcribe → Process → Generate Response → Synthesize → Return
    """
    service = ScenarioService(db)
    engine = ConversationEngine(ollama)
    
    # Get conversation state
    state = await service.get_conversation_state(
        user_id=user_id,
        scenario_id=scenario_id
    )
    
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active conversation found. Start the scenario first."
        )
    
    # Get scenario and character
    scenario = await service.get_scenario_by_id(scenario_id)
    character = next((c for c in scenario.characters if c.id == state.character_id), None)
    
    if not scenario or not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario or character not found"
        )
    
    # 1. Transcribe audio to text
    transcription_result = await whisper_client.transcribe_base64(request.audio_base64, language="de")
    user_message = transcription_result.get('text', '').strip()
    
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not transcribe audio"
        )
    
    # 2. Add user message to state
    await service.add_message(state, "user", user_message)
    
    # 3. Check objectives
    completed_objectives = engine.check_objectives(user_message, scenario, state)
    
    # 4. Update objectives
    for obj_id in completed_objectives:
        await service.complete_objective(state, obj_id)
    
    # 5. Generate AI response
    character_response = await engine.generate_response(
        user_message=user_message,
        scenario=scenario,
        character=character,
        state=state
    )
    
    # 6. Add character response to state
    await service.add_message(state, "character", character_response)
    
    # 7. Generate audio for character response
    character_audio = None
    try:
        character_audio = await piper_client.synthesize_to_base64(character_response)
    except Exception as e:
        print(f"Warning: Failed to generate audio: {e}")
    
    # 8. Check if scenario is complete
    is_complete = engine.is_scenario_complete(scenario, state)
    if is_complete:
        await service.complete_scenario(state)
    
    # 9. Get grammar feedback
    grammar_feedback = engine.extract_grammar_feedback(user_message)
    
    # 10. Calculate score change
    score_change = engine.calculate_score_change(completed_objectives)
    
    # 11. Update state in database
    await service.update_conversation_state(state)
    
    return {
        "transcribed_text": user_message,
        "character_message": character_response,
        "character_audio": character_audio,
        "objectives_updated": completed_objectives,
        "grammar_feedback": grammar_feedback,
        "score_change": score_change,
        "conversation_complete": is_complete
    }

# Checkpoint endpoints

@router.post("/{scenario_id}/checkpoint")
async def create_checkpoint(
    scenario_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Create a checkpoint in current scenario"""
    from bson import ObjectId
    from datetime import datetime
    from ..models.conversation_state import Checkpoint
    
    # Get active conversation
    conversation = await db.conversation_states.find_one({
        "user_id": user_id,
        "scenario_id": scenario_id,
        "status": "active"
    })
    
    if not conversation:
        raise HTTPException(status_code=404, detail="No active conversation found")
    
    # Create checkpoint
    checkpoint_id = str(ObjectId())
    checkpoint = Checkpoint(
        checkpoint_id=checkpoint_id,
        step=conversation.get("current_step", 0),
        score=conversation.get("score", 0),
        objectives_completed=[
            obj["objective_id"] 
            for obj in conversation.get("objectives_progress", []) 
            if obj.get("completed")
        ],
        messages_count=len(conversation.get("messages", [])),
        metadata={"total_duration": conversation.get("total_duration_seconds", 0)}
    )
    
    # Add checkpoint to conversation
    await db.conversation_states.update_one(
        {"_id": conversation["_id"]},
        {
            "$push": {"checkpoints": checkpoint.model_dump()},
            "$set": {"last_checkpoint_id": checkpoint_id}
        }
    )
    
    return {
        "checkpoint_id": checkpoint_id,
        "created_at": checkpoint.created_at,
        "step": checkpoint.step,
        "score": checkpoint.score
    }


@router.post("/{scenario_id}/checkpoint/{checkpoint_id}/restore")
async def restore_checkpoint(
    scenario_id: str,
    checkpoint_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Restore conversation to a checkpoint"""
    # Get conversation
    conversation = await db.conversation_states.find_one({
        "user_id": user_id,
        "scenario_id": scenario_id
    })
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Find checkpoint
    checkpoint = None
    for cp in conversation.get("checkpoints", []):
        if cp["checkpoint_id"] == checkpoint_id:
            checkpoint = cp
            break
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    # Restore state
    messages = conversation.get("messages", [])[:checkpoint["messages_count"]]
    
    await db.conversation_states.update_one(
        {"_id": conversation["_id"]},
        {
            "$set": {
                "current_step": checkpoint["step"],
                "score": checkpoint["score"],
                "messages": messages,
                "status": "active",
                "last_checkpoint_id": checkpoint_id
            }
        }
    )
    
    return {
        "success": True,
        "checkpoint_id": checkpoint_id,
        "restored_to_step": checkpoint["step"]
    }


@router.post("/{scenario_id}/pause")
async def pause_scenario(
    scenario_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Pause current scenario"""
    from datetime import datetime
    
    result = await db.conversation_states.update_one(
        {
            "user_id": user_id,
            "scenario_id": scenario_id,
            "status": "active"
        },
        {
            "$set": {
                "status": "paused",
                "paused_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="No active conversation found")
    
    return {"success": True, "status": "paused"}


@router.post("/{scenario_id}/resume")
async def resume_scenario(
    scenario_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Resume paused scenario"""
    from datetime import datetime
    
    result = await db.conversation_states.update_one(
        {
            "user_id": user_id,
            "scenario_id": scenario_id,
            "status": "paused"
        },
        {
            "$set": {
                "status": "active",
                "last_activity": datetime.utcnow()
            },
            "$unset": {"paused_at": ""}
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="No paused conversation found")
    
    return {"success": True, "status": "active"}
