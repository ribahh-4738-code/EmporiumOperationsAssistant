"""Environment-based configuration (stub for future application modules)."""

from __future__ import annotations

import os


def postgres_connection_kwargs() -> dict[str, str | int]:
    """Build psycopg connection kwargs from POSTGRES_* environment variables."""
    return {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": int(os.environ.get("POSTGRES_PORT", "5435")),
        "user": os.environ.get("POSTGRES_USER", "postgres"),
        "password": os.environ.get("POSTGRES_PASSWORD", "emporium_dev"),
        "dbname": os.environ.get("POSTGRES_DB", "emporium_operation"),
    }
