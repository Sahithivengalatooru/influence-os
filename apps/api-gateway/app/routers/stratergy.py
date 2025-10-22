from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/strategy", tags=["strategy"])

class Pillar(BaseModel):
  name: str
  description: str

class Cadence(BaseModel):
  per_week: int
  windows: List[str]

class Plan(BaseModel):
  objectives: List[str]
  pillars: List[Pillar]
  cadence: Cadence
  kpis: List[str]
  next_steps: List[str]

def _stub_plan() -> Plan:
  return Plan(
    objectives=[
      "Grow qualified followers",
      "Establish topic authority",
      "Generate warm conversations (DMs)"
    ],
    pillars=[
      Pillar(name="Case studies", description="Short wins with numbers and lessons"),
      Pillar(name="How-to", description="Tactical posts that teach one pattern"),
      Pillar(name="Opinions", description="Respectful takes on industry trends")
    ],
    cadence=Cadence(per_week=3, windows=["Tue 9:00", "Thu 11:00", "Sat 10:00"]),
    kpis=["CTR", "Saves", "Comments", "Profile visits"],
    next_steps=["Draft 3 posts", "Schedule next week", "Add one carousel"]
  )

@router.post("/plan", response_model=Plan)
def plan():
  # Optional agent hook; safe fallback
  try:
    from app.agents.content_agent import strategy_plan  # type: ignore
    maybe = strategy_plan()
    if isinstance(maybe, dict): return Plan(**maybe)
    if isinstance(maybe, Plan): return maybe
  except Exception:
    pass
  return _stub_plan()
