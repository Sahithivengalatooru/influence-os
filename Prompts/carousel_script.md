# Carousel Script

## Goal

Create a 6–8 slide LinkedIn carousel script with crisp, visual-first captions.

## Inputs

- topic: {{topic}}
- audience: {{audience|default:"operators"}}
- brand_voice: {{brand_voice|default:"teaches by example"}}
- language: {{language|default:"en"}}
- slides: {{slides|default:7}}

## Slide template

- S1 (Cover): claim or “before → after” in ≤ 9 words
- S2 (Context): the costly problem (≤ 2 lines)
- S3–S5 (How): steps or framework (1 headline + 1 line each)
- S6 (Example): a tiny numeric example
- S7 (CTA): save/share/DM prompt; optional bonus link/keyword

## Constraints

- Each slide: ≤ 14 words; no hashtags; no emojis unless allowed.
- Language must be {{language}}; keep numbers and code in monospaced style out (no backticks).

## Output format (strict)

Return **markdown** as a list:

- Slide 1: ...
- Slide 2: ...
  ...
  Only the bullet list, nothing else.
