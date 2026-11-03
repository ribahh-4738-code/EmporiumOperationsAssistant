"""Shared types for LLM adapters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatTurn:
    """One turn in the conversation. Use roles ``user`` or ``model`` (Gemini)."""

    role: str  # user | model
    content: str


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(frozen=True)
class CompletionResult:
    text: str
    model: str
    usage: TokenUsage | None = None
