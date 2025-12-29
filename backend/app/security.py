import time
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    try:
        # Truncate password to 72 characters for bcrypt compatibility
        if len(password) > 72:
            password = password[:72]
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Hash error: {e}")
        # Fallback to a simple approach if bcrypt fails
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    try:
        # Truncate password to 72 characters for bcrypt compatibility
        if len(password) > 72:
            password = password[:72]
        return pwd_context.verify(password, hashed)
    except Exception as e:
        print(f"Verify error: {e}")
        # Fallback to simple hash comparison if bcrypt fails
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest() == hashed


def create_jwt(sub: str, ttl_seconds: int = 7 * 24 * 3600, role: str = "user") -> str:
    payload = {"sub": sub, "exp": int(time.time()) + ttl_seconds, "role": role}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def auth_dep(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> str:
    token = credentials.credentials
    payload = decode_jwt(token)
    return payload["sub"]


async def optional_auth_dep(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))) -> str | None:
    """Optional authentication - returns user_id if authenticated, None otherwise"""
    if credentials is None:
        return None
    try:
        token = credentials.credentials
        payload = decode_jwt(token)
        return payload["sub"]
    except:
        return None


# Alias for clarity in subscription middleware
async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> str:
    """Get current user ID from JWT token"""
    return await auth_dep(credentials)
