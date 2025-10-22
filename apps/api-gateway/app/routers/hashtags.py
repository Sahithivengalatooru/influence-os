from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/hashtags", tags=["hashtags"])

class Req(BaseModel):
    topic: str

@router.post("/suggest")
def suggest(req: Req):
    # very simple tokenization → hashtags + a few defaults
    words = [w.strip("#,.;:") for w in req.topic.lower().replace("/", " ").split()]
    tags = []
    for w in words:
        if not w:
            continue
        tag = "#" + w.replace(" ", "")
        if tag not in tags:
            tags.append(tag)
    for extra in ["#growth", "#ai", "#product"]:
        if extra not in tags:
            tags.append(extra)
    return {"hashtags": tags[:8]}
