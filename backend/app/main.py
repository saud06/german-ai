from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from .config import settings
from .routers import auth, vocab, grammar, quiz, progress, speech, quiz_v2, paragraph
from .routers import users, ai_conversation, scenarios, analytics, reviews, achievements, grammar_rules, payments
from .routers import grammar_exercises, writing_practice, reading_practice, organizations, api_keys, webhooks, admin_dashboard, gdpr, referrals, marketing_analytics, gamification, friends, leaderboard, learning_paths, integrated_learning, websocket, journeys
from .startup import seed_collections
from .redis_client import redis_client
from .ollama_client import ollama_client
from .whisper_client import whisper_client
from .piper_client import piper_client
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("🚀 Starting German AI Backend...")
    
    # Initialize Redis
    await redis_client.connect()
    
    # Initialize Ollama
    await ollama_client.initialize()
    
    # Pre-warm Ollama model (prevents slow first response)
    if ollama_client.is_available:
        try:
            logger.info("🔥 Pre-warming Ollama model...")
            import asyncio
            # Add timeout to prevent hanging
            await asyncio.wait_for(
                ollama_client.chat([{"role": "user", "content": "Hallo"}]),
                timeout=60.0
            )
            logger.info("✅ Model pre-warmed and ready!")
        except asyncio.TimeoutError:
            logger.warning("⚠️  Model pre-warm timed out (will warm on first request)")
        except Exception as e:
            logger.warning(f"⚠️  Model pre-warm failed: {e}")
    
    # Initialize voice services
    if settings.ENABLE_VOICE_FEATURES:
        logger.info("🎤 Initializing voice services...")
        await whisper_client.initialize()
        await piper_client.initialize()
    
    # Seed database collections
    await seed_collections()
    
    logger.info("✅ Backend startup complete")
    
    yield
    
    # Shutdown tasks
    logger.info("🛑 Shutting down...")
    await redis_client.disconnect()

app = FastAPI(
    title="German AI Learner API", 
    version="1.0.0", 
    lifespan=lifespan,
    response_model_by_alias=False
)

# CORS
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3002",
    "http://127.0.0.1:3002",
    "https://german-ai.fly.dev",  # Production frontend
]
if getattr(settings, "FRONTEND_ORIGIN", None):
    cors_origins.append(settings.FRONTEND_ORIGIN)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

@app.get("/")
def root():
    return {"status": "ok", "service": "german-backend", "version": "1.0.0"}

# Routers
app.include_router(auth.router, prefix=API_PREFIX, tags=["auth"]) 
app.include_router(vocab.router, prefix=API_PREFIX, tags=["vocab"]) 
app.include_router(grammar.router, prefix=API_PREFIX, tags=["grammar"]) 
app.include_router(quiz.router, prefix=API_PREFIX, tags=["quiz"]) 
app.include_router(quiz_v2.router, prefix=API_PREFIX, tags=["quiz-v2"])
app.include_router(progress.router, prefix=API_PREFIX, tags=["progress"]) 
app.include_router(speech.router, prefix=API_PREFIX, tags=["speech"])
app.include_router(paragraph.router, prefix=API_PREFIX, tags=["paragraph"])
app.include_router(users.router, prefix=API_PREFIX, tags=["users"])
app.include_router(ai_conversation.router, prefix=API_PREFIX, tags=["ai"])
app.include_router(scenarios.router, tags=["scenarios"])
app.include_router(analytics.router, prefix=API_PREFIX, tags=["analytics"])
app.include_router(reviews.router, prefix=API_PREFIX, tags=["reviews"])
app.include_router(achievements.router, tags=["achievements"])
app.include_router(grammar_rules.router, prefix=API_PREFIX, tags=["grammar-rules"])
app.include_router(payments.router, prefix=API_PREFIX, tags=["payments"])
app.include_router(grammar_exercises.router, prefix=API_PREFIX, tags=["grammar-exercises"])
app.include_router(writing_practice.router, prefix=API_PREFIX, tags=["writing-practice"])
app.include_router(reading_practice.router, prefix=API_PREFIX, tags=["reading-practice"])
app.include_router(organizations.router, prefix=API_PREFIX, tags=["organizations"])
app.include_router(api_keys.router, prefix=API_PREFIX, tags=["api-keys"])
app.include_router(webhooks.router, prefix=API_PREFIX, tags=["webhooks"])
app.include_router(admin_dashboard.router, prefix=API_PREFIX, tags=["admin"])
app.include_router(gdpr.router, prefix=API_PREFIX, tags=["gdpr"])
app.include_router(referrals.router, prefix=API_PREFIX, tags=["referrals"])
app.include_router(marketing_analytics.router, prefix=API_PREFIX, tags=["marketing"])
app.include_router(gamification.router, prefix=API_PREFIX + "/gamification", tags=["gamification"])
app.include_router(friends.router, prefix=API_PREFIX + "/friends", tags=["friends"])
app.include_router(leaderboard.router, prefix=API_PREFIX, tags=["leaderboard"])
app.include_router(learning_paths.router, prefix=API_PREFIX, tags=["learning-paths"])
app.include_router(integrated_learning.router, tags=["integrated-learning"])
app.include_router(websocket.router, prefix=API_PREFIX, tags=["websocket"])
app.include_router(journeys.router, prefix=API_PREFIX, tags=["journeys"])

# Import and register notifications router
from .routers import notifications
app.include_router(notifications.router, prefix=API_PREFIX + "/notifications", tags=["notifications"])

if settings.DEV_MODE and getattr(settings, "ALLOW_DEV_ROUTES", False):
    from .routers import admin
    app.include_router(admin.router, prefix=API_PREFIX, tags=["admin"]) 
