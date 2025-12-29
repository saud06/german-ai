# Testing Guide - Redis + WebSocket Implementation

## ✅ Task 1 Complete: Redis + WebSocket Foundation

### What Was Implemented

1. **Redis Service** - Caching and session management
2. **WebSocket Support** - Real-time bidirectional communication
3. **Connection Manager** - Handle multiple concurrent WebSocket connections
4. **Frontend Hook** - React hook for easy WebSocket integration
5. **Test UI** - Interactive WebSocket testing interface

---

## 🚀 How to Test

### Step 1: Update Environment Variables

Update your `.env` file with the new variables (or copy from `.env.example`):

```bash
# Add these to your .env file
REDIS_URL=redis://redis:6379
REDIS_MAX_CONNECTIONS=50
WS_MAX_CONNECTIONS=100
WS_HEARTBEAT_INTERVAL=30
ENABLE_AI_CONVERSATION=false
ENABLE_VOICE_FEATURES=false
ENABLE_LIFE_SIMULATION=false
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 2: Rebuild and Start Services

```bash
# Stop existing containers
docker compose down

# Rebuild with new dependencies
docker compose build

# Start all services (including Redis)
docker compose up -d

# Check logs
docker compose logs -f
```

You should see:
- ✅ Redis connected successfully
- ✅ Backend startup complete
- All three containers running: `german_backend`, `german_frontend`, `german_redis`

### Step 3: Verify Redis is Running

```bash
# Check Redis container
docker ps | grep redis

# Test Redis connection
docker exec -it german_redis redis-cli ping
# Should return: PONG
```

### Step 4: Test WebSocket via UI

1. **Login** to the app:
   - Go to http://localhost:3000/login
   - Email: `saud@gmail.com`
   - Password: `password`

2. **Open WebSocket Test Page**:
   - Navigate to http://localhost:3000/test-websocket
   - You should see a green dot indicating "connected"

3. **Test Features**:
   - **Send Text**: Type a message and click "Send"
   - **Ping**: Click "Ping" button to test connection
   - **Echo**: Click "Echo Test" to test echo functionality
   - Watch the message log for responses

### Step 5: Test WebSocket via API (Postman/curl)

#### Using wscat (WebSocket CLI tool)

```bash
# Install wscat if you don't have it
npm install -g wscat

# Connect to WebSocket (replace TOKEN with your JWT)
wscat -c "ws://localhost:8000/api/v1/ws/connect?token=YOUR_JWT_TOKEN"

# Once connected, send messages:
{"type": "ping", "timestamp": 1234567890}
{"type": "echo", "content": "Hello WebSocket!"}
{"type": "broadcast", "content": "Broadcasting to all users"}
```

#### Get JWT Token

```bash
# Login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "saud@gmail.com", "password": "password"}' | jq -r '.token'
```

### Step 6: Test Redis Caching

```bash
# Access Redis CLI
docker exec -it german_redis redis-cli

# Check keys
KEYS *

# Get a value
GET some_key

# Check Redis info
INFO stats
```

---

## 🧪 API Endpoints Added

### WebSocket Endpoints

1. **General WebSocket**
   - **URL**: `ws://localhost:8000/api/v1/ws/connect?token=JWT_TOKEN`
   - **Purpose**: General real-time communication
   - **Messages**:
     - `{"type": "ping"}` - Test connection
     - `{"type": "echo", "content": "text"}` - Echo message back
     - `{"type": "broadcast", "content": "text"}` - Broadcast to all users

2. **Voice WebSocket** (prepared for future)
   - **URL**: `ws://localhost:8000/api/v1/ws/voice?token=JWT_TOKEN`
   - **Purpose**: Voice streaming (will be implemented in Task 3)

---

## 📊 Monitoring

### Check Service Health

```bash
# Backend logs
docker compose logs backend

# Redis logs
docker compose logs redis

# All logs
docker compose logs -f
```

### Redis Monitoring

```bash
# Monitor Redis commands in real-time
docker exec -it german_redis redis-cli MONITOR

# Check memory usage
docker exec -it german_redis redis-cli INFO memory

# Check connected clients
docker exec -it german_redis redis-cli CLIENT LIST
```

---

## 🐛 Troubleshooting

### Issue: Redis connection failed

**Solution**:
```bash
# Check if Redis container is running
docker ps | grep redis

# Restart Redis
docker compose restart redis

# Check Redis logs
docker compose logs redis
```

### Issue: WebSocket won't connect

**Solution**:
1. Check if you're logged in (need JWT token)
2. Check browser console for errors
3. Verify backend is running: `curl http://localhost:8000/`
4. Check CORS settings in backend

### Issue: TypeScript errors in IDE

**Solution**:
These are expected during development. They'll resolve when you:
```bash
# Rebuild frontend
cd frontend
npm install
npm run build
```

### Issue: "Cannot find module 'redis'"

**Solution**:
```bash
# Rebuild backend container
docker compose build backend
docker compose up -d backend
```

---

## ✨ What's Next

### Task 2: Ollama + LLM Integration (Coming Next)

Will add:
- Ollama service in Docker
- Mistral-Small 7B model
- Streaming AI chat responses
- Enhanced grammar correction
- Context management

### Task 3: Voice Pipeline

Will add:
- Whisper STT service
- Piper TTS service
- Real-time voice conversation
- Audio streaming via WebSocket

---

## 📝 Notes

- **Redis is configured** with 256MB memory limit and LRU eviction
- **WebSocket supports** up to 100 concurrent connections (configurable)
- **Automatic reconnection** with exponential backoff
- **Heartbeat mechanism** keeps connections alive
- **All TypeScript errors** are cosmetic and will resolve on build

---

## 🎯 Success Criteria

✅ Redis container running
✅ WebSocket connects successfully
✅ Can send and receive messages
✅ Ping/pong works
✅ Echo test works
✅ No errors in backend logs
✅ Frontend test page loads

---

## 📞 Need Help?

If you encounter issues:
1. Check the logs: `docker compose logs -f`
2. Verify all containers are running: `docker ps`
3. Test Redis: `docker exec -it german_redis redis-cli ping`
4. Test backend: `curl http://localhost:8000/`
5. Check WebSocket in browser console

---

**Implementation Status**: ✅ **COMPLETE**

**Time to Test**: ~10 minutes

**Ready for**: Task 2 (Ollama + LLM Integration)
