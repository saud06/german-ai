# Quick Start Guide - German AI Voice Chat

## 🚀 Start the Application

```bash
cd /Users/saud06/CascadeProjects/german-ai
./start.sh
```

OR manually:
```bash
docker compose up -d
sleep 15
docker compose restart backend  # Ensure all services connected
```

---

## 🎤 Use Voice Chat

1. **Open:** http://localhost:3000/voice-chat
2. **Login:**
   - Email: `saud@gmail.com`
   - Password: `password`
3. **Click** the microphone button 🎤
4. **Speak** in German (or English)
5. **Click** stop when done
6. **Wait** for AI response (~3-5 seconds)
7. **Listen** to the synthesized audio

---

## ✅ Check System Status

```bash
# All services
docker compose ps

# Voice pipeline
curl http://localhost:8000/api/v1/voice/status | jq

# Ollama models
docker compose exec ollama ollama list
```

**Expected Output:**
```json
{
  "whisper_available": true,
  "piper_available": true,
  "voice_features_enabled": true
}
```

---

## 🔧 Common Commands

```bash
# View logs
docker compose logs -f

# Restart backend
docker compose restart backend

# Stop everything
docker compose down

# Rebuild (if code changed)
docker compose build backend frontend
docker compose up -d
```

---

## 🐛 Quick Fixes

### Voice not working?
```bash
docker compose restart backend
```

### Services not starting?
```bash
docker compose down
docker compose up -d
sleep 15
docker compose restart backend
```

### Check what's wrong:
```bash
docker compose logs backend --tail 50
docker compose logs whisper --tail 20
```

---

## 📚 Full Documentation

- **SYSTEM_READY.md** - Complete system status
- **TASK3_VOICE_TESTING.md** - Comprehensive testing guide
- **FRESH_START_SUMMARY.md** - Rebuild documentation

---

## 🎯 That's It!

**The system is ready. Just open the voice chat and start speaking!**

http://localhost:3000/voice-chat
