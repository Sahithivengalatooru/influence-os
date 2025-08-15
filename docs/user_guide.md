# User Guide

## 1) Sign up / Login

- Open the app at `http://localhost:3000`.
- For prototype testing:
  1. Call `POST /v1/auth/dev-token` (via the **Dev Tools** section below or `seed_demo_content.py`) to get a JWT.
  2. Paste the token into your browser’s localStorage under key `io_jwt` (the UI uses it automatically).

Or use:

- **/users/signup** → creates a user and returns a JWT.
- **/users/login** → returns a JWT for future requests.

## 2) Key Screens

- **Dashboard**: calendar preview + analytics.
- **Compose**: generate multi-format posts (text, article, carousel, poll).
- **Calendar**: create/update/delete items.
- **Trends**: surface topics via the research agent.
- **Profile**: analyze a headline & about section; get themes + suggestions.
- **Strategy**: auto-generate content pillars, cadence, KPIs.
- **A/B Tests**: create/run/stop an experiment and assign users to arms.
- **Competitors**: sample insights table.
- **Images**: prompt → inline SVG preview (swap with real model later).
- **Growth**: quick-wins checklist.

## 3) API Endpoints (highlights)

- Auth: `GET /v1/auth/login`, `GET /v1/auth/callback`, `POST /v1/auth/dev-token`
- Users: `POST /v1/users/signup`, `POST /v1/users/login`, `GET /v1/users/me`
- Content: `POST /v1/content/generate`
- Calendar: `GET/POST/PUT/DELETE /v1/calendar`
- Analytics: `GET /v1/analytics/summary`, `GET /v1/analytics/kpi`
- Trends: `GET /v1/trends?industry=AI/ML&seed=RAG`
- Images: `POST /v1/images/generate`
- Moderation: `POST /v1/moderation/check`
- Sentiment: `POST /v1/sentiment/analyze`
- Translate: `POST /v1/translate`

## 4) Dev Tools

- Run `scripts/proto-run.sh` to start API and Web.
- Run `scripts/seed_demo_content.py` to mint a JWT and seed calendar items.
