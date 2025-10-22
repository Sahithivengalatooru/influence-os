from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

from app.auth.jwt import get_current_user, JWTPayload

router = APIRouter(prefix="/moderation", tags=["moderation"])

BANNED = {"hate", "harassment", "spam", "scam", "plagiarism"}


class ModerationReq(BaseModel):
    text: str


class ModerationRes(BaseModel):
    safe: bool
    reasons: List[str] = []


@router.post("/check", response_model=ModerationRes)
def check(req: ModerationReq, user: JWTPayload = Depends(get_current_user)) -> ModerationRes:
    t = req.text.lower()
    hits = [w for w in BANNED if w in t]
    return ModerationRes(safe=len(hits) == 0, reasons=hits)
