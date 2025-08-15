# Poll

## Goal

Write a neutral, decision-helping LinkedIn poll with balanced options.

## Inputs

- question_theme: {{question_theme}}
- audience: {{audience|default:"builders & leads"}}
- brand_voice: {{brand_voice|default:"curious, constructive"}}
- language: {{language|default:"en"}}
- options: {{options|default:3}} # 3–4 recommended

## Constraints

- Avoid leading phrasing; keep options mutually exclusive and collectively exhaustive.
- Include 1 “it depends” style option only if it’s specific.
- Add 1-line context above the poll to frame decision.
- Language must be {{language}}.

## Output format (strict)

Return **plain text** in this layout:
Context: <one line>
Question: <poll question?>
A) <option>
B) <option>
C) <option>
[D) <option>]
CTA: <how you’ll use responses in a follow-up>
