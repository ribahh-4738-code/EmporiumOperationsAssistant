"""Environment-based configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    assistant_display_name: str
    assistant_profile_name: str
    llm_provider: str
    gemini_api_key: str
    gemini_model: str
    llm_temperature: float


def load_settings() -> Settings:
    """Load settings from environment variables (see .env.example)."""
    return Settings(
        postgres_host=os.environ.get("POSTGRES_HOST", "localhost"),
        postgres_port=int(os.environ.get("POSTGRES_PORT", "5435")),
        postgres_user=os.environ.get("POSTGRES_USER", "postgres"),
        postgres_password=os.environ.get("POSTGRES_PASSWORD", "emporium_dev"),
        postgres_db=os.environ.get("POSTGRES_DB", "emporium_operation"),
        assistant_display_name=os.environ.get("ASSISTANT_DISPLAY_NAME", "Maiara"),
        assistant_profile_name=os.environ.get("ASSISTANT_PROFILE_NAME", "maiara"),
        llm_provider=os.environ.get("LLM_PROVIDER", "gemini").lower(),
        gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        gemini_model=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
        llm_temperature=float(os.environ.get("LLM_TEMPERATURE", "0.7")),
    )


def postgres_connection_kwargs(settings: Settings | None = None) -> dict[str, str | int]:
    """Build psycopg connection kwargs."""
    s = settings or load_settings()
    return {
        "host": s.postgres_host,
        "port": s.postgres_port,
        "user": s.postgres_user,
        "password": s.postgres_password,
        "dbname": s.postgres_db,
    }
