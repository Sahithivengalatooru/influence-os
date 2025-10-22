#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RDIR="$ROOT/apps/api-gateway/app/routers"
mkdir -p "$RDIR"

write_if_missing() {
  local path="$1"; shift
  if [ -f "$path" ]; then
    echo "skip: $path (exists)"
  else
    echo "create: $path"
    cat > "$path" <<'PY'
$CONTENT
PY
  fi
}

# users.py
CONTENT='from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Dict
from uuid import uuid4

router = APIRouter(prefix="/users", tags=["users"])
_USERS: Dict[str, Dict] = {}

class SignupReq(BaseModel):
    email: EmailStr
    password: str

class LoginReq(BaseModel):
    email: EmailStr
    password: str

class TokenRes(BaseModel):
    access_token: str
    token_type: str = "bearer"

def _token_for(email: str) -> str:
    # demo-only: not cryptographically secure
    return f"dev.{email}.{uuid4().hex}"

@router.post("/signup", response_model=TokenRes)
def signup(req: SignupReq):
    if req.email in _USERS:
        raise HTTPException(400, "User exists")
    _USERS[req.email] = {"email": req.email, "password": req.password, "role":"user"}
    return {"access_token": _token_for(req.email)}

@router.post("/login", response_model=TokenRes)
def login(req: LoginReq):
    u = _USERS.get(req.email)
    if not u or u["password"] != req.password:
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": _token_for(req.email)}

@router.get("/me")
def me():
    # demo: no real auth middleware; return a static user
    return {"email":"demo@example.com", "role":"user"}'
write_if_missing "$RDIR/users.py"

# profile.py
CONTENT='from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/profile", tags=["profile"])

class ProfileReq(BaseModel):
    headline: str
    about: str

class ProfileRes(BaseModel):
    strengths: List[str]
    gaps: List[str]
    suggestions: List[str]

@router.post("/analyze", response_model=ProfileRes)
def analyze(req: ProfileReq):
    strengths = ["clear niche", "practical examples"] if "example" in req.about.lower() else ["niche clarity"]
    gaps = ["add proof points"] if "case" not in req.about.lower() else []
    suggestions = ["Add 1 metric to headline", "Pin 3 top posts", "Clarify CTA"]
    return {"strengths": strengths, "gaps": gaps, "suggestions": suggestions}'
write_if_missing "$RDIR/profile.py"

# trends.py (only if missing; you may already have it)
CONTENT='from fastapi import APIRouter, Query
router = APIRouter(prefix="/trends", tags=["trends"])

def _get_trends(industry: str, seed: str):
    base = [seed, f"{seed} best practices", f"{seed} pitfalls", f"{industry} news", "case studies"]
    # dedupe & cap
    out=[]; seen=set()
    for t in base:
        if t not in seen:
            out.append(t); seen.add(t)
    return out[:7]

@router.get("")
def list_trends(industry: str = Query("AI/ML"), seed: str = Query("RAG")):
    return {"topics": _get_trends(industry, seed)}'
write_if_missing "$RDIR/trends.py"

# strategy.py (you were missing this; include)
CONTENT='from typing import List
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
        objectives=["Grow qualified followers","Establish topic authority","Generate warm DMs"],
        pillars=[Pillar(name="Case studies", description="Short wins"),
                 Pillar(name="How-to", description="Tactics that teach"),
                 Pillar(name="Opinions", description="Respectful takes")],
        cadence=Cadence(per_week=3, windows=["Tue 09:00","Thu 11:00","Sat 10:00"]),
        kpis=["CTR","Saves","Comments","Profile visits"],
        next_steps=["Draft 3 posts","Schedule next week","Add one carousel"],
    )

@router.post("/plan", response_model=Plan)
def plan():
    try:
        from app.agents.content_agent import strategy_plan  # type: ignore
        maybe = strategy_plan()
        if isinstance(maybe, dict): return Plan(**maybe)
        if isinstance(maybe, Plan): return maybe
    except Exception:
        pass
    return _stub_plan()'
