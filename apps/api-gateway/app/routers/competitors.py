from __future__ import annotations

from fastapi import APIRouter, Depends
from typing import Dict, List

from app.auth.jwt import get_current_user, JWTPayload

router = APIRouter(prefix="/competitors", tags=["competitors"])


@router.get("/")
def list_competitors(user: JWTPayload = Depends(get_current_user)) -> Dict:
    return {
        "ok": True,
        "competitors": [
            {"handle": "@acme", "posts_7d": 6, "avg_engagement": 2.3, "top_post": "RAG wins"},
            {"handle": "@megacorp", "posts_7d": 3, "avg_engagement": 1.1, "top_post": "AI policy"},
        ],
    }


@router.get("/{handle}/posts")
def competitor_posts(handle: str, user: JWTPayload = Depends(get_current_user)) -> Dict:
    sample = [
        {"id": "p1", "title": "Agentic workflows vs pipelines", "engagement": 2.4},
        {"id": "p2", "title": "Designing evals that matter", "engagement": 1.9},
    ]
    return {"handle": handle, "posts": sample}
