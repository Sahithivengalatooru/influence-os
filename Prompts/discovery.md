# Brand Voice Discovery (Interview Script)

Ask the user and capture concise answers.

1. Who is your **primary audience**? (role, seniority, region)
2. What **outcomes** do you help them achieve? (specific)
3. Three adjectives that fit your voice (e.g., “direct”, “warm”, “technical”).
4. Things you **never** want to sound like (e.g., hypey, corporate).
5. Your **proof points** (metrics shipped, clients, case studies).
6. **Topics** you want to own (rank 1–3).
7. **Risk tolerances** (humor, emojis, strong opinions): low / medium / high.
8. **Language** preferences (primary + allowed locales).
9. CTA preferences (DMs, newsletter, calendar link).
10. 3 links to your **best posts**; what worked and why?

## Output (store as JSON)

{
"audience": "...",
"outcomes": ["..."],
"voice_adjectives": ["...", "...", "..."],
"avoid": ["..."],
"proof": ["..."],
"topics": ["t1","t2","t3"],
"risk": "low|medium|high",
"languages": ["en","hi","es"],
"cta": "preferred CTA",
"exemplars": ["url1","url2","url3"]
}
