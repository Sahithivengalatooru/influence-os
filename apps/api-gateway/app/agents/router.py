# apps/api-gateway/app/agents/router.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict

# Import siblings directly (bypasses package __init__ to avoid cycles)
# Content generators: support either `draft_post` (new) or `generate_text` (older stub)
try:
    from .content_agent import draft_post as _draft_post  # preferred
except Exception:  # pragma: no cover - optional
    _draft_post = None  # type: ignore[assignment]

try:
    from .content_agent import generate_text as _generate_text  # fallback
except Exception:  # pragma: no cover - optional
    _generate_text = None  # type: ignore[assignment]

from .research_agent import trend_topics, topic_cards
from .image_agent import generate_image


router = APIRouter(prefix="/agents", tags=["agents"])


# ---------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------

PostType = Literal["text", "article", "carousel", "poll"]

class GenReq(BaseModel):
    type: PostType = "text"
    topic: str
    voice: Optional[str] = Field(
        default="confident, friendly, concise",
        description="Brand voice hint (comma-separated adjectives are fine).",
    )
    lang: str = "en"
    variants: int = Field(3, ge=1, le=6)

class GenRes(BaseModel):
    items: List[str]

class ImgReq(BaseModel):
    title: str
    bullets: Optional[List[str]] = None
    template: Literal["poster", "split", "quote", "stat"] = "poster"
    brand: str = Field(default="slate", description="slate | indigo | emerald | rose | amber")
    ratio: Literal["square", "portrait", "landscape"] = "square"
    width: int = Field(1080, ge=640, le=2000)
    seed: Optional[int] = None
    # Optional quality knob if your image agent supports variant ranking later
    n_candidates: int = Field(1, ge=1, le=12)

class ImgRes(BaseModel):
    width: int
    height: int
    data_url: str

class TopicCardsRes(BaseModel):
    topic: str
    hooks: List[str]
    hashtags: List[str]


# ---------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------

def _generate_variants(kind: PostType, topic: str, voice: str, lang: str, n: int) -> List[str]:
    """
    Use new `draft_post` if available; otherwise fall back to older `generate_text`.
    """
    if _draft_post is not None:
        return _draft_post(
            topic=topic,
            brand_voice=voice or "confident, friendly, concise",
            post_type=kind,
            n_variants=n,
            language=lang,
        )
    if _generate_text is not None:
        return _generate_text(
            kind=kind, topic=topic, voice=voice or "", lang=lang, n=n
        )
    # Last-resort stub (should not happen if content_agent exists)
    return [f"[DEMO {kind.upper()}] {topic} — {voice} (v{i+1})" for i in range(n)]


# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------

@router.get("/health", include_in_schema=False)
def health():
    return {"ok": True, "service": "agents"}

# -------- Content --------

@router.post("/content/generate", response_model=GenRes)
def content_generate(req: GenReq):
    items = _generate_variants(
        kind=req.type, topic=req.topic, voice=req.voice or "", lang=req.lang, n=req.variants
    )
    return {"items": items}

# -------- Research --------

@router.get("/research/topics")
def research_topics(
    industry: str = Query("AI/ML"),
    seed: str = Query("RAG"),
    n: int = Query(10, ge=1, le=50),
    shuffle: bool = Query(True),
):
    topics = trend_topics(industry=industry, seed=seed, n=n, shuffle=shuffle)
    return {"topics": topics}

@router.get("/research/cards", response_model=List[TopicCardsRes])
def research_topic_cards(
    industry: str = Query("AI/ML"),
    seed: str = Query("RAG"),
    n: int = Query(8, ge=1, le=24),
):
    return topic_cards(industry=industry, seed=seed, n=n)

# -------- Images --------

@router.post("/images/generate", response_model=ImgRes)
def images_generate(req: ImgReq):
    data_url = generate_image(
        title=req.title,
        bullets=req.bullets,
        template=req.template,
        brand=req.brand,
        ratio=req.ratio,
        width=req.width,
        seed=req.seed,
    )
    height = req.width if req.ratio == "square" else (
        int(req.width * 1.25) if req.ratio == "portrait" else int(req.width * 0.56)
    )
    return {"width": req.width, "height": height, "data_url": data_url}

# Handy GET for quick manual tests in the browser:
@router.get("/images/generate", response_model=ImgRes)
def images_generate_get(
    title: str = Query(...),
    bullets: Optional[str] = Query(None, description="Comma- or semicolon-separated bullets"),
    template: Literal["poster", "split", "quote", "stat"] = Query("poster"),
    brand: str = Query("slate"),
    ratio: Literal["square", "portrait", "landscape"] = Query("square"),
    width: int = Query(1080, ge=640, le=2000),
    seed: Optional[int] = Query(None),
):
    bl = []
    if bullets:
        # split on commas/semicolons
        parts = [p.strip() for p in bullets.replace(";", ",").split(",")]
        bl = [p for p in parts if p]
    data_url = generate_image(
        title=title, bullets=bl, template=template, brand=brand, ratio=ratio, width=width, seed=seed
    )
    height = width if ratio == "square" else (
        int(width * 1.25) if ratio == "portrait" else int(width * 0.56)
    )
    return {"width": width, "height": height, "data_url": data_url}
