"""
Rate Limiting Middleware
Redis-based rate limiting for API endpoints
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import hashlib
from typing import Optional


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    def __init__(self, app, redis_client):
        super().__init__(app)
        self.redis = redis_client
        
        # Default rate limits (requests per hour)
        self.default_limits = {
            "free": 100,
            "premium": 1000,
            "plus": 5000,
            "enterprise": 10000
        }
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for certain paths
        skip_paths = ["/docs", "/redoc", "/openapi.json", "/health", "/"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Get identifier (API key or user ID)
        identifier = await self._get_identifier(request)
        if not identifier:
            # No authentication, use IP-based rate limiting
            identifier = f"ip:{request.client.host}"
            rate_limit = 50  # Strict limit for unauthenticated requests
        else:
            # Get rate limit based on organization tier
            rate_limit = await self._get_rate_limit(identifier, request)
        
        # Check rate limit
        allowed = await self._check_rate_limit(identifier, rate_limit)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "X-RateLimit-Limit": str(rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int((datetime.utcnow() + timedelta(hours=1)).timestamp()))
                }
            )
        
        # Get remaining requests
        remaining = await self._get_remaining(identifier, rate_limit)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int((datetime.utcnow() + timedelta(hours=1)).timestamp()))
        
        return response
    
    async def _get_identifier(self, request: Request) -> Optional[str]:
        """Get identifier from request (API key or user ID)"""
        # Check for API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            # Hash API key for Redis key
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            return f"api_key:{key_hash}"
        
        # Check for JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            # In production, decode JWT to get user ID
            # For now, use token hash
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            return f"user:{token_hash}"
        
        return None
    
    async def _get_rate_limit(self, identifier: str, request: Request) -> int:
        """Get rate limit for identifier"""
        # If API key, get from database
        if identifier.startswith("api_key:"):
            # In production, query database for API key rate limit
            # For now, return default
            return 1000
        
        # If user, get organization tier
        if identifier.startswith("user:"):
            # In production, query database for user's organization tier
            # For now, return default
            return 100
        
        # IP-based
        return 50
    
    async def _check_rate_limit(self, identifier: str, limit: int) -> bool:
        """Check if identifier has exceeded rate limit"""
        if not self.redis or not self.redis.is_connected:
            # If Redis is not available, allow request (fail open)
            return True
        
        try:
            # Get current count
            key = f"rate_limit:{identifier}"
            current = await self.redis.get(key)
            
            if current is None:
                # First request in this window
                await self.redis.setex(key, 3600, 1)  # 1 hour TTL
                return True
            
            current = int(current)
            if current >= limit:
                return False
            
            # Increment counter
            await self.redis.incr(key)
            return True
        
        except Exception as e:
            # If Redis fails, allow request (fail open)
            print(f"Rate limit check failed: {e}")
            return True
    
    async def _get_remaining(self, identifier: str, limit: int) -> int:
        """Get remaining requests for identifier"""
        if not self.redis or not self.redis.is_connected:
            return limit
        
        try:
            key = f"rate_limit:{identifier}"
            current = await self.redis.get(key)
            
            if current is None:
                return limit
            
            current = int(current)
            remaining = max(0, limit - current)
            return remaining
        
        except Exception:
            return limit


# Decorator for endpoint-specific rate limiting
def rate_limit(requests_per_hour: int):
    """Decorator for endpoint-specific rate limiting"""
    def decorator(func):
        func._rate_limit = requests_per_hour
        return func
    return decorator
