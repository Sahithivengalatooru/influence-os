from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

from app.auth.jwt import get_current_user, JWTPayload

router = APIRouter(prefix="/hashtags", tags=["hashtags"])


class SuggestReq(BaseModel):
    topic: str


class SuggestRes(BaseModel):
    hashtags: List[str]


@router.post("/suggest", response_model=SuggestRes)
def suggest(req: SuggestReq, user: JWTPayload = Depends(get_current_user)) -> SuggestRes:
    base = req.topic.lower().replace("#", "").split()
    uniq: list[str] = []
    for tok in base:
        tag = "#" + "".join(ch for ch in tok if ch.isalnum())
        if len(tag) > 1 and tag not in uniq:
            uniq.append(tag)
    for extra in ["#growth", "#community", "#buildinpublic"]:
        if extra not in uniq:
            uniq.append(extra)
    return SuggestRes(hashtags=uniq[:10])
