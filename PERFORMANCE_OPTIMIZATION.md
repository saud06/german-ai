# Performance Optimization - Life Simulation

## Current Performance Issue

**Problem:** AI responses taking 10-12 seconds to generate  
**Expected:** 2-4 seconds for text-only responses  
**Model:** llama3.2:1b (GPU-accelerated)

---

## Analysis

### Test Results:
1. **Direct Ollama API:** ~2 seconds ✅
2. **Scenario conversation:** ~12 seconds ❌

### Root Causes:
1. **Chat API overhead** - Using chat endpoint with full context
2. **Context size** - System prompt + conversation history
3. **Token generation** - Model generating more tokens than requested
4. **Processing overhead** - Objective checking, state updates

---

## Optimizations Applied

### 1. Reduced Token Generation
```python
'num_predict': 25,  # Very short responses (1 sentence max)
```

### 2. Smaller Context Window
```python
'num_ctx': 512,  # Smaller context for faster processing
```

### 3. Limited Conversation History
```python
recent_messages = state.messages[-4:]  # Only last 4 messages
```

### 4. Shorter System Prompt
```python
"Antworte SEHR KURZ (maximal 1 Satz, 10-15 Wörter)"
```

---

## Current Configuration

### Ollama Settings:
```python
options={
    'temperature': 0.7,
    'num_predict': 25,
    'top_p': 0.9,
    'top_k': 40,
    'repeat_penalty': 1.1,
    'num_ctx': 512,
}
```

### Model:
- **Name:** llama3.2:1b
- **Location:** GPU (localhost:11435)
- **Expected speed:** 50-100 tokens/second

---

## Further Optimization Options

### Option 1: Use Generate API Instead of Chat
**Pros:**
- Faster (2s vs 12s)
- Simpler prompt
- Less overhead

**Cons:**
- Manual prompt construction
- No built-in conversation management

**Implementation:**
```python
# Instead of chat API
response = await self.ollama.client.generate(
    model=self.ollama.model,
    prompt=f"{system_prompt}\n\nUser: {user_message}\nAssistant:",
    options={'num_predict': 25}
)
```

### Option 2: Streaming Responses
**Pros:**
- User sees response immediately
- Better perceived performance

**Cons:**
- More complex frontend
- Still same total time

### Option 3: Response Caching
**Pros:**
- Instant responses for common phrases
- Reduced load

**Cons:**
- Less natural conversation
- Cache management complexity

### Option 4: Parallel Processing
**Pros:**
- Check objectives while generating
- Faster overall

**Cons:**
- More complex code
- Potential race conditions

---

## Recommended Next Steps

### Immediate (Quick Wins):
1. ✅ **Reduce num_predict to 25** - Already done
2. ✅ **Limit conversation history** - Already done
3. ✅ **Shorter system prompt** - Already done
4. ⏳ **Switch to generate API** - Recommended

### Short-term:
1. **Add response streaming** - Better UX
2. **Cache common responses** - "Guten Tag", "Danke", etc.
3. **Optimize objective checking** - Run in parallel

### Long-term:
1. **Fine-tune model** - Train on restaurant scenarios
2. **Use smaller specialized model** - Faster for specific tasks
3. **Implement response templates** - Mix AI + templates

---

## Performance Targets

| Metric | Current | Target | Optimized |
|--------|---------|--------|-----------|
| AI Generation | 12s | 2-3s | 2-4s |
| Objective Check | <100ms | <50ms | <50ms |
| State Update | <100ms | <50ms | <50ms |
| **Total Response** | **12s** | **3-4s** | **2-5s** |

---

## Testing Commands

### Test Direct Ollama:
```bash
curl -s http://localhost:11435/api/generate \
  -d '{"model":"llama3.2:1b","prompt":"Hallo!","options":{"num_predict":20}}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['response'])"
```

### Test Scenario Endpoint:
```bash
TOKEN="your_token_here"
time curl -s -X POST "http://localhost:8000/api/v1/scenarios/SCENARIO_ID/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hallo!"}'
```

---

## Implementation Priority

### High Priority (Do Now):
- [x] Reduce token generation limit
- [x] Shorten system prompt
- [x] Limit conversation history
- [ ] **Switch to generate API** ⭐

### Medium Priority (This Week):
- [ ] Add response streaming
- [ ] Implement basic caching
- [ ] Optimize objective checking

### Low Priority (Future):
- [ ] Fine-tune model
- [ ] Response templates
- [ ] Advanced caching

---

## Expected Results After Full Optimization

With all optimizations:
- **Generate API:** 2-3s (vs 12s currently)
- **Streaming:** Perceived <1s (first tokens appear immediately)
- **Caching:** <100ms for common phrases
- **Overall:** 2-4s average response time

---

## Notes

- Current bottleneck is chat API overhead
- Model itself is fast (~2s)
- System prompt and context add 10s overhead
- Generate API would solve most issues
- Streaming would improve UX significantly

---

**Status:** Optimizations applied, testing needed  
**Next Action:** Switch to generate API for 5-6x speedup  
**Updated:** 2025-01-04
