from __future__ import annotations

from typing import Literal, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
import os
import random
import textwrap

router = APIRouter(prefix="/content", tags=["content"])

PostType = Literal["text", "article", "carousel", "poll"]
PostLength = Literal["short", "medium", "long"]  # ~60-90 / 150-250 / 400-600 words (approx)

class GenReq(BaseModel):
    type: PostType
    topic: str
    brand_voice: Optional[str] = Field(default="confident, friendly, concise")
    language: Optional[str] = Field(default="en")
    n_variants: int = Field(default=2, ge=1, le=6)
    length: PostLength = "medium"  # NEW: control verbosity

class GenRes(BaseModel):
    variants: List[str]

# -------- Utilities

ANGLES = [
    "why-it-matters",
    "how-to",
    "checklist",
    "case-study",
    "myth-busting",
    "contrarian",
    "framework",
    "story",
    "metrics",
    "pitfalls",
]

HOOKS = [
    "Most teams ship features—few ship outcomes.",
    "If you’re still betting on bigger context windows, read this.",
    "Here’s the playbook we wish we had six months ago.",
    "Short thread for operators who like numbers.",
    "This is the difference between demos and production.",
]

CTAS = [
    "Curious how this maps to your stack? DM me.",
    "Save this for next sprint planning.",
    "Share with the teammate who owns search.",
    "Reply with what you’d add or change.",
    "Want the full checklist? Comment 'PLAYBOOK'.",
]

def _rng(seed_hint: str) -> random.Random:
    # deterministic-but-different per variant/topic
    return random.Random(seed_hint)

def _pick(r: random.Random, items: List[str]) -> str:
    return items[r.randrange(len(items))]

def _words_for(length: PostLength) -> tuple[int, int]:
    return {
        "short": (60, 90),
        "medium": (150, 250),
        "long": (400, 600),
    }[length]

def _pad_to_range(text: str, length: PostLength, r: random.Random) -> str:
    # Quick-and-dirty length normalizer (adds a small appendix if too short)
    lo, hi = _words_for(length)
    words = text.split()
    if len(words) >= lo:
        return text
    extras = [
        "Prune scope, define a measurable outcome, and iterate weekly.",
        "Start small, benchmark baselines, and write down what you’ll stop doing.",
        "Ship a thin slice, instrument the path, and review real user journeys.",
    ]
    while len(words) < lo:
        add = _pick(r, extras)
        words.extend(add.split())
    return " ".join(words[: hi])

# -------- Optional OSS LLM (vLLM) path

def _llm_generate(req: GenReq, i: int) -> Optional[str]:
    """
    If VLLM_BASE_URL is set and httpx is available, ask an OSS model (e.g. Llama 3.1 8B).
    Uses OpenAI-compatible /v1/chat/completions (common in vLLM).
    Returns a string on success, or None to fall back to template generation.
    """
    base = os.getenv("VLLM_BASE_URL")
    if not base:
        return None

    try:
        import httpx  # optional dep; if missing we fall back
    except Exception:
        return None

    model = os.getenv("VLLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")
    sys = (
        f"You are an assistant that writes high-signal LinkedIn content in the brand voice: "
        f"{req.brand_voice}. Write in {req.language}. Avoid fluff; prefer concrete tips."
    )
    angle = ANGLES[i % len(ANGLES)]
    prompt = (
        f"Create a {req.type} about '{req.topic}' with angle '{angle}'. "
        f"Length: {req.length}. Return only the content. "
        f"If type=carousel, provide 7 short slides prefixed 'Slide N:'. "
        f"If type=poll, provide a question and 4 options."
    )
    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{base.rstrip('/')}/v1/chat/completions",
                json={
                    "model": model,
                    "temperature": 0.9,
                    "top_p": 0.95,
                    "messages": [
                        {"role": "system", "content": sys},
                        {"role": "user", "content": prompt},
                    ],
                },
            )
        if resp.status_code >= 400:
            return None
        data = resp.json()
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        return content or None
    except Exception:
        return None

# -------- Template-based generator (no model needed)

