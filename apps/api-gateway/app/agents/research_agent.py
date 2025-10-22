# apps/api-gateway/app/agents/research_agent.py
from __future__ import annotations

"""
Lightweight, dependency-free "research" helper for the prototype.

- Produces a list of trending topics for a given industry and seed.
- Deterministic-ish variety via seeded RNG (stable for same inputs).
- Includes utilities to format hashtags and hook lines (for UI cards).

This is intentionally model-free so the prototype runs anywhere.
Later you can swap the internals for:
  * RSS/Atom fetch + keyword extraction
  * Embedding clustering (e.g., sentence-transformers)
  * CLIP/BM25 re-ranking
…while keeping the same public functions & signatures.

Public API:
  - trend_topics(industry="AI/ML", seed="RAG", n=10, shuffle=True) -> list[str]
  - topic_cards(industry="AI/ML", seed="RAG", n=8) -> list[dict]
"""

from typing import Dict, List, Tuple
import random
import re
import time

__all__ = ["trend_topics", "topic_cards"]

# -----------------------------------------------------------------------------
# Static seed lists (extend freely)
# -----------------------------------------------------------------------------

_BASE_TOPICS: Dict[str, List[str]] = {
    "AI/ML": [
        "RAG",
        "LLM Ops",
        "Vector databases",
        "Latency tuning",
        "Evaluation frameworks",
        "Guardrails & safety",
        "Agent frameworks",
        "Cost optimization",
        "Multimodal models",
        "Retrieval quality",
        "Distillation & adapters",
        "Data pipelines",
        "Prompt engineering",
        "Synthetic data",
        "Observability for LLMs",
    ],
    "Product": [
        "Activation metrics",
        "Retention loops",
        "A/B testing best practices",
        "North-star metric",
        "Onboarding friction",
        "Pricing experiments",
        "PMF validation",
        "Feature flags",
        "Experiment design",
        "Attribution models",
        "Funnel diagnostics",
        "User research ops",
    ],
    "Growth": [
        "Content distribution",
        "SEO for developers",
        "Community-driven growth",
        "Referral loops",
        "Influencer collaborations",
        "Newsletter growth",
        "Lifecycle email",
        "CTR optimization",
        "Landing page experiments",
        "Cold outreach patterns",
        "Event-driven campaigns",
    ],
    "Data/Infra": [
        "Streaming pipelines",
        "Lakehouse patterns",
        "Batch vs. real-time tradeoffs",
        "Caching strategies",
        "Queue backpressure",
        "Cost/perf guardrails",
        "Schema evolution",
        "Observability",
        "Incident response",
        "Infra as code",
        "K8s autoscaling",
    ],
}

# Lite synonyms/expansions to produce variety around a seed term
_SYNONYMS: Dict[str, List[str]] = {
    "rag": ["retrieval augmented generation", "knowledge grounding", "context retrieval"],
    "agent": ["agentic workflows", "tool-use agents", "multistep planners"],
    "eval": ["evaluation frameworks", "quality benchmarks", "task-level evals"],
    "vector": ["vector databases", "ANN indexes", "dense retrieval"],
    "latency": ["latency tuning", "token throughput", "cache hits"],
    "guardrail": ["guardrails & safety", "policy checks", "toxicity filters"],
    "growth": ["growth loops", "distribution", "activation"],
    "abtest": ["A/B testing", "experimentation", "bandits"],
}


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def _seed_for(*parts: str) -> int:
    # Use time sliced into days to keep results slightly fresh when seed omitted
    day_bucket = int(time.time() // (24 * 3600))
    return hash("|".join(parts + (str(day_bucket),))) & 0xFFFFFFFF

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())

def _title(s: str) -> str:
    s = _normalize(s)
    return s[:1].upper() + s[1:] if s else s

def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for it in items:
        key = it.lower()
        if key not in seen:
            seen.add(key)
            out.append(it)
    return out

def _expand_seed(seed: str) -> List[str]:
    if not seed:
        return []
    key = re.sub(r"[^a-z]+", "", seed.lower())
    syns = _SYNONYMS.get(key, [])
    return [seed] + syns


def _hashtags(topic: str, extra: List[str] | None = None, limit: int = 6) -> List[str]:
    words = re.findall(r"[A-Za-z0-9]{3,}", topic.lower())
    tags = ["#" + w for w in dict.fromkeys(words)]
    for t in (extra or []):
        if t not in tags:
            tags.append(t)
    return tags[:limit]


def _hooks_for(topic: str) -> List[str]:
    t = _title(topic)
    return [
        f"{t}: what actually moved the metric",
        f"{t}: the 80/20 playbook",
        f"{t}: mistakes we made (and fixed)",
        f"{t}: quick wins you can ship this week",
        f"{t}: numbers before narrative",
        f"{t}: trade-offs and how we chose",
    ]


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

def trend_topics(
    industry: str = "AI/ML",
    seed: str = "RAG",
    n: int = 10,
    shuffle: bool = True,
) -> List[str]:
    """
    Return `n` trending/topic ideas for an industry, optionally biased by `seed`.

    Deterministic for the same (industry, seed, n) within a day.
    """
    industry_key = industry if industry in _BASE_TOPICS else "AI/ML"
    base = list(_BASE_TOPICS[industry_key])

    # Bias by seed (move to front, add expansions)
    expansions = _expand_seed(seed)
    for e in expansions:
        if e and e not in base:
            base.insert(0, _title(e))

    # Shuffle deterministically for variety
    rng = random.Random(_seed_for(industry_key, seed, str(n)))
    if shuffle:
        rng.shuffle(base)

    # Light long-tail composition: add "for X" or "with Y"
    tails = [
        "for startups", "for enterprise", "on a budget",
        "with small teams", "with strict SLAs", "with public datasets",
    ]
    long_tail: List[str] = []
    for t in base[: min(8, len(base))]:
        if rng.random() < 0.35:
            long_tail.append(f"{t} {rng.choice(tails)}")

    topics = _dedupe_keep_order(base + long_tail)
    return topics[: max(1, n)]


def topic_cards(
    industry: str = "AI/ML",
    seed: str = "RAG",
    n: int = 8,
) -> List[Dict[str, object]]:
    """
    Richer objects for UI cards: topic + hooks + hashtags.
    """
    topics = trend_topics(industry=industry, seed=seed, n=n, shuffle=True)
    cards: List[Dict[str, object]] = []
    for t in topics:
        cards.append(
            {
                "topic": t,
                "hooks": _hooks_for(t)[:3],
                "hashtags": _hashtags(t, extra=["#growth", "#product", "#ai"]),
            }
        )
    return cards
