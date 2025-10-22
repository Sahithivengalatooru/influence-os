#!/usr/bin/env python3
"""
Seed the prototype with a dev JWT and some demo data.

Usage:
  python scripts/seed_demo_content.py
Env:
  BASE (default http://localhost:8000/v1)
"""
import os, json, time
import requests

BASE = os.environ.get("BASE", "http://localhost:8000/v1")

def post(path, json_body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.post(f"{BASE}{path}", headers=headers, json=json_body or {})
    try:
        r.raise_for_status()
    except Exception:
        print(f"POST {path} failed:", r.status_code, r.text)
        raise
    return r.json()

def get(path, token=None, params=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(f"{BASE}{path}", headers=headers, params=params or {})
    try:
        r.raise_for_status()
    except Exception:
        print(f"GET {path} failed:", r.status_code, r.text)
        raise
    return r.json()

def main():
    print(f"==> Seeding against {BASE}")

    # 1) Mint a local dev token (requires APP_ENV=local on API)
    token = post("/auth/dev-token", {"email": "demo@example.com", "role": "user", "ttl_minutes": 240})["access_token"]
    print("   minted JWT (truncated):", token[:24], "...")

    # 2) Calendar items
    today = time.strftime("%Y-%m-%d")
    items = [
        {"date": today, "title": "Thought leadership post"},
        {"date": today, "title": "Carousel: AI trends"},
    ]
    for it in items:
        post("/calendar", it, token=token)
    cal = get("/calendar", token=token)
    print(f"   calendar items: {len(cal)}")

    # 3) Generate content variants
    variants = post("/content/generate", {
        "type": "text",
        "topic": "Agentic RAG for enterprise search",
        "brand_voice": "confident, friendly, concise",
        "n_variants": 2
    }, token=token)["variants"]
    print("   generated variants:", len(variants))

    # 4) Hashtags
    tags = post("/hashtags/suggest", {"topic": "Agentic RAG for enterprise search"}, token=token)["hashtags"]
    print("   hashtags:", ", ".join(tags[:5]), "...")

    # 5) Image stub
    img = post("/images/generate", {"prompt": "Minimal gradient cover", "style": "minimal"}, token=token)["image_data_uri"]
    print("   image data-uri length:", len(img))

    # 6) Analytics
    summary = get("/analytics/summary", token=token)
    print("   analytics series:", list(summary.get("series", {}).keys()))

    print("==> Done.")
    print("\nTip: Copy this JWT into localStorage under key 'io_jwt' to browse the UI authenticated.")
    print("     localStorage.setItem('io_jwt', '<token>')")

if __name__ == "__main__":
    main()
