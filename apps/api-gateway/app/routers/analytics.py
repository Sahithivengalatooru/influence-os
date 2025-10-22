from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Dict, List, Optional

from app.auth.jwt import get_current_user, JWTPayload

router = APIRouter(prefix="/analytics", tags=["analytics"])


class Series(BaseModel):
    label: str
    values: List[float]


class AnalyticsSummary(BaseModel):
    ok: bool = True
    series: Dict[str, List[float]]


class KPIRequest(BaseModel):
    range_days: int = 7


@router.get("/summary", response_model=AnalyticsSummary)
def summary(user: JWTPayload = Depends(get_current_user)) -> AnalyticsSummary:
    # Prototype stub data
    return AnalyticsSummary(
        series={
            "likes": [10, 18, 14, 22, 30, 26, 33],
            "comments": [2, 5, 3, 4, 6, 5, 7],
            "shares": [1, 2, 2, 3, 4, 3, 5],
            "ctr": [1.2, 1.5, 1.1, 1.8, 2.1, 2.0, 2.4],
            "reach": [300, 420, 380, 520, 600, 570, 680],
        }
    )


@router.get("/kpi")
def kpi(
    metric: str = Query("ctr", pattern="^(likes|comments|shares|ctr|reach)$"),
    range_days: int = Query(7, ge=1, le=30),
    user: JWTPayload = Depends(get_current_user),
) -> Dict[str, List[float]]:
    # Tiny extractor from the summary series
    series = {
        "likes": [10, 18, 14, 22, 30, 26, 33],
        "comments": [2, 5, 3, 4, 6, 5, 7],
        "shares": [1, 2, 2, 3, 4, 3, 5],
        "ctr": [1.2, 1.5, 1.1, 1.8, 2.1, 2.0, 2.4],
        "reach": [300, 420, 380, 520, 600, 570, 680],
    }
    vals = series.get(metric, [])[-range_days:]
    return {"metric": metric, "values": vals}
