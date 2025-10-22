from __future__ import annotations

from typing import List, Literal
import random
import re

PostType = Literal["text", "article", "carousel", "poll"]


# --- tiny helpers -------------------------------------------------------------

def _seed_for(*parts: str) -> int:
    """Deterministic-ish seed so same inputs produce same variants."""
    return hash("|".join(parts)) & 0xFFFFFFFF

def _sent_case(s: str) -> str:
    s = s.strip()
    return s[:1].upper() + s[1:] if s else s

def _hashtagify(topic: str, extra: List[str]) -> List[str]:
    # naive hashtagging: keep alnum words > 2 chars
    words = re.findall(r"[A-Za-z0-9]{3,}", topic.lower())
    tags = ["#" + w for w in dict.fromkeys(words)]  # unique, in order
    for t in extra:
        if t not in tags:
            tags.append(t)
    return tags[:6]

def _voice_note(brand_voice: str) -> str:
    # Pull 1–2 adjectives as a subtle tone note
    bits = [b.strip() for b in re.split(r"[;,/]| and ", brand_voice) if b.strip()]
    if not bits:
        return ""
    bits = bits[:2]
    return f" (tone: {', '.join(bits)})"


# --- main generator -----------------------------------------------------------

def draft_post(
    *,
    topic: str,
    brand_voice: str = "confident, friendly, concise",
    post_type: PostType = "text",
    n_variants: int = 2,
    language: str = "en",
) -> List[str]:
    """
    Produce n_variants demo drafts for the given topic & post_type.

    Still model-free (prototype). Later you can swap the body of each case
    with an OSS LLM call while keeping this function's signature.
    """
    n = max(1, min(6, n_variants))
    rng = random.Random(_seed_for(topic, brand_voice, post_type, language))

    # Shared building blocks
    hooks = [
        "3 takeaways you can use this week",
        "What worked for us (and what didn't)",
        "Playbook: from idea → shipped",
        "Mistakes to avoid + a safer path",
        "The 80/20 that actually moves metrics",
        "From zero to first win",
    ]
    ctas = [
        "Curious how you're tackling this—drop a comment.",
        "If this helps, share it with a teammate.",
        "Want the full write-up? Say 'send' below.",
        "Bookmark for your next sprint planning.",
        "Try one step today and report back.",
    ]
    frames = [
        "Context → Problem → Approach → Results → Next",
        "Goal → Constraints → Options → Decision → Lessons",
        "Symptom → Root cause → Experiment → Outcome → Repeat",
    ]
    bullets_bank = [
        "ship small wins fast",
        "optimize for clarity over cleverness",
        "measure the thing users actually feel",
        "cut scope until it fits in a week",
        "default to boring infrastructure",
        "write the success criteria before building",
        "treat latency budgets as product features",
        "document how to rollback safely",
    ]

    out: List[str] = []

    for i in range(n):
        # vary picks per variant
        hook = rng.choice(hooks)
        frame = rng.choice(frames)
        cta = rng.choice(ctas)
        bullets = rng.sample(bullets_bank, k=min(4, len(bullets_bank)))

        voice = _voice_note(brand_voice)
        tags = _hashtagify(topic, extra=["#product", "#ai", "#growth"])

        if post_type == "text":
            body = (
                f"{_sent_case(topic)} — {hook}{voice}\n"
                f"• {bullets[0].capitalize()}\n"
                f"• {bullets[1].capitalize()}\n"
                f"• {bullets[2].capitalize()}\n\n"
                f"{cta}\n"
                f"{' '.join(tags)}"
            )

        elif post_type == "article":
            title = f"{_sent_case(topic)}: a practical guide{voice}"
            intro = (
                "Why it matters: users don't care about our roadmap—"
                "they care about outcomes. Here’s a concrete way to get there."
            )
            section_a = (
                f"1) Context\n"
                f"- What we were trying to achieve\n"
                f"- Constraints we accepted\n"
                f"- Signals we watched"
            )
            section_b = (
                f"2) Approach\n"
                f"- {_sent_case(bullets[0])}\n"
                f"- {_sent_case(bullets[1])}\n"
                f"- {_sent_case(bullets[2])}"
            )
            section_c = (
                f"3) Results\n"
                f"- Lead metric moved (+{rng.randint(5,18)}%)\n"
                f"- Trade-offs we accepted\n"
                f"- What we’d change next time"
            )
            outro = f"Framework used: {frame}. {cta}\n{' '.join(tags)}"
            body = f"{title}\n\n{intro}\n\n{section_a}\n\n{section_b}\n\n{section_c}\n\n{outro}"

        elif post_type == "carousel":
            # 5 slides outline
            s1 = f"Slide 1 — Hook\n{_sent_case(topic)}: {hook}{voice}"
            s2 = f"Slide 2 — Problem\n• {_sent_case(bullets[0])}\n• {_sent_case(bullets[1])}"
            s3 = f"Slide 3 — Approach\n• {_sent_case(bullets[2])}\n• {_sent_case(bullets[3])}"
            s4 = f"Slide 4 — Results\n• Metric improved\n• Simpler ops\n• Happier users"
            s5 = f"Slide 5 — CTA\n{cta}\n{ ' '.join(tags) }"
            body = "\n\n".join([s1, s2, s3, s4, s5])

        else:  # poll
            q_variants = [
                f"Biggest blocker for {_sent_case(topic)}?",
                f"How are you approaching {_sent_case(topic)} today?",
                f"What outcome matters most for {_sent_case(topic)}?",
            ]
            options_sets = [
                ["Cost", "Latency", "Accuracy", "Security"],
                ["We do it", "Considering", "Pilot soon", "Not a fit"],
                ["Activation", "Retention", "Revenue", "Delight"],
            ]
            q = rng.choice(q_variants) + voice
            opts = rng.choice(options_sets)
            body = f"Poll: {q}\nOptions: " + " | ".join(opts) + f"\n\n{cta}"

        out.append(body + f"\n\n(v{i+1})")

    return out
