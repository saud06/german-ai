from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import datetime
from ..db import get_db
from ..security import hash_password, verify_password, create_jwt, get_current_user_id as get_current_user
from bson import ObjectId

router = APIRouter(prefix="/auth")

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    user_id: str
    message: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str
    user_id: str

@router.post('/register', response_model=RegisterResponse)
async def register(payload: RegisterRequest, db=Depends(get_db)):
    users = db["users"]
    existing = await users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {
        "name": payload.name,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "level": "A1",
    }
    res = await users.insert_one(doc)
    user_id = str(res.inserted_id)
    
    # Create free subscription for new user
    subscription_doc = {
        "user_id": user_id,
        "stripe_customer_id": None,  # Will be created when user upgrades
        "stripe_subscription_id": None,
        "tier": "free",
        "status": "active",
        "current_period_start": None,
        "current_period_end": None,
        "cancel_at_period_end": False,
        "trial_end": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db["subscriptions"].insert_one(subscription_doc)
    
    return {"user_id": user_id, "message": "Registration successful"}

@router.post('/login', response_model=LoginResponse)
async def login(payload: LoginRequest, db=Depends(get_db)):
    users = db["users"]
    user = await users.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # Include user role in JWT token
    user_role = user.get("role", "user")
    token = create_jwt(str(user["_id"]), role=user_role)
    return {"token": token, "user_id": str(user["_id"]) }
