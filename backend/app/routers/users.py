from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from ..db import get_db
from ..security import auth_dep, hash_password, verify_password
from bson import ObjectId
from pymongo import ReturnDocument

router = APIRouter(prefix="/users")


class MeResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: EmailStr


@router.get("/me", response_model=MeResponse)
async def get_me(user_id: str = Depends(auth_dep), db=Depends(get_db)):
    users = db["users"]
    user = await users.find_one({"_id": ObjectId(user_id)}, {"name": 1, "email": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])  # serialize
    return user


class UpdateMeRequest(BaseModel):
    name: str
    email: EmailStr


@router.put("/me", response_model=MeResponse)
async def update_me(payload: UpdateMeRequest, user_id: str = Depends(auth_dep), db=Depends(get_db)):
    users = db["users"]
    # Ensure email is unique (except for the same user)
    existing = await users.find_one({"email": payload.email, "_id": {"$ne": ObjectId(user_id)}})
    if existing:
        raise HTTPException(status_code=400, detail="Email already in use")
    res = await users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {"name": payload.name, "email": payload.email}},
        return_document=ReturnDocument.AFTER,
        projection={"name": 1, "email": 1},
    )
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    res["_id"] = str(res["_id"])  # serialize
    return res


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.put("/me/password")
async def change_password(payload: ChangePasswordRequest, user_id: str = Depends(auth_dep), db=Depends(get_db)):
    users = db["users"]
    user = await users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(payload.current_password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    await users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password_hash": hash_password(payload.new_password)}}
    )
    return {"message": "Password updated"}