write_if_missing "$RDIR/strategy.py"

# content.py (you might already have; keep minimal)
CONTENT='from typing import Literal, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/content", tags=["content"])
PostType = Literal["text","article","carousel","poll"]

class GenReq(BaseModel):
    type: PostType
    topic: str
    brand_voice: Optional[str] = "confident, friendly, concise"
    language: Optional[str] = "en"
    n_variants: int = Field(default=2, ge=1, le=5)

class GenRes(BaseModel):
    variants: List[str]

def _stub(req: GenReq) -> List[str]:
    base = {
        "text": "3 takeaways on {topic}: context, evals, ship small wins.",
        "article": "Why {topic} matters, how to start, and pitfalls.",
        "carousel": "Cover: {topic} • S2 problem • S3 framework • S4 tactics • S5 example • S6 metrics • S7 CTA",
        "poll": "What blocks {topic} most at your org?"
    }
    return [base.get(req.type, "{topic}").format(topic=req.topic)+f" (v{i+1})" for i in range(req.n_variants)]

@router.post("/generate", response_model=GenRes)
def generate(req: GenReq):
    try:
        from app.agents import content_agent  # type: ignore
        fn = getattr(content_agent, "generate_variants", None) or getattr(content_agent, "generate", None)
        if callable(fn):
            out = fn(type=req.type, topic=req.topic, brand_voice=req.brand_voice, language=req.language, n=req.n_variants, n_variants=req.n_variants)
            if isinstance(out, dict) and "variants" in out: return {"variants":[str(x) for x in out["variants"]]}
            if isinstance(out, list): return {"variants":[str(x) for x in out]}
            if isinstance(out, str): return {"variants":[out]}
    except Exception:
        pass
    return {"variants": _stub(req)}'
write_if_missing "$RDIR/content.py"

# calendar.py (missing in your error)
CONTENT='from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
from uuid import uuid4

router = APIRouter(prefix="/calendar", tags=["calendar"])
Status = Literal["draft","scheduled","published"]

class Item(BaseModel):
    id: str
    date: str  # YYYY-MM-DD
    title: str
    status: Status = "draft"

_DB: List[Item] = []

@router.get("", response_model=List[Item])
def list_items():
    return _DB

@router.post("", response_model=Item)
def create_item(date: str, title: str):
    it = Item(id=uuid4().hex, date=date, title=title, status="draft")
    _DB.append(it)
    return it

@router.put("/{item_id}", response_model=Item)
def update_item(item_id: str, item: Item):
    for i, it in enumerate(_DB):
        if it.id == item_id:
            _DB[i] = item
            return item
    raise HTTPException(404, "Not found")

@router.delete("/{item_id}")
def delete_item(item_id: str):
    global _DB
    before = len(_DB)
    _DB = [it for it in _DB if it.id != item_id]
    return {"ok": len(_DB) < before}'
write_if_missing "$RDIR/calendar.py"

# linkedin.py
CONTENT='from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix="/linkedin", tags=["linkedin"])
_SCHEDULED: List[Dict] = []
_PUBLISHED: List[Dict] = []

class ScheduleReq(BaseModel):
    scheduled_at: str
    text: str
    media_urls: List[str] | None = None

@router.post("/schedule")
def schedule(req: ScheduleReq):
    sid = uuid4().hex
    _SCHEDULED.append({"id": sid, **req.dict()})
    return {"ok": True, "scheduled_id": sid}

@router.get("/scheduled")
def scheduled():
    return {"ok": True, "items": _SCHEDULED}

@router.post("/publish")
def publish_now(text: str, media_urls: List[str] | None = None):
    pid = uuid4().hex
    _PUBLISHED.append({"id": pid, "text": text, "media_urls": media_urls, "published_at": datetime.utcnow().isoformat()+"Z"})
    return {"ok": True, "post_id": pid, "status":"published"}

@router.get("/metrics")
def metrics():
    return {"ok": True, "user": "demo@example.com", "metrics": {"followers": 1200, "avg_engagement": 2.1}}'
