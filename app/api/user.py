# app/api/user.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
async def read_users():
    return [{"username": "user1"}, {"username": "user2"}]