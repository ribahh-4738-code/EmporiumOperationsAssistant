"""Placeholder for future local models (e.g. Gemma)."""

from __future__ import annotations

from emporium_operations_assistant.llm.types import ChatTurn, CompletionResult


class LocalGemmaAdapter:
    """Not implemented — reserved for on-prem inference."""

    def complete(
        self,
        messages: list[ChatTurn],
        *,
        system_instruction: str | None = None,
    ) -> CompletionResult:
        raise NotImplementedError(
            "Local Gemma adapter is not implemented yet. Use LLM_PROVIDER=gemini."
        )
