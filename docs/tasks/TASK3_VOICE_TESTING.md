# Task 3: Voice Pipeline - Comprehensive Testing Guide

**Date:** November 2024  
**Status:** Testing Phase  
**Version:** 1.0

---

## 🎯 Testing Objectives

1. Verify Whisper STT transcription accuracy
2. Verify Piper TTS synthesis quality
3. Test full voice conversation pipeline
4. Validate error handling and edge cases
5. Measure performance metrics
6. Document all findings

---

## 📋 Pre-Test Checklist

### ✅ System Requirements
- [ ] All Docker containers running
- [ ] Backend accessible on port 8000
- [ ] Frontend accessible on port 3000
- [ ] Voice features enabled in .env
- [ ] User logged in with valid token

### ✅ Service Status Check
```bash
# Check all containers
docker ps --format "table {{.Names}}\t{{.Status}}"

# Expected output:
# german_backend    - Up
# german_frontend   - Up
# german_redis      - Up (healthy)
# german_whisper    - Up (healthy)
# german_piper      - Up
# german_ollama     - Up
```

### ✅ Voice API Status
```bash
curl -s http://localhost:8000/api/v1/voice/status | python3 -m json.tool
```

**Expected Response:**
```json
{
    "whisper_available": true,
    "piper_available": true,
    "voice_features_enabled": true,
    "whisper_model": "medium",
    "piper_voice": "de_DE-thorsten-high"
}
```

---

## 🧪 Test Suite 1: Whisper STT (Speech-to-Text)

### Test 1.1: Basic Transcription (German)

**Objective:** Verify Whisper can transcribe German audio

**Test Steps:**
1. Navigate to http://localhost:3000/voice-chat
2. Click microphone button
3. Speak: "Guten Tag, wie geht es Ihnen?"
4. Stop recording

**Expected Result:**
- Transcription appears in chat
- Text is accurate (>90% match)
- Response time < 2 seconds

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Notes: _______________

---

### Test 1.2: English Transcription

**Objective:** Verify Whisper handles English input

**Test Steps:**
1. Click microphone
2. Speak: "Hello, how are you today?"
3. Stop recording

**Expected Result:**
- Transcription appears
- Recognized as English
- Accurate transcription

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Notes: _______________

---

### Test 1.3: Long Audio (30+ seconds)

**Objective:** Test handling of longer audio clips

**Test Steps:**
1. Record 30-60 seconds of German speech
2. Stop and wait for processing

**Expected Result:**
- Full transcription
- No timeout errors
- Processing time < 5 seconds

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Processing time: _____ seconds
- Notes: _______________

---

### Test 1.4: Background Noise

**Objective:** Test robustness with background noise

**Test Steps:**
1. Play background music/noise
2. Speak German sentence
3. Stop recording

**Expected Result:**
- Transcription still works
- May have minor errors
- No crashes

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Accuracy: ____%
- Notes: _______________

---

### Test 1.5: Very Short Audio (<1 second)

**Objective:** Test edge case of very short audio

**Test Steps:**
1. Click and immediately stop recording
2. Or say single word quickly

**Expected Result:**
- Error message or empty transcription
- No crash
- Graceful handling

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Notes: _______________

---

## 🧪 Test Suite 2: Piper TTS (Text-to-Speech)

### Test 2.1: Basic Synthesis (German)

**Objective:** Verify Piper can synthesize German text

**Test Method:** Use API directly
```bash
TOKEN="your_jwt_token_here"

curl -X POST http://localhost:8000/api/v1/voice/synthesize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Guten Tag, wie geht es Ihnen?"
  }'
```

**Expected Result:**
- Returns base64 audio
- Audio is playable
- Voice sounds natural
- German pronunciation correct

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Audio quality (1-5): _____
- Notes: _______________

---

### Test 2.2: Long Text Synthesis

**Objective:** Test synthesis of longer text

**Test Text:**
```
"Die deutsche Sprache ist eine sehr interessante Sprache. 
Sie hat viele komplexe Grammatikregeln, aber sie ist auch 
sehr logisch und präzise. Viele Menschen auf der ganzen 
Welt lernen Deutsch als Fremdsprache."
```

