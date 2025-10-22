from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from uuid import uuid4

from app.auth.jwt import get_current_user, JWTPayload

router = APIRouter(prefix="/linkedin", tags=["linkedin"])

# In-memory scheduled posts for prototype
_SCHEDULED: Dict[str, Dict] = {}


class ScheduleReq(BaseModel):
    scheduled_at: str            # ISO timestamp
    text: str
    media_urls: Optional[List[str]] = None


class PublishReq(BaseModel):
    text: str
    media_urls: Optional[List[str]] = None


@router.post("/schedule")
def schedule_post(req: ScheduleReq, user: JWTPayload = Depends(get_current_user)):
    pid = str(uuid4())
    _SCHEDULED[pid] = {
        "id": pid,
        "user": user.sub,
        "scheduled_at": req.scheduled_at,
        "text": req.text,
        "media_urls": req.media_urls or [],
        "status": "scheduled",
    }
    return {"ok": True, "scheduled_id": pid}


@router.get("/scheduled")
def list_scheduled(user: JWTPayload = Depends(get_current_user)):
    items = [v for v in _SCHEDULED.values() if v["user"] == user.sub]
    return {"ok": True, "items": items}


@router.post("/publish")
def publish_now(req: PublishReq, user: JWTPayload = Depends(get_current_user)):
    # Prototype: pretend publish succeeded and return a fake post id
    post_id = f"li_{uuid4().hex[:8]}"
    return {"ok": True, "post_id": post_id, "status": "published"}


@router.get("/metrics")
def get_metrics(user: JWTPayload = Depends(get_current_user)):
    # Prototype stub metrics
    return {
        "ok": True,
        "user": user.sub,
        "metrics": {"likes": 42, "comments": 7, "shares": 3, "impressions": 1870, "ctr": 2.1},
    }
