from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Literal

from app.auth.jwt import get_current_user, JWTPayload

router = APIRouter(prefix="/translate", tags=["translate"])


class TransReq(BaseModel):
    text: str
    target_lang: Literal["en", "hi", "es"] = "en"


class TransRes(BaseModel):
    text: str
    lang: str


# Prototype: trivial mapping. Replace with NLLB/M2M later.
LEX = {("Hello", "hi"): "नमस्ते", ("Hello", "es"): "Hola"}


@router.post("/", response_model=TransRes)
def translate(req: TransReq, user: JWTPayload = Depends(get_current_user)) -> TransRes:
    if (req.text, req.target_lang) in LEX:
        return TransRes(text=LEX[(req.text, req.target_lang)], lang=req.target_lang)
    return TransRes(text=req.text, lang=req.target_lang)
