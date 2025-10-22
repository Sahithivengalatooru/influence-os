from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from uuid import uuid4

from app.auth.jwt import get_current_user, JWTPayload

router = APIRouter(prefix="/calendar", tags=["calendar"])

# In-memory calendar store for prototype
_CAL: Dict[str, Dict] = {}


class CalendarItem(BaseModel):
    id: str
    date: str           # ISO date (YYYY-MM-DD)
    title: str
    status: str = "draft"  # draft | scheduled | published


class CreateItem(BaseModel):
    date: str
    title: str


@router.get("/", response_model=List[CalendarItem])
def list_items(user: JWTPayload = Depends(get_current_user)):
    return [CalendarItem(**v) for v in _CAL.values()]


@router.post("/", response_model=CalendarItem)
def create_item(req: CreateItem, user: JWTPayload = Depends(get_current_user)):
    cid = str(uuid4())
    item = CalendarItem(id=cid, date=req.date, title=req.title)
    _CAL[cid] = item.model_dump()
    return item


@router.put("/{item_id}", response_model=CalendarItem)
def update_item(item_id: str, patch: CalendarItem, user: JWTPayload = Depends(get_current_user)):
    if item_id not in _CAL:
        raise HTTPException(status_code=404, detail="Not found")
    _CAL[item_id] = patch.model_dump()
    return CalendarItem(**_CAL[item_id])


@router.delete("/{item_id}")
def delete_item(item_id: str, user: JWTPayload = Depends(get_current_user)):
    _CAL.pop(item_id, None)
    return {"ok": True}
