# Longform Article (LinkedIn)

## Goal

Draft an actionable LinkedIn article that readers can apply today.

## Inputs

- topic: {{topic}}
- audience: {{audience|default:"practitioners & PMs"}}
- brand_voice: {{brand_voice|default:"credible, direct, generous"}}
- language: {{language|default:"en"}}
- target_words: {{target_words|default:"700–900"}}

## Must include

- Clear thesis in intro (≤ 3 sentences).
- Sectioned body with H2 headings (##) and short paragraphs.
- 1 mini case-study or numeric example.
- A 5-step checklist or framework.
- Closing “Next steps” with 3 bulleted actions.

## Constraints

- Avoid fluff, clichés, and needless adjectives.
- No unverified claims or private data.
- If uncertain, prefer “how to decide” over prescriptive rules.

## Output format (strict)

Return **markdown** beginning with the title line:
`# {{proposed_title}}`
Then sections with `##` headings. Do not include frontmatter or JSON.
