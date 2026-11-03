"""Tests for RAG text chunking."""

from __future__ import annotations

import pytest

from emporium_operations_assistant.rag.chunking import chunk_text


def test_chunk_text_empty() -> None:
    assert chunk_text("", size=100, overlap=10) == []
    assert chunk_text("   \n\t  ", size=100, overlap=10) == []


def test_chunk_text_short_fits_one_chunk() -> None:
    text = "Política de parcelamento em até 12x."
    chunks = chunk_text(text, size=200, overlap=20)
    assert len(chunks) == 1
    assert "parcelamento" in chunks[0]


def test_chunk_text_overlap_produces_multiple() -> None:
    text = "a" * 250
    chunks = chunk_text(text, size=100, overlap=20)
    assert len(chunks) >= 2
    assert all(len(c) <= 100 for c in chunks)


def test_chunk_text_invalid_size() -> None:
    with pytest.raises(ValueError, match="size must be positive"):
        chunk_text("hello", size=0, overlap=0)
