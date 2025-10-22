from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

from app.auth.jwt import get_current_user, JWTPayload

router = APIRouter(prefix="/growth", tags=["growth"])


class GrowthChecklist(BaseModel):
    quick_wins: List[str]
    playbooks: List[str]
    profile_tips: List[str]


@router.get("/checklist", response_model=GrowthChecklist)
def checklist(user: JWTPayload = Depends(get_current_user)) -> GrowthChecklist:
    return GrowthChecklist(
        quick_wins=[
            "Comment on 3 high-signal posts/day",
            "Post 3x/week (mix text, carousel, poll)",
            "End with a clear CTA (save/DM)"
        ],
        playbooks=[
            "Case-study carousel: problem → approach → results",
            "Weekly poll to drive comments and reach",
            "AMA thread to convert lurkers to followers"
        ],
        profile_tips=[
            "Use a crisp headline with role + outcome",
            "Pin a post that shows measurable impact",
            "Add contact/CTA in the About section"
        ],
    )
