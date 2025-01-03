from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from ..db import get_db
from ..security import hash_password, verify_password, create_jwt
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
    return {"user_id": str(res.inserted_id), "message": "Registration successful"}

@router.post('/login', response_model=LoginResponse)
async def login(payload: LoginRequest, db=Depends(get_db)):
    users = db["users"]
    user = await users.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_jwt(str(user["_id"]))
    return {"token": token, "user_id": str(user["_id"]) }
