"""Tests for Gemini turn normalization."""

from __future__ import annotations

from emporium_operations_assistant.llm.history import normalize_turns_for_llm
from emporium_operations_assistant.llm.roles import ROLE_MODEL, ROLE_USER
from emporium_operations_assistant.llm.types import ChatTurn


def test_normalize_drops_leading_non_user() -> None:
    turns = [
        ChatTurn(role=ROLE_MODEL, content="Olá"),
        ChatTurn(role=ROLE_USER, content="Oi"),
    ]
    out = normalize_turns_for_llm(turns)
    assert len(out) == 1
    assert out[0].role == ROLE_USER


def test_normalize_merges_same_role() -> None:
    turns = [
        ChatTurn(role=ROLE_USER, content="A"),
        ChatTurn(role=ROLE_USER, content="B"),
    ]
    out = normalize_turns_for_llm(turns)
    assert len(out) == 1
    assert "A" in out[0].content and "B" in out[0].content


def test_normalize_drops_trailing_model() -> None:
    turns = [
        ChatTurn(role=ROLE_USER, content="Pergunta"),
        ChatTurn(role=ROLE_MODEL, content="Resposta"),
    ]
    out = normalize_turns_for_llm(turns)
    assert len(out) == 1
    assert out[0].role == ROLE_USER
