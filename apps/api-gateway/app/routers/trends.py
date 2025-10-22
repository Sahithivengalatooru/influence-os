from __future__ import annotations
from fastapi import APIRouter, Query
from datetime import datetime
import random

router = APIRouter(prefix="/trends", tags=["trends"])

def _maybe_agent(industry: str, seed: str) -> list[str] | None:
    """Use an agent if you have one; expect a List[str] back."""
    try:
        from app.agents import research_agent  # type: ignore
        fn = getattr(research_agent, "get_trends", None)
        if callable(fn):
            out = fn(industry=industry, seed=seed)
            if isinstance(out, list) and all(isinstance(x, str) for x in out):
                return out
    except Exception:
        pass
    return None

def _pool(industry: str, seed: str) -> list[str]:
    s = seed.strip()
    i = industry.strip()
    base = [
        s,
        f"{s} best practices",
        f"{s} pitfalls",
        f"{s} evaluation",
        f"{s} guardrails",
        f"{s} ROI",
        f"{s} case studies",
        f"{s} vs alternatives",
        f"{s} open-source tooling",
        f"{s} benchmarks",
        f"{s} observability",
        f"{s} in production",
        f"{s} hallucinations",
        f"{s} retrieval quality",
        f"{s} data pipelines",
        f"{s} small models",
        f"{s} latency & cost",
        f"{s} PM playbook",
        f"{s} adoption metrics",
        f"{s} onboarding",
        f"{s} architecture",
        f"{s} eval datasets",
        f"{s} privacy & compliance",
        f"{s} human-in-the-loop",
        f"{s} error analysis",
        f"{i} news",
        f"{i} trends",
        "case studies",
        "tooling landscape",
        "benchmarks",
    ]
    # de-dupe while preserving order
    seen, out = set(), []
    for t in base:
        if t not in seen:
            seen.add(t); out.append(t)
    return out

@router.get("")
def list_trends(
    industry: str = Query("AI/ML", description="Industry keyword"),
    seed: str = Query("RAG", description="Seed topic or keyword"),
    n: int = Query(10, ge=3, le=25, description="How many topics to return"),
    shuffle: bool = Query(True, description="Shuffle the pool for variety"),
    salt: str | None = Query(None, description="Optional entropy; any string"),
):
    # 1) Prefer agent output if present
    agent_topics = _maybe_agent(industry, seed)
    pool = agent_topics or _pool(industry, seed)

    # 2) Entropy so repeated calls can differ
    r = random.Random()
    if salt:
        r.seed(f"{industry}|{seed}|{salt}")
    elif shuffle:
        # minute tick makes result change over time even with same inputs
        r.seed(f"{industry}|{seed}|{datetime.utcnow().strftime('%Y%m%d%H%M')}")

    if shuffle:
        r.shuffle(pool)

    return {"topics": pool[:n]}
