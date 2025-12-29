"""
Redis client for caching and session management
"""
import redis.asyncio as redis
from typing import Optional, Any
import json
import logging
from .config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    """Async Redis client wrapper"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.pool: Optional[redis.ConnectionPool] = None
    
    async def connect(self):
        """Initialize Redis connection pool"""
        try:
            self.pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True
            )
            self.client = redis.Redis(connection_pool=self.pool)
            # Test connection
            await self.client.ping()
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.client = None
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("Redis disconnected")
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        if not self.client:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: str, 
        expire: Optional[int] = None
    ) -> bool:
        """Set value in Redis with optional expiration (seconds)"""
        if not self.client:
            return False
        try:
            if expire:
                await self.client.setex(key, expire, value)
            else:
                await self.client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.client:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            return False
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from Redis"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON for key: {key}")
        return None
    
    async def set_json(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """Set JSON value in Redis"""
        try:
            json_str = json.dumps(value)
            return await self.set(key, json_str, expire)
        except (TypeError, json.JSONEncodeError) as e:
            logger.error(f"Failed to encode JSON: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter"""
        if not self.client:
            return None
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR error: {e}")
            return None
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on existing key"""
        if not self.client:
            return False
        try:
            return await self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE error: {e}")
            return False
    
    async def ping(self) -> bool:
        """Ping Redis to check connection"""
        if not self.client:
            return False
        try:
            await self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis PING error: {e}")
            return False

# Global Redis client instance
redis_client = RedisClient()

async def get_redis() -> RedisClient:
    """Dependency for FastAPI routes"""
    return redis_client
