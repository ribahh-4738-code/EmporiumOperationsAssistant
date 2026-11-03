"""Tests for catalog keyword extraction and price filter parsing."""

from __future__ import annotations

from decimal import Decimal

from emporium_operations_assistant.assistant.catalog_search import (
    extract_keywords,
    extract_max_price_brl,
    _query_without_price_phrases,
)


def test_extract_keywords_skips_stopwords() -> None:
    kws = extract_keywords("Você pode me dizer violão Yamaha preço?")
    assert "violão" in kws
    assert "yamaha" in kws
    assert "você" not in kws
    assert "pode" not in kws


def test_extract_keywords_accent_and_min_length() -> None:
    kws = extract_keywords("oi")
    assert kws == []


def test_extract_max_price_brl() -> None:
    assert extract_max_price_brl("violões até R$ 1000") == Decimal("1000")
    assert extract_max_price_brl("ate 849,90 reais") == Decimal("849.90")
    assert extract_max_price_brl("sem preço") is None


def test_keywords_after_stripping_price() -> None:
    q = _query_without_price_phrases("Quais opções de violões até R$1000?")
    kws = extract_keywords(q)
    assert "violões" in kws or "viol" in " ".join(kws)