write_if_missing "$RDIR/linkedin.py"

# analytics.py
CONTENT='from fastapi import APIRouter, Query
router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
def summary():
    return {"ok": True, "series": {"likes":[10,18,14,22,30,26,33], "comments":[2,5,3,4,6,5,7], "shares":[1,2,2,3,4,3,5], "ctr":[1.2,1.5,1.1,1.8,2.1,2.0,2.4], "reach":[300,420,380,520,600,570,680]}}

@router.get("/kpi")
def kpi(metric: str = Query("likes"), range_days: int = Query(7)):
    series = {"likes":[10,18,14,22,30,26,33], "comments":[2,5,3,4,6,5,7], "shares":[1,2,2,3,4,3,5], "ctr":[1.2,1.5,1.1,1.8,2.1,2.0,2.4], "reach":[300,420,380,520,600,570,680]}
    return {"metric": metric, "values": series.get(metric, [])[:range_days] }'
write_if_missing "$RDIR/analytics.py"

# hashtags.py
CONTENT='from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter(prefix="/hashtags", tags=["hashtags"])

class Req(BaseModel):
    topic: str

@router.post("/suggest")
def suggest(req: Req):
    words = [w.strip("#,.;:") for w in req.topic.lower().split() if w.isalpha() or "-" in w]
    tags = list(dict.fromkeys([f"#{w}" for w in words] + ["#growth","#ai","#product"]))[:8]
    return {"hashtags": tags}'
write_if_missing "$RDIR/hashtags.py"

# moderation.py
CONTENT='from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter(prefix="/moderation", tags=["moderation"])

BLOCKLIST = {"hate","violence","self-harm"}
class Req(BaseModel):
    text: str

@router.post("/check")
def check(req: Req):
    t = req.text.lower()
    flagged = any(b in t for b in BLOCKLIST)
    reasons = [b for b in BLOCKLIST if b in t]
    return {"ok": not flagged, "flagged": flagged, "reasons": reasons}'
write_if_missing "$RDIR/moderation.py"

# abtests.py
CONTENT='from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from uuid import uuid4
import hashlib

router = APIRouter(prefix="/abtests", tags=["abtests"])
_EXPS: Dict[str, Dict] = {}

class CreateReq(BaseModel):
    name: str
    goal: str
    a: str
    b: str

@router.post("")
def create(req: CreateReq):
    i = uuid4().hex
    _EXPS[i] = {"id": i, "name": req.name, "goal": req.goal, "a": req.a, "b": req.b, "status":"draft"}
    return _EXPS[i]

@router.get("/{exp_id}")
def get(exp_id: str):
    if exp_id not in _EXPS: raise HTTPException(404, "not found")
    return _EXPS[exp_id]

@router.post("/{exp_id}/start")
def start(exp_id: str):
    if exp_id not in _EXPS: raise HTTPException(404, "not found")
    _EXPS[exp_id]["status"]="running"; return _EXPS[exp_id]

@router.post("/{exp_id}/stop")
def stop(exp_id: str, winner: str | None = None):
    if exp_id not in _EXPS: raise HTTPException(404, "not found")
    _EXPS[exp_id]["status"]="stopped"; _EXPS[exp_id]["winner"]=winner; return _EXPS[exp_id]

@router.get("/{exp_id}/assign")
def assign(exp_id: str, user_id: str):
    if exp_id not in _EXPS: raise HTTPException(404, "not found")
    arm = "a" if int(hashlib.sha256(user_id.encode()).hexdigest(),16) % 2 == 0 else "b"
    return {"exp_id": exp_id, "user_id": user_id, "arm": arm}'
write_if_missing "$RDIR/abtests.py"

# competitors.py
CONTENT='from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter(prefix="/competitors", tags=["competitors"])

