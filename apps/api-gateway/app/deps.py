from typing import AsyncGenerator

import httpx

# Re-export settings so other modules can `from app.deps import get_settings, Settings`
from .config import Settings, get_settings


async def get_http() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Shared Async HTTP client (use as a FastAPI dependency)."""
    async with httpx.AsyncClient(timeout=30) as client:
        yield client
