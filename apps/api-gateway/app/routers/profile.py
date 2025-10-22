from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/profile", tags=["profile"])

class AnalyzeReq(BaseModel):
    headline: str
    about: str

class AnalyzeRes(BaseModel):
    strengths: List[str]
    themes: List[str]
    suggestions: List[str]

KEY_THEMES = {
    "rag": "Retrieval quality & evals",
    "agent": "Agentic workflows & orchestration",
    "pm": "Product thinking & outcome focus",
    "ml": "ML engineering & data pipelines",
    "ops": "Reliability & observability",
    "open source": "OSS adoption & tooling",
    "latency": "Perf, latency, and cost",
    "eval": "Task-level evaluation",
}

def _extract_themes(text: str) -> list[str]:
    t = text.lower()
    found = []
    for k, v in KEY_THEMES.items():
        if k in t and v not in found:
            found.append(v)
    # default fallbacks if nothing matched
    if not found:
        found = ["Outcome-driven PM", "AI/ML product delivery"]
    return found[:6]

def _strengths(headline: str, about: str) -> list[str]:
    s = []
    hl = headline.lower()
    ab = about.lower()
    if "pm" in hl or "product" in hl:
        s.append("Product strategy & prioritization")
    if "rag" in ab:
        s.append("RAG system design & retrieval quality")
    if "agent" in ab:
        s.append("Agentic patterns for complex tasks")
    if "ml" in ab or "ai" in ab:
        s.append("AI/ML feature delivery")
    if "ship" in ab or "shipped" in ab:
        s.append("Bias to ship and iterate")
    if not s:
        s = ["Clear communication", "Hands-on delivery"]
    return list(dict.fromkeys(s))[:6]

def _suggestions(headline: str, about: str) -> list[str]:
    tips = [
        "Add 1–2 quantified outcomes (e.g., deflection +12%, TTA −40%).",
        "Link to one public case study or demo thread.",
        "Tighten niche keywords to improve discoverability (e.g., 'RAG evals', 'agentic ops').",
        "Use a short CTA in the About to invite conversations.",
    ]
    if len(about.split()) < 40:
        tips.insert(0, "Expand the About to ~80–120 words with concrete wins.")
    if len(headline) < 40:
        tips.append("Make the headline benefit-led (what value you create).")
    return tips[:5]

@router.post("/analyze", response_model=AnalyzeRes)
def analyze(req: AnalyzeReq):
    return {
        "strengths": _strengths(req.headline, req.about),
        "themes": _extract_themes(req.about + " " + req.headline),
        "suggestions": _suggestions(req.headline, req.about),
    }
