"""LLM provider protocol."""

from __future__ import annotations

from typing import Protocol

from emporium_operations_assistant.llm.types import ChatTurn, CompletionResult


class LLMProvider(Protocol):
    """Multi-adapter interface for cloud and local models."""

    def complete(self, messages: list[ChatTurn], *, system_instruction: str | None = None) -> CompletionResult:
        """Generate an assistant reply from chat turns."""
