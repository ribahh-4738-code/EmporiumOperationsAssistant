"""Tests for order id and email extraction from user messages."""

from __future__ import annotations

from emporium_operations_assistant.assistant.order_lookup import extract_email, extract_order_id


def test_extract_order_id_pedido() -> None:
    assert extract_order_id("Quero saber do pedido 8") == 8
    assert extract_order_id("pedido #12") == 12
    assert extract_order_id("número do pedido 3") == 3


def test_extract_order_id_no_bare_number() -> None:
    assert extract_order_id("O total foi 4599 reais") is None
    assert extract_order_id("violão Yamaha") is None


def test_extract_email_status_question() -> None:
    text = (
        "Gostaria de saber o status do meu pedido, "
        "meu e-mail é rafael.pereira@jmail.com"
    )
    assert extract_email(text) == "rafael.pereira@jmail.com"