def _gen_text(req: GenReq, r: random.Random, i: int) -> str:
    hook = _pick(r, HOOKS)
    angle = ANGLES[i % len(ANGLES)]
    cta = _pick(r, CTAS)
    body = ""

    if angle == "why-it-matters":
        body = f"{hook} Here’s why {req.topic} actually moves the needle: speed-to-insight, lower toil, and fewer dead-ends."
    elif angle == "how-to":
        body = f"How to apply {req.topic} this week: pick one noisy workflow, add guardrails, and measure a real KPI—not token usage."
    elif angle == "checklist":
        items = [
            f"Define success (ex: reduce search time by 30%)",
            "Pin a narrow slice and limit context",
            "Evaluate on user tasks—not synthetic",
            "Add feedback loops and safe fallbacks",
            "Review outcomes weekly, not models",
        ]
        body = "Checklist:\n" + "\n".join([f"• {x}" for x in items])
    elif angle == "case-study":
        body = f"At a mid-market SaaS, {req.topic} cut mean search time from 42s → 18s and raised self-serve by 12%. The trick: ruthless scoping and fast feedback."
    elif angle == "myth-busting":
        body = f"Three myths about {req.topic}: 1) ‘Bigger context fixes recall’ 2) ‘Eval = high BLEU’ 3) ‘Release when perfect’. Reality: small slices + outcome evals."
    elif angle == "contrarian":
        body = f"Hot take: stop chasing ‘state-of-the-art’. For {req.topic}, boring architectures win—because they’re observable and cheap to iterate."
    elif angle == "framework":
        body = f"Framework for {req.topic}: (1) Problem framing (2) Data paths (3) Retrieval quality (4) Guardrails (5) Outcome evals (6) Ops."
    elif angle == "story":
        body = f"Last quarter we tried {req.topic}. First attempt flopped—noisy docs, no evals. We trimmed scope and added task-level checks. That’s when adoption moved."
    elif angle == "metrics":
        body = f"Stop measuring tokens. For {req.topic}, track time-to-answer, helpfulness, and deflection. If users don’t save time, it didn’t land."
    else:  # pitfalls
        body = f"Common pitfalls with {req.topic}: vague objectives, stuffing too much context, and skipping user validation. Fix those and your win-rate jumps."

    text = f"{body}\n\n{cta}"
    return _pad_to_range(text, req.length, r)

def _gen_article(req: GenReq, r: random.Random, i: int) -> str:
    angle = ANGLES[i % len(ANGLES)]
    title = {
        "how-to": f"How to make {req.topic} work in production",
        "case-study": f"{req.topic}: a 6-week rollout that stuck",
        "framework": f"A pragmatic framework for {req.topic}",
        "pitfalls": f"{req.topic}: 7 pitfalls (and how to avoid them)",
    }.get(angle, f"{req.topic}: what actually matters")

    sections = [
        ("The Problem", f"Teams chase demos, not outcomes. {req.topic} stalls when the scope is wide and feedback is slow."),
        ("What Good Looks Like", "Thin slices, explicit outcomes, and ruthless observability."),
        ("The Playbook", "Start small, instrument, and review weekly. Align evals with user tasks."),
        ("Metrics", "Time-to-answer, saves, deflection, CTR on helpful actions."),
        ("Next Steps", "Pick one workflow, define success, ship a slice, review in 7 days."),
    ]
    lines = [f"# {title}", ""]
    for h, p in sections:
        lines.append(f"## {h}")
        lines.append(textwrap.fill(p, width=90))
        lines.append("")
    lines.append(_pick(r, CTAS))
    out = "\n".join(lines)
    return _pad_to_range(out, req.length, r)

def _gen_carousel(req: GenReq, r: random.Random, i: int) -> str:
    slides = [
        f"Slide 1: {req.topic} — the 7-slide playbook",
        "Slide 2: Problem — demos wow, adoption stalls",
        "Slide 3: Scope — ship one narrow workflow",
        "Slide 4: Retrieval — quality beats bigger windows",
        "Slide 5: Evals — tie to user tasks",
        "Slide 6: Ops — guardrails, logs, feedback",
        "Slide 7: CTA — comment 'PLAYBOOK' for the checklist",
    ]
    return "\n".join(slides)

def _gen_poll(req: GenReq, r: random.Random, i: int) -> str:
    q = f"What blocks {req.topic} most at your org?"
    opts = ["Noisy docs", "Weak evals", "Wrong KPIs", "Complex ops"]
    return "\n".join([q] + [f"- {o}" for o in opts] + ["Duration: 3 days"])

# -------- Main orchestration

def _template_generate(req: GenReq) -> List[str]:
    r = _rng(req.topic + req.brand_voice + req.length)
    out: List[str] = []
    for i in range(req.n_variants):
        if req.type == "text":
            out.append(_gen_text(req, r, i))
        elif req.type == "article":
            out.append(_gen_article(req, r, i))
        elif req.type == "carousel":
            out.append(_gen_carousel(req, r, i))
        elif req.type == "poll":
            out.append(_gen_poll(req, r, i))
    return out

def _hybrid_generate(req: GenReq) -> List[str]:
    """
    Try OSS LLM for each variant; on failure, fall back to templates.
    Set VLLM_BASE_URL (and optionally VLLM_MODEL) to enable.
    """
    results: List[str] = []
    for i in range(req.n_variants):
        content = _llm_generate(req, i)
        if not content:
            # fallback to template for this slot only
            content = _template_generate(GenReq(**{**req.dict(), "n_variants": 1}))[0]
        results.append(content)
    return results

@router.post("/generate", response_model=GenRes)
def generate(req: GenReq):
    # OSS LLM path if configured, else pure templates (still diverse)
    if os.getenv("VLLM_BASE_URL"):
        variants = _hybrid_generate(req)
    else:
        variants = _template_generate(req)
    return {"variants": variants}
