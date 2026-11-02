"""Environment-based configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_dotenv_file(env_path: Path | None = None) -> None:
    """Load KEY=VALUE pairs from .env into os.environ (does not override existing)."""
    path = env_path or (project_root() / ".env")
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip().strip("\ufeff")
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not os.environ.get(key):
            os.environ[key] = value


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
    chat_history_limit: int
    chat_channel: str


def load_settings(*, load_env_file: bool = True) -> Settings:
    """Load settings from environment variables (see .env.example)."""
    if load_env_file:
        load_dotenv_file()
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
        gemini_model=os.environ.get("GEMINI_MODEL", "gemini-3.6-flash"),
        llm_temperature=float(os.environ.get("LLM_TEMPERATURE", "0.7")),
        chat_history_limit=int(os.environ.get("CHAT_HISTORY_LIMIT", "20")),
        chat_channel=os.environ.get("CHAT_CHANNEL", "cli"),
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
