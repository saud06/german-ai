"""
Conversation engine for scenario-based AI conversations
Handles context-aware responses and objective tracking
"""

import re
from typing import List, Tuple, Optional
from app.models.scenario import Scenario, Character, Objective
from app.models.conversation_state import ConversationState
from app.ollama_client import OllamaClient


class ConversationEngine:
    """Engine for managing scenario conversations"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
    
    def build_system_prompt(
        self,
        scenario: Scenario,
        character: Character,
        state: ConversationState
    ) -> str:
        """Build system prompt for AI character"""
        
        # Get uncompleted objectives
        uncompleted_objectives = []
        for obj_progress in state.objectives_progress:
            objective = next(
                (obj for obj in scenario.objectives if obj.id == obj_progress.objective_id),
                None
            )
            if objective and not obj_progress.completed:
                uncompleted_objectives.append(objective.description)
        
        prompt = f"""Du bist {character.name}, {character.role}.
Persönlichkeit: {character.personality}

Szenario: {scenario.name}

REGELN:
1. Antworte NUR auf Deutsch
2. MAXIMAL 1 kurzer Satz (10-15 Wörter)
3. Bleibe in deiner Rolle
4. Verstehe fehlerhafte Sätze
5. Reagiere natürlich

AKTUELLE ZIELE: {', '.join(uncompleted_objectives[:2]) if uncompleted_objectives else 'Gespräch führen'}"""
        
        return prompt
    
    def build_conversation_history(self, state: ConversationState) -> List[dict]:
        """Build conversation history for AI context"""
        # Get last 4 messages for context (faster processing)
        recent_messages = state.messages[-4:]
        
        history = []
        for msg in recent_messages:
            history.append({
                "role": "assistant" if msg.role == "character" else "user",
                "content": msg.content
            })
        
        return history
    
    async def generate_response(
        self,
        user_message: str,
        scenario: Scenario,
        character: Character,
        state: ConversationState
    ) -> str:
        """Generate AI character response"""
        
        # Build system prompt
        system_prompt = self.build_system_prompt(scenario, character, state)
        
        # Build conversation history
        history = self.build_conversation_history(state)
        
        # Build conversation messages properly for chat API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Use chat API with strict limits for short responses
        response = await self.ollama.client.chat(
            model=self.ollama.model,
            messages=messages,
            options={
                'temperature': 0.7,
                'num_predict': 25,  # Strict limit for short responses
                'top_p': 0.9,
                'top_k': 40,
                'repeat_penalty': 1.2,  # Higher to avoid repetition
                'num_ctx': 1024,
                'stop': ['\n', 'Gast:', 'User:', '\n\n'],  # Stop tokens to prevent format leaking
            }
        )
        
        ai_response = response.get('message', {}).get('content', '').strip()
        
        # Clean up any leaked format
        if 'Gast:' in ai_response:
            ai_response = ai_response.split('Gast:')[0].strip()
        if character.name + ':' in ai_response:
            ai_response = ai_response.replace(character.name + ':', '').strip()
        
        # Ensure response ends with punctuation
        if ai_response and ai_response[-1] not in '.!?':
            ai_response += '.'
        
        # Enforce maximum length (truncate if too long)
        words = ai_response.split()
        if len(words) > 20:
            ai_response = ' '.join(words[:20]) + '...'
        
        return ai_response
    
    async def generate_response_stream(
        self,
        user_message: str,
        scenario: Scenario,
        character: Character,
        state: ConversationState
    ):
        """Generate AI character response with streaming"""
        
        # Build system prompt
        system_prompt = self.build_system_prompt(scenario, character, state)
        
        # Build conversation history
        history = self.build_conversation_history(state)
        
        # Build conversation messages properly for chat API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Use chat API with streaming and strict limits
        stream = await self.ollama.client.chat(
            model=self.ollama.model,
            messages=messages,
            options={
                'temperature': 0.7,
                'num_predict': 25,  # Strict limit for short responses
                'top_p': 0.9,
                'top_k': 40,
                'repeat_penalty': 1.2,  # Higher to avoid repetition
                'num_ctx': 1024,
                'stop': ['\n', 'Gast:', 'User:', '\n\n'],  # Stop tokens
            },
            stream=True
        )
        
        # Stream the response with format cleaning
        word_count = 0
        async for chunk in stream:
            if 'message' in chunk and 'content' in chunk['message']:
                content = chunk['message']['content']
                if content:
                    # Stop if we see format leaking
                    if 'Gast:' in content or character.name + ':' in content:
                        break
                    # Enforce word limit during streaming
                    word_count += len(content.split())
                    if word_count > 20:
                        break
                    yield content
    
    def check_objectives(
        self,
        user_message: str,
        scenario: Scenario,
        state: ConversationState
    ) -> List[str]:
        """Check if user message completes any objectives"""
        completed_objective_ids = []
        
        user_message_lower = user_message.lower()
        
        for obj_progress in state.objectives_progress:
            if obj_progress.completed:
                continue
            
            # Find the objective
            objective = next(
                (obj for obj in scenario.objectives if obj.id == obj_progress.objective_id),
                None
            )
            
            if not objective:
                continue
            
            # Check if any keywords match
            keywords_found = 0
            for keyword in objective.keywords:
                keyword_lower = keyword.lower()
                # Use word boundaries for better matching
                pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                if re.search(pattern, user_message_lower):
                    keywords_found += 1
            
            # If at least one keyword found, mark as completed
            if keywords_found > 0:
                completed_objective_ids.append(objective.id)
                continue
            
            # Special handling for objectives that require answering questions
            # If the objective description contains "fragen" or "antwort" and user has sent multiple messages
            # after other objectives are completed, mark it as complete
            obj_desc_lower = objective.description.lower()
            if any(word in obj_desc_lower for word in ['fragen', 'antwort', 'question']):
                # Count how many other objectives are already completed
                completed_count = sum(1 for op in state.objectives_progress if op.completed)
                total_messages = len(state.messages)
                
                # If most objectives are done and user has been actively participating (5+ messages)
                # mark this objective as complete
                if completed_count >= len(state.objectives_progress) - 1 and total_messages >= 5:
                    # Check if user message is substantive (more than just "ja" or "nein")
                    if len(user_message.split()) >= 2 or any(word in user_message_lower for word in ['ja', 'nein', 'ich', 'bin', 'der', 'die', 'das']):
                        completed_objective_ids.append(objective.id)
        
        return completed_objective_ids
    
    def extract_grammar_feedback(self, user_message: str) -> Optional[str]:
        """Extract basic grammar feedback (simple rules)"""
        feedback = []
        
        # Check for common mistakes
        # This is a simple implementation - could be enhanced with proper grammar checking
        
        # Check for missing articles
        if re.search(r'\b(möchte|will|brauche)\s+(Wasser|Bier|Kaffee)\b', user_message, re.IGNORECASE):
            feedback.append("Tipp: Vergiss nicht den Artikel! 'ein Wasser', 'ein Bier', 'einen Kaffee'")
        
        # Check for informal/formal mix
        if 'du' in user_message.lower() and any(word in user_message.lower() for word in ['bitte', 'danke']):
            # In formal scenarios, should use 'Sie'
            pass  # This would need scenario context
        
        return feedback[0] if feedback else None
    
    def is_scenario_complete(
        self,
        scenario: Scenario,
        state: ConversationState
    ) -> bool:
        """Check if all required objectives are completed"""
        required_objectives = [obj for obj in scenario.objectives if obj.required]
        
        for obj in required_objectives:
            obj_progress = next(
                (op for op in state.objectives_progress if op.objective_id == obj.id),
                None
            )
            if not obj_progress or not obj_progress.completed:
                return False
        
        return True
    
    def calculate_score_change(self, objectives_completed: List[str]) -> int:
        """Calculate score change based on objectives completed"""
        return len(objectives_completed) * 20  # 20 points per objective
