from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None

async def get_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is None:
        # Use short timeouts so that initial connection attempts fail fast during startup
        # This prevents the app from hanging on startup if the DB is unreachable.
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=3000,
        )
        # Choose DB name in the following order:
        # 1) Explicit MONGODB_DB_NAME from env
        # 2) Fallback to 'german_ai'
        #
        # Note: Avoid calling _client.get_default_database() because it raises
        # ConfigurationError when the URI does not include a database name.
        db_name = settings.MONGODB_DB_NAME or "german_ai"
        _db = _client[db_name]
    return _db
