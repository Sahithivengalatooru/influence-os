from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.hash import bcrypt

from app.auth.jwt import create_jwt, get_current_user, JWTPayload
from app.config import get_settings, Settings

router = APIRouter(prefix="/users", tags=["users"])

# In-memory user store for prototype
_USERS: dict[str, str] = {}  # email -> bcrypt hash


class SignupReq(BaseModel):
    email: EmailStr
    password: str


class LoginReq(BaseModel):
    email: EmailStr
    password: str


class TokenRes(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/signup", response_model=TokenRes)
def signup(req: SignupReq, settings: Settings = Depends(get_settings)):
    if req.email in _USERS:
        raise HTTPException(status_code=400, detail="User already exists")
    _USERS[req.email] = bcrypt.hash(req.password)
    token = create_jwt(sub=req.email, role="user", ttl_minutes=120, settings=settings)
    return TokenRes(access_token=token)


@router.post("/login", response_model=TokenRes)
def login(req: LoginReq, settings: Settings = Depends(get_settings)):
    hashed = _USERS.get(req.email)
    if not hashed or not bcrypt.verify(req.password, hashed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_jwt(sub=req.email, role="user", ttl_minutes=120, settings=settings)
    return TokenRes(access_token=token)


@router.get("/me")
def me(user: JWTPayload = Depends(get_current_user)):
    return {"email": user.sub, "role": user.role}
