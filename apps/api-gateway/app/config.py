from __future__ import annotations

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # CORS / environment
    APP_ENV: str = "local"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # JWT
    JWT_SECRET: str = "change_me"
    JWT_ALG: str = "HS256"

    # Optional model servers (not required for prototype)
    VLLM_BASE_URL: str = "http://localhost:8001/v1"
    VLLM_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"

    # OAuth placeholders (optional for prototype)
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_REDIRECT_URI: str = "http://localhost:8000/v1/auth/callback"
    LINKEDIN_SCOPES: str = "r_liteprofile r_emailaddress w_member_social"

    class Config:
        # Read a .env file from the repo root by default
        env_file = os.environ.get("ENV_FILE", os.path.join(os.path.dirname(__file__), "../../..", ".env"))
        extra = "allow"


# simple singleton access
_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