@router.get("")
def list_competitors():
    path = Path(__file__).resolve().parents[3] / "data" / "examples" / "competitors.json"
    if path.exists():
        data = json.loads(path.read_text())
        return {"ok": True, "competitors": data.get("competitors", [])}
    # fallback
    return {"ok": True, "competitors": [{"handle":"@acme","posts_7d":6,"avg_engagement":2.3,"top_post":"RAG wins"}]}'
write_if_missing "$RDIR/competitors.py"

# sentiment.py
CONTENT='from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter(prefix="/sentiment", tags=["sentiment"])

POS = {"great","good","love","win","ship","fast"}
NEG = {"bad","hate","slow","bug","blocker"}

class Req(BaseModel):
    text: str

@router.post("/analyze")
def analyze(req: Req):
    t = req.text.lower()
    p = sum(1 for w in POS if w in t); n = sum(1 for w in NEG if w in t)
    if p>n: label="positive"; score=min(1.0, 0.5 + 0.1*p)
    elif n>p: label="negative"; score=min(1.0, 0.5 + 0.1*n)
    else: label="neutral"; score=0.5
    return {"label": label, "score": score}'
write_if_missing "$RDIR/sentiment.py"

# translate.py
CONTENT='from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter(prefix="/translate", tags=["translate"])

class Req(BaseModel):
    text: str
    target_lang: str = "en"

@router.post("")
def translate(req: Req):
    # demo: pretend it is translated
    return {"text": req.text, "lang": req.target_lang}'
write_if_missing "$RDIR/translate.py"

# images.py (only if you don’t already have it)
CONTENT='from fastapi import APIRouter
from pydantic import BaseModel, Field
import base64

router = APIRouter(prefix="/images", tags=["images"])

class ImageReq(BaseModel):
    prompt: str
    style: str = Field(default="minimal")
    size: str = Field(default="1024x1024")

class ImageRes(BaseModel):
    image_data_uri: str

def _svg_stub(prompt: str, style: str, size: str) -> str:
    w, h = (int(x) for x in size.lower().split("x")[:2])
    svg = f"<svg xmlns=\\"http://www.w3.org/2000/svg\\" width=\\"{w}\\" height=\\"{h}\\"><rect width=\\"100%\\" height=\\"100%\\" fill=\\"#111\\"/><text x=\\"50%\\" y=\\"50%\\" dominant-baseline=\\"middle\\" text-anchor=\\"middle\\" fill=\\"#fff\\" font-size=\\"{min(w,h)//16}\\">{style}: {prompt[:64]}</text></svg>"
    b64 = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{b64}"

@router.post("/generate", response_model=ImageRes)
def generate(req: ImageReq):
    return {"image_data_uri": _svg_stub(req.prompt, req.style, req.size)}'
write_if_missing "$RDIR/images.py"

# growth.py
CONTENT='from fastapi import APIRouter
router = APIRouter(prefix="/growth", tags=["growth"])

@router.get("/checklist")
def checklist():
    return {"quick_wins": ["Tighten headline","Pin top 3 posts","Post 3x/week"],
            "playbooks": ["Case study mini","How-to thread","Carousel 7 slides"],
            "profile_tips": ["Add proof points","CTA to DM","Update banner"]}'
write_if_missing "$RDIR/growth.py"

# export.py
CONTENT='from fastapi import APIRouter, Response
import csv, io, json

router = APIRouter(prefix="/export", tags=["export"])

_SERIES = {"likes":[10,18,14,22,30,26,33], "comments":[2,5,3,4,6,5,7], "shares":[1,2,2,3,4,3,5], "ctr":[1.2,1.5,1.1,1.8,2.1,2.0,2.4], "reach":[300,420,380,520,600,570,680]}

@router.get("/analytics.json")
def analytics_json():
    return {"ok": True, "series": _SERIES}

@router.get("/analytics.csv")
def analytics_csv():
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["metric","values"])
    for k,v in _SERIES.items():
        w.writerow([k, ";".join(map(str,v))])
    return Response(content=buf.getvalue(), media_type="text/csv")'
write_if_missing "$RDIR/export.py"

echo "Done."
