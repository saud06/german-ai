# 🇩🇪 German AI Language Learning Platform

A comprehensive, AI-powered German language learning platform featuring interactive lessons, real-time speech practice, gamification, and immersive life simulation scenarios.

## ✨ Key Features

### 🎓 **Learning System**
- **Integrated Learning Path**: Structured curriculum with chapters, locations, and activities
- **Vocabulary Builder**: 1000+ German words with spaced repetition (SM-2 algorithm)
- **Grammar Lessons**: Interactive grammar exercises with AI-powered feedback
- **Quiz System**: Dynamic quizzes with AI-generated questions (Mistral 7B)
- **Progress Tracking**: Detailed analytics and learning statistics

### 🎤 **Speech & Voice**
- **Speech Practice**: Real-time pronunciation feedback with word-by-word color-coded analysis
- **Voice Conversations**: Natural German conversations with AI (Whisper + Ollama + Piper)
- **Paragraph Mode**: Practice reading full paragraphs with sentence-by-sentence navigation
- **Live Transcription**: Browser-based speech recognition with accuracy scoring

### 🎮 **Life Simulation**
- **10 Real-Life Scenarios**: Restaurant, Hotel, Supermarket, Doctor, Train Station, Bank, Pharmacy, Post Office, Apartment Viewing, Job Interview
- **AI-Powered NPCs**: Dynamic character interactions with personalities
- **Objective System**: Keyword-based completion tracking with hints
- **Streaming Responses**: Real-time AI conversation via Server-Sent Events

### 🏆 **Gamification**
- **Achievement System**: Unlock badges and milestones
- **Leaderboard**: Compete with other learners
- **Friends System**: Connect and learn together
- **XP & Levels**: Track your progress and level up
- **Daily Streaks**: Maintain learning consistency

