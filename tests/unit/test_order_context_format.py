"""Tests for order context string building (SQL mocked)."""

from __future__ import annotations

import pytest

from emporium_operations_assistant.assistant.order_context import build_order_context
from emporium_operations_assistant.config import Settings


def test_build_order_context_by_order_id(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_detail(order_id: int, settings=None, **kwargs: object) -> dict[str, object]:
        assert order_id == 8
        return {
            "header": {
                "order_id": 8,
                "customer_name": "Test User",
                "customer_email": "t@example.com",
                "order_date": "2026-02-15",
                "status": "shipped",
                "total_brl": 349.9,
                "payment_method": "debit",
                "tracking_code": "BRJL5544332BR",
                "estimated_delivery": None,
                "notes": None,
            },
            "items": [
                {"quantity": 1, "product_id": 96, "product_name": "Product X"},
            ],
        }

    monkeypatch.setattr(
        "emporium_operations_assistant.assistant.order_context.get_order_detail",
        fake_detail,
    )
    ctx = build_order_context(settings, user_query="pedido 8", session_customer_id=None)
    assert "Pedido #8" in ctx
    assert "shipped" in ctx
    assert "BRJL5544332BR" in ctx
    assert "Product X" in ctx


def test_build_order_context_not_found(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "emporium_operations_assistant.assistant.order_context.get_order_detail",
        lambda *a, **k: None,
    )
    ctx = build_order_context(settings, user_query="pedido 999", session_customer_id=None)
    assert "não encontrado" in ctx
