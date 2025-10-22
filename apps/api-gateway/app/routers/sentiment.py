from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Literal

from app.auth.jwt import get_current_user, JWTPayload

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


class SentReq(BaseModel):
    text: str


class SentRes(BaseModel):
    label: Literal["positive", "neutral", "negative"]
    score: float


@router.post("/analyze", response_model=SentRes)
def analyze(req: SentReq, user: JWTPayload = Depends(get_current_user)) -> SentRes:
    t = req.text.lower()
    pos = sum(t.count(w) for w in ["great", "love", "nice", "win", "good", "awesome"])
    neg = sum(t.count(w) for w in ["bad", "hate", "fail", "terrible", "worse", "awful"])
    if pos > neg:
        return SentRes(label="positive", score=min(1.0, 0.6 + 0.1 * pos))
    if neg > pos:
        return SentRes(label="negative", score=min(1.0, 0.6 + 0.1 * neg))
    return SentRes(label="neutral", score=0.5)