**Expected Result:**
- Complete synthesis
- No cutoff
- Natural pauses
- Processing time < 3 seconds

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Processing time: _____ seconds
- Notes: _______________

---

### Test 2.3: Special Characters

**Objective:** Test handling of umlauts and special characters

**Test Text:** "Äpfel, Öl, Über, ß, München"

**Expected Result:**
- Correct pronunciation of umlauts
- ß pronounced correctly
- No errors

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Notes: _______________

---

### Test 2.4: Numbers and Dates

**Objective:** Test synthesis of numbers

**Test Text:** "Heute ist der 1. November 2024. Die Temperatur beträgt 15 Grad."

**Expected Result:**
- Numbers spoken correctly
- Dates pronounced naturally

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Notes: _______________

---

## 🧪 Test Suite 3: Full Voice Conversation Pipeline

### Test 3.1: Simple Conversation

**Objective:** Test complete STT → LLM → TTS flow

**Test Steps:**
1. Open http://localhost:3000/voice-chat
2. Record: "Hallo! Wie heißt du?"
3. Wait for AI response
4. Verify audio plays automatically

**Expected Result:**
- User speech transcribed
- AI generates German response
- AI response synthesized to audio
- Audio plays automatically
- Total latency < 5 seconds

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Total latency: _____ seconds
- Transcription: _______________
- AI Response: _______________
- Notes: _______________

---

### Test 3.2: Multi-Turn Conversation

**Objective:** Test conversation context retention

**Test Steps:**
1. Turn 1: "Ich heiße Max. Wie heißt du?"
2. Wait for response
3. Turn 2: "Wie ist das Wetter heute?"
4. Wait for response
5. Turn 3: "Was ist mein Name?" (test context)

**Expected Result:**
- AI remembers context
- Responses are contextually relevant
- AI recalls user's name in turn 3

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Context retained: [ ] Yes [ ] No
- Notes: _______________

---

### Test 3.3: Error Recovery

**Objective:** Test system recovery from errors

**Test Steps:**
1. Record silence (no speech)
2. Record very loud noise
3. Record mixed language
4. Interrupt recording multiple times

**Expected Result:**
- Graceful error messages
- No crashes
- System remains usable

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Errors encountered: _______________
- Recovery successful: [ ] Yes [ ] No
- Notes: _______________

---

### Test 3.4: Concurrent Users (Load Test)

**Objective:** Test system under load

**Test Method:**
```bash
# Simulate 5 concurrent voice requests
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/voice/conversation \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"audio_base64":"'$(base64 test_audio.wav)'","context":"general"}' &
done
wait
```

**Expected Result:**
- All requests complete
- No timeouts
- Response times remain acceptable

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Requests completed: ___/5
- Average response time: _____ seconds
- Notes: _______________

---

## 🧪 Test Suite 4: Performance Metrics

### Test 4.1: Latency Breakdown

**Objective:** Measure each component's latency

**Test Method:** Check backend logs for timing

**Metrics to Record:**

| Component | Target | Actual | Pass/Fail |
|-----------|--------|--------|-----------|
| STT (Whisper) | <1.5s | ___s | [ ] |
| LLM (Ollama) | <2s | ___s | [ ] |
| TTS (Piper) | <0.5s | ___s | [ ] |
| **Total Pipeline** | **<4s** | **___s** | **[ ]** |

**Notes:** _______________

---

### Test 4.2: Accuracy Metrics

**Objective:** Measure transcription accuracy

**Test Method:** 
1. Prepare 10 German sentences
2. Record each clearly
3. Compare transcription to original

**Accuracy Results:**

| Sentence | Original | Transcribed | Accuracy % |
|----------|----------|-------------|------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| ... | | | |

**Average Accuracy:** ____%

**Pass Criteria:** >85% average accuracy

**Result:** [ ] Pass [ ] Fail

---

### Test 4.3: Resource Usage

**Objective:** Monitor system resource usage