### 💳 **Monetization**
- **Subscription Plans**: Free, Basic, Premium, and Lifetime tiers
- **Payment Integration**: Stripe-powered checkout
- **Referral Program**: Earn rewards for inviting friends
- **Admin Dashboard**: User management and analytics

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop**: Latest version ([Install Docker](https://docs.docker.com/get-docker/))
- **Git**: For cloning the repository
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 15GB free space for AI models
- **GPU** (Optional but Recommended): NVIDIA/AMD for 10-15x faster AI performance

### One-Command Setup ⚡

**Clone and run the automated setup script:**

```bash
git clone https://github.com/saud06/german-ai.git
cd german-ai
chmod +x setup.sh
./setup.sh
```

**That's it!** The script will automatically:
- ✅ Detect your operating system (Linux/macOS/Windows WSL)
- ✅ Detect your GPU (NVIDIA/AMD/CPU)
- ✅ Install Ollama **natively** on your machine for GPU acceleration
- ✅ Download 3 AI models (mistral:7b, llama3.2:3b, gemma2:9b) - ~11GB total
- ✅ Configure environment variables automatically
- ✅ Start Docker containers (Backend, Frontend, Whisper, Piper, Redis)
- ✅ Verify everything is working

### What Gets Installed

**Native (GPU-Accelerated):**
- 🧠 **Ollama** - Runs on your GPU for fast AI responses
  - mistral:7b (4.4 GB) - Main conversation model
  - llama3.2:3b (2.0 GB) - Fast responses
  - gemma2:9b (5.4 GB) - Grammar checking

**Docker Containers:**
- 🐳 **Backend** (FastAPI) - Port 8000
- 🌐 **Frontend** (Next.js) - Port 3000
- 🎤 **Whisper** (Speech Recognition) - Port 9000
- 🔊 **Piper** (Text-to-Speech) - Port 10200
- 💾 **Redis** (Cache) - Port 6379

### Access the Application

After setup completes (5-10 minutes for model downloads):

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### First Time Setup

1. Open http://localhost:3000
2. Create your account
3. Start learning German!

### Demo Account (Optional)
```
Email:    saud@gmail.com
Password: password
```

### Platform-Specific Notes

**macOS Users:**
- The script will prompt you to install Ollama from https://ollama.com/download
- After installation, run `./setup.sh` again

**Windows Users:**
- Use WSL2 (Windows Subsystem for Linux) for best compatibility
- Or use PowerShell: `.\setup-windows.ps1` (if available)

**Linux Users:**
- Script works on Ubuntu, Debian, Fedora, Arch, and most distributions
- GPU drivers (NVIDIA/AMD) should be installed beforehand for GPU acceleration

> **📖 For detailed setup instructions, troubleshooting, and manual configuration, see [SETUP.md](./SETUP.md)**

## 📊 Architecture

### Tech Stack

**Backend:**
- FastAPI (Python)
- MongoDB (Database)
- Redis (Caching)
- Ollama (Local LLM - Mistral 7B)
- Whisper (Speech-to-Text)
- Piper (Text-to-Speech)

**Frontend:**
- Next.js 14 (React)
- TypeScript
- Tailwind CSS
- Zustand (State Management)
- Lucide Icons

**Infrastructure:**
- Docker & Docker Compose
- Nginx (Production)
- Fly.io (Deployment)

### Services

| Service | Port | Description | Location |
|---------|------|-------------|----------|
| Frontend | 3000 | Next.js web application | Docker |
| Backend | 8000 | FastAPI REST API | Docker |
| MongoDB | 27017 | Database | MongoDB Atlas |
| Redis | 6379 | Cache & sessions | Docker |
| **Ollama (GPU)** | **11435** | **Local LLM inference (Mistral 7B)** | **Native (Host)** |
| Whisper | 9000 | Speech recognition | Docker |
| Piper | 10200 | Text-to-speech (Thorsten voice) | Docker |

### 🎯 AI Routing Strategy (PERMANENT)

**Heavy AI Features → Local GPU Ollama (Port 11435)**
- ✅ Grammar checking (Mistral 7B)
- ✅ Quiz generation (Mistral 7B)
- ✅ Scenario conversations (Mistral 7B)
- ✅ Voice chat responses (Llama 3.2 1B for speed)

**Light Services → Docker**
- ✅ Speech-to-text (Whisper tiny model)
- ✅ Text-to-speech (Piper with Thorsten voice)
- ✅ Caching (Redis)
- ✅ Frontend & Backend containers

**Why This Setup?**
- **Performance**: GPU Ollama provides 10-15x faster AI responses (1-2s vs 10-15s)
- **Quality**: Mistral 7B produces natural, grammatically correct German
- **Cost**: $0 per request vs OpenAI API costs
- **Privacy**: All AI processing happens locally

## 🎯 Core Features

### 1. Learning Path
Navigate through structured German lessons:
- **Chapters**: Organized learning modules
- **Locations**: Themed learning environments (Café, Park, Library, etc.)
- **Activities**: Interactive exercises (vocabulary, grammar, scenarios)
- **Progress Tracking**: Visual progress indicators and completion stats

### 2. Speech Practice
Advanced pronunciation training:
- Real-time word-by-word feedback
- Color-coded accuracy (Green/Yellow/Red)
- Similarity scoring algorithm
- Paragraph reading mode
- AI coach feedback with suggestions

### 3. Vocabulary System
Comprehensive word learning:
- 1000+ German words across multiple categories
- Spaced Repetition (SM-2 algorithm)
- Audio pronunciations
- Example sentences
- Progress tracking per word set

### 4. Grammar Exercises
Interactive grammar learning:
- AI-powered error detection (Mistral 7B)
- Detailed explanations
- Alternative phrasings
- Learning tips
- Fallback to rule-based checking

### 5. Quiz System
Dynamic assessment:
- Database of 84+ pre-made questions
- AI-generated questions (Mistral 7B)
- Multiple difficulty levels (A1-C2)
- Topic-based quizzes
- Instant feedback

### 6. Life Simulation Scenarios
Immersive real-world practice:
- 10 unique scenarios with multiple characters
- AI-driven conversations
- Objective-based progression
- Hint system
- Completion tracking

## 🛠️ Development

### Project Structure
```
german-ai/
├── backend/
│   ├── app/
│   │   ├── routers/          # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── models/           # Data models
│   │   ├── middleware/       # Auth, rate limiting
│   │   └── main.py           # FastAPI app
│   ├── scripts/              # Database seeding
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   ├── lib/              # Utilities
│   │   └── store/            # State management
│   └── package.json
├── k8s/                      # Kubernetes configs
├── docker-compose.yml        # Development setup
├── docker-compose.production.yml
├── START_PROJECT.sh          # Start script
└── STOP_PROJECT.sh           # Stop script
```

### Local Development

**Start services:**
```bash
./START_PROJECT.sh
```

**View logs:**
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

**Stop services:**
```bash
./STOP_PROJECT.sh
```

**Rebuild after code changes:**
```bash
docker compose build backend
docker compose restart backend
```

### Database Seeding

Seed the database with initial data:
```bash
# Seed learning path
docker compose exec backend python scripts/seed_complete_learning_path.py

# Seed vocabulary
docker compose exec backend python scripts/import_seed_words.py

# Seed achievements
docker compose exec backend python scripts/seed_achievements.py

# Create admin user
docker compose exec backend python scripts/set_admin.py
```

## 📈 Performance

### AI Response Times
- **Mistral 7B (GPU)**: 1-3 seconds
- **Mistral 7B (CPU)**: 5-10 seconds
- **Whisper (tiny model)**: 0.5-1.5 seconds
- **Piper TTS**: 2-3 seconds

### Optimization Features
- Model keep-alive (30 minutes)
- Redis caching
- Lazy service initialization
- Efficient database indexing
- Spaced repetition algorithm

## 🔒 Security

- JWT-based authentication
- Password hashing (bcrypt)
- Rate limiting
- CORS configuration
- Environment variable protection
- Secure session management

## 🌐 Deployment

### Production Deployment

The application is configured for deployment on Fly.io:

```bash
# Deploy backend
fly deploy -c fly.toml

# Deploy frontend
cd frontend && fly deploy
```

### Environment Variables (Production)

Ensure these are set in your production environment:
- `MONGODB_URI`
- `JWT_SECRET`
- `REDIS_URL`
- `FRONTEND_ORIGIN`
- `OPENAI_API_KEY` (optional)

## 🧪 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

**Authentication:**
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token

**Learning:**
- `GET /api/v1/learning-paths` - Get learning paths
- `GET /api/v1/vocab` - Get vocabulary
- `POST /api/v1/grammar/check` - Check grammar
- `GET /api/v1/quiz/start-public` - Start quiz

**Speech:**
- `POST /api/v1/speech/check` - Check pronunciation
- `GET /api/v1/paragraph/generate` - Generate practice paragraph

**Scenarios:**
- `GET /api/v1/scenarios` - List scenarios
- `POST /api/v1/scenarios/{id}/start` - Start scenario
- `POST /api/v1/scenarios/{id}/message` - Send message

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Ollama** - Local LLM runtime
- **Mistral AI** - Open-source language model
- **OpenAI Whisper** - Speech recognition
- **Piper TTS** - Text-to-speech synthesis
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework
- **MongoDB** - Database
- **Stripe** - Payment processing

## 📞 Support

For issues and questions:
- GitHub Issues: [github.com/saud06/german-ai/issues](https://github.com/saud06/german-ai/issues)
- Email: saud06@example.com

---

**Made with ❤️ for German language learners**

**Live Demo**: https://german-ai.fly.dev
