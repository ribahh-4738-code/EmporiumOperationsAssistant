"""Optional smoke tests against local PostgreSQL seed data."""

from __future__ import annotations

import pytest
import psycopg

from emporium_operations_assistant.assistant.order_queries import get_order_detail
from emporium_operations_assistant.config import load_settings, postgres_connection_kwargs

pytestmark = pytest.mark.integration


def _postgres_available() -> bool:
    settings = load_settings(load_env_file=True)
    try:
        with psycopg.connect(**postgres_connection_kwargs(settings), connect_timeout=2):
            return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def require_postgres() -> None:
    if not _postgres_available():
        pytest.skip("PostgreSQL not available (start ./install.sh or Docker stack)")


def test_get_order_detail_seed_order_8(require_postgres: None) -> None:
    settings = load_settings(load_env_file=True)
    detail = get_order_detail(8, settings)
    assert detail is not None
    header = detail["header"]
    assert isinstance(header, dict)
    assert header.get("order_id") == 8
    assert header.get("status") == "shipped"
    assert header.get("tracking_code") == "BRJL5544332BR"