**Test Method:**
```bash
# Monitor during voice conversation
docker stats --no-stream
```

**Resource Metrics:**

| Container | CPU % | Memory | Pass/Fail |
|-----------|-------|--------|-----------|
| backend | ___% | ___MB | [ ] |
| whisper | ___% | ___MB | [ ] |
| piper | ___% | ___MB | [ ] |
| ollama | ___% | ___MB | [ ] |

**Notes:** _______________

---

## 🧪 Test Suite 5: Edge Cases & Error Handling

### Test 5.1: Network Interruption

**Objective:** Test behavior during network issues

**Test Steps:**
1. Start recording
2. Pause Docker network: `docker network disconnect german-ai_default german_whisper`
3. Stop recording
4. Reconnect: `docker network connect german-ai_default german_whisper`

**Expected Result:**
- Error message displayed
- System recovers after reconnection

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Notes: _______________

---

### Test 5.2: Service Unavailable

**Objective:** Test when voice services are down

**Test Steps:**
1. Stop Whisper: `docker stop german_whisper`
2. Try to record
3. Restart: `docker start german_whisper`

**Expected Result:**
- Clear error message
- "Whisper STT not available"
- No crash

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Error message: _______________

---

### Test 5.3: Invalid Audio Format

**Objective:** Test handling of invalid audio

**Test Method:** Send invalid base64 to API

**Expected Result:**
- 400 Bad Request
- Descriptive error message

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Status code: _____
- Error message: _______________

---

### Test 5.4: Token Expiration

**Objective:** Test auth token expiration

**Test Steps:**
1. Use expired token
2. Try voice conversation

**Expected Result:**
- 401 Unauthorized
- Redirect to login

**Actual Result:**
- [ ] Pass
- [ ] Fail
- Notes: _______________

---

## 🧪 Test Suite 6: Browser Compatibility

### Test 6.1: Chrome/Chromium

**Browser:** Chrome/Chromium
**Version:** _____

**Test Results:**
- [ ] Microphone access works
- [ ] Recording works
- [ ] Audio playback works
- [ ] UI displays correctly

**Notes:** _______________

---

### Test 6.2: Firefox

**Browser:** Firefox
**Version:** _____

**Test Results:**
- [ ] Microphone access works
- [ ] Recording works
- [ ] Audio playback works
- [ ] UI displays correctly

**Notes:** _______________

---

### Test 6.3: Safari

**Browser:** Safari
**Version:** _____

**Test Results:**
- [ ] Microphone access works
- [ ] Recording works
- [ ] Audio playback works
- [ ] UI displays correctly

**Notes:** _______________

---

## 📊 Test Summary

### Overall Results

**Total Tests:** 25+
**Passed:** _____
**Failed:** _____
**Pass Rate:** _____%

### Critical Issues Found

1. _______________
2. _______________
3. _______________

### Minor Issues Found

1. _______________
2. _______________
3. _______________

### Performance Summary

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| STT Latency | <1.5s | ___s | [ ] |
| TTS Latency | <0.5s | ___s | [ ] |
| Total Pipeline | <4s | ___s | [ ] |
| Transcription Accuracy | >85% | ___% | [ ] |

---

## 🔧 Issues & Resolutions

### Issue 1: [Title]
**Severity:** [ ] Critical [ ] High [ ] Medium [ ] Low
**Description:** _______________
**Steps to Reproduce:** _______________
**Resolution:** _______________
**Status:** [ ] Fixed [ ] In Progress [ ] Deferred

---

### Issue 2: [Title]
**Severity:** [ ] Critical [ ] High [ ] Medium [ ] Low
**Description:** _______________
**Steps to Reproduce:** _______________
**Resolution:** _______________
**Status:** [ ] Fixed [ ] In Progress [ ] Deferred

---

## ✅ Sign-Off

### Testing Completed By
**Name:** _____________________
**Date:** _____________________
**Signature:** _____________________

### Approved By
**Name:** _____________________
**Date:** _____________________
**Signature:** _____________________

---

## 📝 Additional Notes

_______________
_______________
_______________

---

**End of Testing Document**
