# Influence OS – Prototype (API only)

This is the **FastAPI** backend skeleton for the prototype. It exposes:

- `GET /health` – service health
- A versioned mount at `/v1/*` (ready to attach feature routers)

## Quick start

1. Create a virtual environment and install deps:

```bash
cd apps/api-gateway
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
```
