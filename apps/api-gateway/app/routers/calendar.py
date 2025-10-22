from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from typing import List, Literal, Optional
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix="/calendar", tags=["calendar"])

Status = Literal["draft", "scheduled", "published"]

class Item(BaseModel):
    id: str
    date: str  # ISO YYYY-MM-DD
    title: str
    status: Status = "draft"

class CreateItemReq(BaseModel):
    date: str
    title: str

_DB: List[Item] = []

def _to_iso_date(s: str) -> str:
    """Accept a few common formats and return YYYY-MM-DD."""
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # last resort: if it's already 10 chars and looks plausible, keep it
    if len(s) == 10 and s[4] in "-/" and s[7] in "-/":
        try:
            return datetime.fromisoformat(s.replace("/", "-")).strftime("%Y-%m-%d")
        except Exception:
            pass
    raise HTTPException(422, f"Invalid date format: {s}. Use YYYY-MM-DD or dd/MM/YYYY.")

@router.get("", response_model=List[Item])
def list_items():
    return _DB

@router.post("", response_model=Item)
def create_item(
    # allow either query params...
    date: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    # ...or JSON body
    payload: Optional[CreateItemReq] = Body(None),
):
    if payload:
        date = date or payload.date
        title = title or payload.title

    if not date or not title:
        raise HTTPException(422, "Both 'date' and 'title' are required (query or JSON).")

    it = Item(
        id=uuid4().hex,
        date=_to_iso_date(date),
        title=title.strip(),
        status="draft",
    )
    _DB.append(it)
    return it

@router.put("/{item_id}", response_model=Item)
def update_item(item_id: str, item: Item):
    for i, it in enumerate(_DB):
        if it.id == item_id:
            # normalize date on update too
            item.date = _to_iso_date(item.date)
            _DB[i] = item
            return item
    raise HTTPException(404, "Not found")

@router.delete("/{item_id}")
def delete_item(item_id: str):
    global _DB
    before = len(_DB)
    _DB = [it for it in _DB if it.id != item_id]
    return {"ok": len(_DB) < before}
