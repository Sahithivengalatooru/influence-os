from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response

from app.config import get_settings, Settings
from app.auth import oauth as oauth_router

# Feature routers
from app.routers import (
    users,
    profile,
    trends,
    strategy,
    content,
    calendar,
    linkedin,
    analytics,
    hashtags,
    moderation,
    abtests,
    competitors,
    sentiment,
    translate,
    images,
    growth,
    export as export_router,
)


def create_app() -> FastAPI:
    """
    Root ASGI app. Hosts a minimal /health and mounts the versioned API at /v1.
    The root app disables docs; the versioned sub-app exposes docs at /v1/docs.
    """
    settings: Settings = get_settings()

    app = FastAPI(
        title="Influence OS API (Prototype)",
        version="0.1.0",
        docs_url=None,        # use versioned docs at /v1/docs
        redoc_url=None,
        openapi_url=None,
    )

    # ---------- CORS ----------
    allowed = [o.strip() for o in (settings.ALLOWED_ORIGINS or "").split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------- Root health ----------
    @app.get("/health")
    def health():
        return {"ok": True, "service": "api-gateway", "env": settings.APP_ENV}

    # ---------- Root helpers (redirect + favicon) ----------
    @app.get("/", include_in_schema=False)
    def root_redirect():
        # Send browsers straight to interactive docs
        return RedirectResponse(url="/v1/docs")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        # 1x1 transparent PNG to suppress 404 spam in logs
        import base64
        png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
        )
        return Response(content=png, media_type="image/png")

    # ---------- Versioned API (/v1) ----------
    v1 = FastAPI(
        title="Influence OS API v1",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
        openapi_url="/openapi.json",
    )

    @v1.get("/")
    def v1_root():
        return {"ok": True, "message": "v1 ready"}

    # Auth (LinkedIn OAuth PKCE stub + dev token)
    v1.include_router(oauth_router.router)

    # Feature routers (per brief)
    v1.include_router(users.router)
    v1.include_router(profile.router)
    v1.include_router(trends.router)
    v1.include_router(strategy.router)
    v1.include_router(content.router)
    v1.include_router(calendar.router)
    v1.include_router(linkedin.router)
    v1.include_router(analytics.router)
    v1.include_router(hashtags.router)
    v1.include_router(moderation.router)
    v1.include_router(abtests.router)
    v1.include_router(competitors.router)
    v1.include_router(sentiment.router)
    v1.include_router(translate.router)
    v1.include_router(images.router)
    v1.include_router(growth.router)
    v1.include_router(export_router.router)

    # Mount under /v1
    app.mount("/v1", v1)

    return app


# Uvicorn entrypoint
app = create_app()
