"""Tests for catalog keyword extraction."""

from __future__ import annotations

from emporium_operations_assistant.assistant.catalog_search import extract_keywords


def test_extract_keywords_skips_stopwords() -> None:
    kws = extract_keywords("Você pode me dizer violão Yamaha preço?")
    assert "violão" in kws
    assert "yamaha" in kws
    assert "você" not in kws
    assert "pode" not in kws


def test_extract_keywords_accent_and_min_length() -> None:
    kws = extract_keywords("oi")
    assert kws == []
