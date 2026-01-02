# Scenarios AI Enhancement Strategy

## Current State Analysis

### What's Already AI-Powered ✅
1. **Character Dialogue** - AI generates NPC responses in real-time
2. **Conversation Flow** - Streaming AI responses via SSE
3. **Personality System** - Characters have AI-driven personalities
4. **Emotion Tracking** - Character emotions change based on conversation

### What's Database-Driven (Static) ❌
1. **Scenario Creation** - All scenarios are pre-seeded in MongoDB
2. **Objectives** - Fixed objectives with keyword matching
3. **Difficulty Levels** - Manually assigned per scenario
4. **Character Personalities** - Pre-defined, not adaptive
5. **Branching Paths** - Pre-scripted dialogue branches

## Comparison with Other Features

### Vocabulary System (Fully AI-Powered) ✅
- AI generates words on-demand based on user level
- Personalized to user's journey and progress
- Saved to DB only after user interaction
- Dynamic difficulty adjustment

### Quiz System (Fully AI-Powered) ✅
- AI generates questions in real-time
- Adapts to user's level and topic
- No pre-seeded questions needed
- Cached for performance but generated first

### Scenarios (Hybrid - Needs More AI) ⚠️
- **Current**: Pre-seeded scenarios from DB
- **AI Usage**: Only dialogue generation
- **Problem**: Limited variety, static content

## Proposed AI Enhancements

### Phase 1: AI-Generated Scenarios (High Priority)
**Goal**: Generate scenarios on-demand like vocabulary/quiz

**Implementation**:
```python
# New endpoint: /api/v1/scenarios/generate
async def generate_scenario(
    category: str,  # restaurant, hotel, shopping, etc.
    level: str,     # a1, a2, b1, b2, c1, c2
    user_interests: List[str] = None
):
    """
    Use AI to generate a complete scenario:
    - Name and description
    - Character with personality
    - Objectives based on level
    - Context and setting
    """
    prompt = f"""
    Generate a German learning scenario for CEFR level {level.upper()}.
    Category: {category}
    
    Create:
    1. Scenario name (German + English)
    2. Description of situation
    3. Character (name, role, personality)
    4. 3-5 learning objectives
    5. Initial greeting
    
    Make it realistic and culturally appropriate.
    """
    
    # Use Mistral 7B for scenario generation
    scenario_data = await ollama_client.generate(prompt)
    
    # Save to DB for caching
    # Return to user
```

**Benefits**:
- Infinite variety of scenarios
- Personalized to user interests
- Always fresh content
- Adapts to user's journey

### Phase 2: Dynamic Objectives (Medium Priority)
**Goal**: AI evaluates conversation for objective completion

**Current Problem**:
- Keyword matching is rigid
- "Bestellen Sie ein Getränk" only checks for keywords like "Kaffee", "Tee"
- Misses valid completions

**AI Solution**:
```python
async def check_objective_completion(
    objective: str,
    conversation_history: List[Message],
    user_level: str
):
    """
    Use AI to determine if objective was met
    """
    prompt = f"""
    Objective: {objective}
    User level: {user_level}
    
    Conversation:
    {format_conversation(conversation_history)}
    
    Did the user complete this objective? (yes/no)
    Explain why.
    """
    
    result = await ollama_client.generate(prompt)
    return result.completed, result.explanation
```

**Benefits**:
- More accurate objective tracking
- Accepts creative solutions
- Better feedback to users

### Phase 3: Adaptive Difficulty (Medium Priority)
**Goal**: AI adjusts scenario difficulty in real-time

**Implementation**:
```python
async def adjust_scenario_difficulty(
    conversation_state: ConversationState,
    user_performance: dict
):
    """
    Monitor user performance and adjust:
    - Character speech complexity
    - Vocabulary level
    - Conversation speed
    - Hints frequency
    """
    
    if user_performance['struggling']:
        # Simplify character responses
        # Provide more hints
        # Use easier vocabulary
    elif user_performance['excelling']:
        # Increase complexity
        # Add unexpected situations
        # Use advanced vocabulary
```

**Benefits**:
- Personalized learning experience
- Keeps users in "flow state"
- Better engagement

### Phase 4: Intelligent Branching (Low Priority)
**Goal**: AI creates dynamic dialogue branches

**Current**: Pre-scripted branches in DB
**AI Solution**: Generate branches based on user input

```python
async def generate_dialogue_branch(
    user_message: str,
    scenario_context: dict,
    character: Character
):
    """
    AI decides:
    - How character should respond
    - What new branches to create
    - How to guide toward objectives
    """
    
    # AI analyzes user intent
    # Generates appropriate response
    # Creates new conversation paths
```

### Phase 5: Scenario Recommendations (Low Priority)
**Goal**: AI suggests scenarios based on user history

```python
async def recommend_scenarios(
    user_id: str,
    completed_scenarios: List[str],
    weak_areas: List[str]
):
    """
    AI analyzes:
    - User's completed scenarios
    - Grammar mistakes
    - Vocabulary gaps
    - Journey goals
    
    Recommends:
    - Next best scenario
    - Focus areas
    - Difficulty level
    """
```

## Implementation Priority

### Immediate (This Session)
1. ✅ Fix filter buttons (hide for Student journey)
2. ✅ Create comprehensive scenario seed (30 scenarios for A1-A2)
3. 🔄 Add B1-C2 scenarios (45 more scenarios)

### Next Session
1. Implement AI scenario generation endpoint
2. Add dynamic objective checking
3. Test AI-generated vs static scenarios

### Future
1. Adaptive difficulty system
2. Intelligent branching
3. Scenario recommendations

## Technical Stack for AI Features

### Models to Use
- **Mistral 7B**: Scenario generation, objective checking
- **Gemma 2:9b**: Grammar analysis, feedback
- **Llama 3.2:3b**: Quick responses, simple tasks

### Caching Strategy
- Generate with AI first time
- Cache in MongoDB for reuse
- Regenerate periodically for freshness
- User can request "new version"

## Expected Impact

### User Experience
- 📈 Infinite scenario variety
- 🎯 Better objective tracking
- 🔄 Adaptive learning
- 💡 Personalized content

### System Performance
- First generation: 2-3 seconds (AI)
- Cached scenarios: <100ms (DB)
- Hybrid approach: Best of both worlds

## Next Steps

1. Complete scenario seeding (75 total scenarios)
2. Design AI generation API
3. Implement and test
4. Gather user feedback
5. Iterate and improve
