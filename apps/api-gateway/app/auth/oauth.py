from __future__ import annotations

import base64
import hashlib
import os
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.auth.jwt import create_jwt

router = APIRouter(prefix="/auth", tags=["auth"])


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def create_pkce_pair() -> tuple[str, str]:
    """
    Returns (code_verifier, code_challenge).
    The client must keep the verifier and send it back on /callback.
    """
    verifier = _b64url(os.urandom(40))
    challenge = _b64url(hashlib.sha256(verifier.encode()).digest())
    return verifier, challenge


# ======== Schemas ========

class OAuthInitResponse(BaseModel):
    authorization_url: str
    code_verifier: str
    state: str


class TokenResponse(BaseModel):
    access_token: str
    expires_in: int


# ======== Endpoints ========

@router.get("/login", response_model=OAuthInitResponse)
async def login(settings: Settings = Depends(get_settings)):
    """
    Returns a LinkedIn authorization URL (PKCE S256), along with a code_verifier
    that the client must keep and send to /auth/callback.

    This is a prototype stub: it does not persist state server-side.
    """
    code_verifier, code_challenge = create_pkce_pair()
    state = _b64url(os.urandom(12))  # optional CSRF token

    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&client_id={settings.LINKEDIN_CLIENT_ID}"
        f"&redirect_uri={settings.LINKEDIN_REDIRECT_URI}"
        f"&scope={settings.LINKEDIN_SCOPES.replace(' ', '%20')}"
        f"&code_challenge={code_challenge}&code_challenge_method=S256"
        f"&state={state}"
    )
    return OAuthInitResponse(
        authorization_url=auth_url,
        code_verifier=code_verifier,
        state=state,
    )


@router.get("/callback", response_model=TokenResponse)
async def callback(
    code: str = Query(..., description="Authorization code from LinkedIn"),
    code_verifier: str = Query(..., description="The PKCE code_verifier returned by /auth/login"),
    settings: Settings = Depends(get_settings),
    http: httpx.AsyncClient = Depends(lambda: httpx.AsyncClient(timeout=30)),
):
    """
    Prototype stub: returns a fake token for development.
    In production you'd call LinkedIn's token endpoint:

      POST https://www.linkedin.com/oauth/v2/accessToken
      Content-Type: application/x-www-form-urlencoded
      grant_type=authorization_code
      code=<code>
      redirect_uri=<settings.LINKEDIN_REDIRECT_URI>
      client_id=<settings.LINKEDIN_CLIENT_ID>
      client_secret=<settings.LINKEDIN_CLIENT_SECRET>
      code_verifier=<code_verifier>

    and return the real access_token/expires_in from LinkedIn.
    """
    # Safety check (we don't verify state in this stub)
    if not code or not code_verifier:
        raise HTTPException(status_code=400, detail="Missing code or code_verifier")

    # Stubbed success
    return TokenResponse(access_token="FAKE_LINKEDIN_TOKEN_FOR_DEV_ONLY", expires_in=3600)


# ======== Local Dev Helper (optional) ========

class DevTokenReq(BaseModel):
    email: str
    role: Optional[str] = "user"
    ttl_minutes: int = 120


class DevTokenRes(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/dev-token", response_model=DevTokenRes)
def dev_token(
    req: DevTokenReq,
    settings: Settings = Depends(get_settings),
):
    """
    Local-only shortcut to mint a first-party JWT without OAuth.
    Useful for testing authenticated routes in the prototype.

    You may want to guard this behind APP_ENV == 'local' in production code.
    """
    if settings.APP_ENV != "local":
        raise HTTPException(status_code=403, detail="dev-token only allowed in local env")
    token = create_jwt(sub=req.email, role=req.role or "user", ttl_minutes=req.ttl_minutes, settings=settings)
    return DevTokenRes(access_token=token)
