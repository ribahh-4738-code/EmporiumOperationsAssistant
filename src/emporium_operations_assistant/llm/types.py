"""Shared types for LLM adapters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatTurn:
    role: str
    content: str


@dataclass(frozen=True)
class CompletionResult:
    text: str
    model: str
