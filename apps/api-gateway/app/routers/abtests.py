from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Literal, Optional
from uuid import uuid4
import hashlib
import time

router = APIRouter(prefix="/abtests", tags=["abtests"])

Status = Literal["created", "running", "stopped"]

class CreateExp(BaseModel):
    name: str = Field(..., examples=["headline-variants"])
    goal: str = Field(..., examples=["CTR"])
    a: str = Field(..., description="Variant A payload (e.g., headline text)")
    b: str = Field(..., description="Variant B payload")

class Experiment(BaseModel):
    id: str
    name: str
    goal: str
    a: str
    b: str
    status: Status = "created"
    created_at: float
    # very simple counters for demo/preview
    metrics: Dict[str, Dict[str, int]] = Field(
        default_factory=lambda: {
            "views": {"A": 0, "B": 0},
            "clicks": {"A": 0, "B": 0},
        }
    )

# In-memory store for the prototype
_DB: Dict[str, Experiment] = {}

def _get(exp_id: str) -> Experiment:
    exp = _DB.get(exp_id)
    if not exp:
        raise HTTPException(404, "Experiment not found")
    return exp

@router.post("", response_model=Experiment)
def create_exp(payload: CreateExp):
    exp_id = uuid4().hex
    exp = Experiment(
        id=exp_id,
        name=payload.name.strip(),
        goal=payload.goal.strip(),
        a=payload.a.strip(),
        b=payload.b.strip(),
        status="created",
        created_at=time.time(),
    )
    _DB[exp_id] = exp
    return exp

@router.get("/{exp_id}", response_model=Experiment)
def get_exp(exp_id: str):
    return _get(exp_id)

@router.post("/{exp_id}/start", response_model=Experiment)
def start_exp(exp_id: str):
    exp = _get(exp_id)
    exp.status = "running"
    _DB[exp_id] = exp
    return exp

@router.post("/{exp_id}/stop", response_model=Experiment)
def stop_exp(exp_id: str):
    exp = _get(exp_id)
    exp.status = "stopped"
    _DB[exp_id] = exp
    return exp

@router.get("/{exp_id}/assign")
def assign_variant(
    exp_id: str,
    user_id: Optional[str] = Query(None, description="Stable assignment key"),
):
    """
    Deterministic 50/50 split by user_id; random-ish if none provided.
    """
    exp = _get(exp_id)
    if exp.status != "running":
        raise HTTPException(400, "Experiment is not running")
    key = user_id or uuid4().hex
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    variant = "A" if int(h, 16) % 2 == 0 else "B"
    # bump a naive view counter for demo purposes
    exp.metrics["views"][variant] += 1
    return {"experiment_id": exp_id, "variant": variant}

@router.post("/{exp_id}/click")
def click(exp_id: str, variant: Literal["A", "B"]):
    exp = _get(exp_id)
    exp.metrics["clicks"][variant] += 1
    return {"ok": True, "metrics": exp.metrics}
