import os
import sys
import asyncio
import pytest
from fastapi.testclient import TestClient

# Ensure default envs for tests
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DB_NAME", "german_test")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("DEV_MODE", "true")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.main import app  # noqa: E402
from app.security import create_jwt, auth_dep  # noqa: E402

# Windows-specific fix: use Selector event loop for sync TestClient compatibility
if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

def test_health_root():
    with TestClient(app) as client:
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"
        assert data.get("service") == "german-backend"

def test_quiz_public_endpoint():
    with TestClient(app) as client:
        r = client.get("/api/v1/quiz/start-public", params={"size": 3})
        # Endpoint should always respond, even if DB is empty (may return empty questions list)
        assert r.status_code == 200
        data = r.json()
        assert "quiz_id" in data
        assert "questions" in data


def test_grammar_public_endpoint_basic():
    # Without OPENAI_API_KEY and possibly without DB, this endpoint may return 503
    # If DB is available and rules match, it should return 200 with JSON
    if sys.platform.startswith("win"):
        # No-op on Windows (avoid intermittent event loop issues with async drivers under TestClient)
        return
    with TestClient(app) as client:
        r = client.post("/api/v1/grammar/check-public", json={"sentence": "Ich gehen zur Schule."})
        assert r.status_code in (200, 503)
        if r.status_code == 200:
            data = r.json()
            assert "corrected" in data
            assert "explanation" in data


def test_speech_suggestions_endpoint():
    # Public endpoint with graceful fallbacks to static content
    with TestClient(app) as client:
        r = client.get("/api/v1/speech/suggestions", params={"size": 5})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        # Each item should have text
        if data:
            assert "text" in data[0]


@pytest.mark.skipif(sys.platform.startswith("win"), reason="Skip on Windows due to event loop issues with async DB drivers")
def test_progress_weekly_endpoint_shape():
    # Weekly endpoint should return an object with a 7-length values array
    with TestClient(app) as client:
        # Override auth dependency for test
        app.dependency_overrides[auth_dep] = lambda: "demo-user"
        r = client.get("/api/v1/progress/demo-user/weekly")
        app.dependency_overrides.clear()
        assert r.status_code == 200
        body = r.json()
        vals = body.get("values")
        assert isinstance(vals, list)
        assert len(vals) == 7


@pytest.mark.skipif(sys.platform.startswith("win"), reason="Skip on Windows due to event loop issues with async DB drivers")
def test_progress_summary_endpoint_keys():
    # Summary endpoint should return core keys with expected types
    with TestClient(app) as client:
        app.dependency_overrides[auth_dep] = lambda: "demo-user"
        r = client.get("/api/v1/progress/demo-user")
        app.dependency_overrides.clear()
        assert r.status_code == 200
        body = r.json()
        for key in ("user_id", "streak", "words_learned", "quizzes_completed", "common_errors", "badges"):
            assert key in body
        assert isinstance(body["user_id"], str)
        assert isinstance(body["streak"], int)
        assert isinstance(body["words_learned"], int)
        assert isinstance(body["quizzes_completed"], int)
        assert isinstance(body.get("common_errors"), list)
        assert isinstance(body.get("badges"), list)
