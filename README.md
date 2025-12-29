# 🇩🇪 German AI Language Learning Platform

A comprehensive, self-hosted AI-powered German language learning platform with voice conversation capabilities.

## ✨ Features

- 🤖 **AI Conversation**: Real-time German conversation with Mistral 7B
- 🎤 **Voice Chat**: Speak German and get audio responses (Whisper + Piper)
- 📚 **Vocabulary**: Learn and practice German words
- 📖 **Grammar**: Interactive grammar lessons
- 🎯 **Quizzes**: Test your knowledge
- 📊 **Progress Tracking**: Monitor your learning journey
- 🔒 **Self-Hosted**: Complete privacy, zero API costs
- ⚡ **GPU Accelerated**: Fast responses with local GPU

## 🚀 Quick Start

### Development Mode (GPU - Recommended for Local)

Uses native backend with GPU Ollama for maximum performance.

```bash
# One-time setup
./setup-gpu.sh

# Start development environment
./dev-start.sh
```

**Performance:**
- AI Response: 1-3s (GPU accelerated)
- Voice Transcription: 0.5-1.5s
- Total: ~5-7s per conversation

### Production Mode (Docker)

Uses Docker for all services.

```bash
# Start production environment
./prod-start.sh
```

## 📋 Prerequisites

### For Development (GPU Mode)
- macOS with Apple Silicon (M1/M2/M3)
- Python 3.11+
- Ollama installed
- Docker and Docker Compose

### For Production (Docker Mode)
- Docker and Docker Compose
- MongoDB Atlas URI (or local MongoDB)

## 🔧 Configuration

### 1. Environment Variables

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB_NAME=german_ai

# Security
JWT_SECRET=your-secure-random-string-32-chars

# Ollama (auto-configured)
OLLAMA_MODEL=llama3.2:1b
OLLAMA_TEMPERATURE=0.7

# Voice Features
ENABLE_VOICE_FEATURES=true
WHISPER_MODEL=tiny
PIPER_VOICE=de_DE-thorsten-high
```

### 2. MongoDB Setup

Get a free MongoDB Atlas account:
1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a free cluster
3. Get your connection string
4. Add it to `.env` as `MONGODB_URI`

## 📊 Services

### Development Mode
```
Frontend:   http://localhost:3000
Backend:    http://localhost:8000
API Docs:   http://localhost:8000/docs
Voice Chat: http://localhost:3000/voice-chat

Backend:    Native (GPU)
Ollama:     Native GPU (port 11435)
Whisper:    Docker (port 9000)
Piper:      Docker (port 10200)
```

### Production Mode
```
Frontend:   http://localhost:3000
Backend:    http://localhost:8000
API Docs:   http://localhost:8000/docs
Voice Chat: http://localhost:3000/voice-chat

All services: Docker
Ollama:       Docker (port 11434)
```

## 🎯 Usage

### Demo Login
```
Email:    saud@gmail.com
Password: password
```

### Voice Chat
1. Go to http://localhost:3000/voice-chat
2. Click the microphone button
3. Speak in German
4. AI responds with audio

### AI Conversation
1. Go to http://localhost:3000/test-ai
2. Type or speak German
3. Get instant AI responses

## 🛠️ Management

### Development Mode

**Check Status:**
```bash
./test-system.sh
```

**View Logs:**
```bash
# Backend
tail -f /tmp/backend-dev.log

# Docker services
docker compose logs -f whisper
docker compose logs -f piper
```

**Stop Services:**
```bash
# Stop backend
ps aux | grep uvicorn | grep -v grep | awk '{print $2}' | xargs kill

# Stop Docker services
docker compose down
```

### Production Mode

**View Logs:**
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

**Stop Services:**
```bash
docker compose down
```

**Restart Services:**
```bash
docker compose restart backend
```

## 📁 Project Structure

```
german-ai/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── routers/     # API endpoints
│   │   ├── services/    # Business logic
│   │   ├── models/      # Data models
│   │   └── clients/     # External service clients
│   └── requirements.txt
├── frontend/            # Next.js frontend
│   ├── src/
│   │   ├── app/        # Pages
│   │   ├── components/ # React components
│   │   └── lib/        # Utilities
│   └── package.json
├── docs/               # Documentation
│   ├── planning/       # Master plans
│   ├── tasks/          # Task documentation
│   └── archive/        # Old docs
├── docker-compose.yml  # Docker configuration
├── dev-start.sh       # Development startup
├── prod-start.sh      # Production startup
├── setup-gpu.sh       # GPU setup
└── test-system.sh     # System tests
```

## 🧪 Testing

### System Test
```bash
./test-system.sh
```

### Voice Pipeline Test
```bash
# Start dev environment
./dev-start.sh

# Test voice chat
# Go to http://localhost:3000/voice-chat
# Speak: "Hallo, wie geht's?"
```

### API Test
```bash
# Health check
curl http://localhost:8000/

# Voice status
curl http://localhost:8000/api/v1/voice/status

# Backend info (dev mode only)
curl http://localhost:8000/api/v1/debug/backend-info
```

## 📈 Performance

<<<<<<< HEAD
### Development Mode (GPU)
- Transcription: 0.5-1.5s (Whisper tiny)
- AI Generation: 1-3s (GPU Ollama)
- Synthesis: 2-3s (Piper)
- **Total: ~5-7s**

### Production Mode (Docker)
- Transcription: 1-2s
- AI Generation: 5-10s (CPU)
- Synthesis: 2-3s
- **Total: ~8-15s**

## 🐛 Troubleshooting

### Backend not starting
```bash
# Check logs
tail -f /tmp/backend-dev.log

# Check if port is in use
lsof -i :8000

# Kill existing process
ps aux | grep uvicorn | grep -v grep | awk '{print $2}' | xargs kill
```

### GPU Ollama not working
```bash
# Check if running
lsof -i :11435

# Restart GPU Ollama
./setup-gpu.sh

# Check models
curl http://localhost:11435/api/tags
```

### Voice features not working
```bash
# Check services
docker compose ps

# Restart voice services
docker compose restart whisper piper

# Check voice status
curl http://localhost:8000/api/v1/voice/status
```

## 📚 Documentation

- **Planning**: `docs/planning/MASTER_PLAN_EXECUTIVE_SUMMARY.md`
- **Tasks**: `docs/tasks/TASK3_COMPLETION_SUMMARY.md`
- **Testing**: `docs/tasks/TASK3_VOICE_TESTING.md`

## 🏗️ Development Roadmap

- ✅ **Phase 1-2**: Foundation & AI (Complete)
- ✅ **Phase 3**: Voice Pipeline (Complete)
- 🔄 **Phase 4**: Life Simulation (Current)
- ⏳ **Phase 5**: Mobile Apps
- ⏳ **Phase 6**: Scale & Expansion

## 🤝 Contributing

This is a portfolio project. Contributions are welcome!

## 📄 License

MIT License

## 🙏 Acknowledgments

- **Ollama**: Local LLM runtime
- **Whisper**: Speech-to-text
- **Piper**: Text-to-speech
- **FastAPI**: Backend framework
- **Next.js**: Frontend framework

---

**Made with ❤️ for German language learners**
=======
https://german-ai.fly.dev
>>>>>>> 1b470bdba034e8d6a8e159ae8e2290296e6ca80e
