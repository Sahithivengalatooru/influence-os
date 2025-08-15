# Text Post (LinkedIn)

## Goal

Write a scannable LinkedIn **text post** that teaches 1–3 concrete ideas and invites a lightweight CTA.

## Inputs

- topic: {{topic}}
- audience: {{audience|default:"AI/product builders"}}
- brand_voice: {{brand_voice|default:"confident, friendly, concise"}}
- language: {{language|default:"en"}}
- length: {{length|default:"120–180 words"}}
- cta: {{cta|default:"Save this for later or DM me ‘RAG’"}}

## Style constraints

- Headline first line ≤ 80 chars. Use sentence case, no clickbait.
- Short paragraphs (1–3 lines), skimmable bullets, **bold** sparingly.
- Avoid hype and vague claims; include 1 concrete example or number.
- No emojis unless {{allow_emojis|default:"false"}} is true (then ≤ 2 tasteful).
- Write in {{language}}; if non-English, localize idioms.

## Structure

1. Hook (1 line)
2. Context + 2–3 takeaways (bulleted)
3. Mini-CTA (1 line)

## Output format (strict)

Return **plain text** only (no JSON, no markdown headings). Start with the hook line.
