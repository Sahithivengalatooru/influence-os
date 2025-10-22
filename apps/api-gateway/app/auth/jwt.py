from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import Settings, get_settings

security = HTTPBearer(auto_error=True)


class JWTPayload(BaseModel):
    sub: str                     # subject (e.g., user email or id)
    iat: int                     # issued-at (unix seconds)
    exp: int                     # expiration (unix seconds)
    role: str = "user"           # convenience role field


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_jwt(
    *,
    sub: str,
    settings: Settings,
    role: str = "user",
    ttl_minutes: int = 60,
) -> str:
    """Create a signed JWT."""
    now = _now_utc()
    payload = JWTPayload(
        sub=sub,
        iat=int(now.timestamp()),
        exp=int((now + timedelta(minutes=ttl_minutes)).timestamp()),
        role=role,
    ).model_dump()
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def decode_jwt(token: str, settings: Settings) -> JWTPayload:
    """Decode & validate a JWT, returning the typed payload or raising 401."""
    try:
        data = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        return JWTPayload(**data)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


async def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(security),
    settings: Settings = Depends(get_settings),
) -> JWTPayload:
    """FastAPI dependency: returns the authenticated user's payload."""
    return decode_jwt(cred.credentials, settings)


def require_roles(*allowed: str) -> Callable[[JWTPayload], JWTPayload]:
    """
    Usage:
        @app.get("/admin")
        def admin_only(user: JWTPayload = Depends(require_roles("admin"))):
            ...
    """
    allowed_set = set(allowed)

    def _dep(
        user: JWTPayload = Depends(get_current_user),
    ) -> JWTPayload:
        if allowed_set and user.role not in allowed_set:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return _dep
