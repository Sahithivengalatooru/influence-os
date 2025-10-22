from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from typing import Dict, List
import csv
import io

from app.auth.jwt import get_current_user, JWTPayload

router = APIRouter(prefix="/export", tags=["export"])


def _stub_analytics() -> Dict[str, List[float]]:
    return {
        "likes": [10, 18, 14, 22, 30, 26, 33],
        "comments": [2, 5, 3, 4, 6, 5, 7],
        "shares": [1, 2, 2, 3, 4, 3, 5],
        "ctr": [1.2, 1.5, 1.1, 1.8, 2.1, 2.0, 2.4],
        "reach": [300, 420, 380, 520, 600, 570, 680],
    }


@router.get("/analytics.csv")
def analytics_csv(user: JWTPayload = Depends(get_current_user)):
    data = _stub_analytics()
    days = max(len(v) for v in data.values())

    buf = io.StringIO()
    writer = csv.writer(buf)
    header = ["day"] + list(data.keys())
    writer.writerow(header)
    for i in range(days):
        row = [i + 1] + [data[k][i] if i < len(data[k]) else "" for k in data.keys()]
        writer.writerow(row)

    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=analytics.csv"},
    )


@router.get("/analytics.json")
def analytics_json(user: JWTPayload = Depends(get_current_user)):
    return {"ok": True, "series": _stub_analytics()}
