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
- Docker and Docker Compose
- MongoDB Atlas account (free tier works)
- 8GB RAM minimum
- (Optional) GPU for faster AI responses

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/saud06/german-ai.git
cd german-ai
```

2. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB_NAME=german_ai

# Security
JWT_SECRET=your-secure-random-string-min-32-chars

# AI Models
OLLAMA_MODEL=mistral:7b
ENABLE_AI_QUIZ_TOPUP=true

# Voice Features
ENABLE_VOICE_FEATURES=true
WHISPER_MODEL=tiny
PIPER_VOICE=de_DE-thorsten-high

# Optional: OpenAI (for enhanced features)
OPENAI_API_KEY=sk-...
```

3. **Start the application**
```bash
./START_PROJECT.sh
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Demo Account
```
Email:    saud@gmail.com
Password: password
```

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

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Next.js web application |
| Backend | 8000 | FastAPI REST API |
| MongoDB | 27017 | Database (external) |
| Redis | 6379 | Cache & sessions |
| Ollama | 11434 | Local LLM inference |
| Whisper | 9000 | Speech recognition |
| Piper | 10200 | Text-to-speech |

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
