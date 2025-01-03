from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import auth, vocab, grammar, quiz, progress, speech
from .routers import users
from .startup import seed_collections
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    await seed_collections()
    yield
    # Shutdown tasks (none)

app = FastAPI(title="German AI Learner API", version="1.0.0", lifespan=lifespan)

# CORS
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3002",
    "http://127.0.0.1:3002",
]
if getattr(settings, "FRONTEND_ORIGIN", None):
    cors_origins.append(settings.FRONTEND_ORIGIN)  # e.g., https://your-frontend.onrender.com

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    # Allow any localhost/127.0.0.1 port in development to avoid CORS issues when dev servers run on different ports
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
app.include_router(progress.router, prefix=API_PREFIX, tags=["progress"]) 
app.include_router(speech.router, prefix=API_PREFIX, tags=["speech"]) 
app.include_router(users.router, prefix=API_PREFIX, tags=["users"])
if settings.DEV_MODE and getattr(settings, "ALLOW_DEV_ROUTES", False):
    # Lazy import to avoid importing dev code in production images
    from .routers import admin  # type: ignore
    app.include_router(admin.router, prefix=API_PREFIX, tags=["admin"]) 
