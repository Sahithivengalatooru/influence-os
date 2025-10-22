from __future__ import annotations
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

from app.agents.image_agent import generate_image

router = APIRouter(prefix="/images", tags=["images"])

Template = Literal["poster", "split", "quote", "stat"]
Ratio = Literal["square", "portrait", "landscape"]

class ImageReq(BaseModel):
    title: str = Field(..., examples=["AI + community building tips"])
    bullets: Optional[List[str]] = Field(default=None, examples=[["Host office hours", "Run AMAs", "Celebrate wins"]])
    template: Template = "poster"
    brand: str = Field(default="slate", description="slate | indigo | emerald | rose | amber")
    ratio: Ratio = "square"
    width: int = Field(default=1080, ge=640, le=2000)
    seed: Optional[int] = None

class ImageRes(BaseModel):
    width: int
    height: int
    data_url: str

@router.post("/generate", response_model=ImageRes)
def generate(req: ImageReq):
    data_url = generate_image(
        title=req.title,
        bullets=req.bullets,
        template=req.template,
        brand=req.brand,
        ratio=req.ratio,
        width=req.width,
        seed=req.seed,
    )
    h = req.width if req.ratio == "square" else (int(req.width * 1.25) if req.ratio == "portrait" else int(req.width * 0.56))
    return {"width": req.width, "height": h, "data_url": data_url}

# Handy GET for quick tests in browser: /v1/images/generate?title=Hello&template=quote
@router.get("/generate", response_model=ImageRes)
def generate_get(
    title: str = Query(...),
    bullets: Optional[str] = Query(None, description="Comma-separated"),
    template: Template = Query("poster"),
    brand: str = Query("slate"),
    ratio: Ratio = Query("square"),
    width: int = Query(1080, ge=640, le=2000),
    seed: Optional[int] = Query(None),
):
    bl = [b.strip() for b in (bullets.split(",") if bullets else []) if b.strip()]
    data_url = generate_image(title=title, bullets=bl, template=template, brand=brand, ratio=ratio, width=width, seed=seed)
    h = width if ratio == "square" else (int(width * 1.25) if ratio == "portrait" else int(width * 0.56))
    return {"width": width, "height": h, "data_url": data_url}
