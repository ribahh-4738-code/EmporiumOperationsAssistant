"""Chat message roles aligned with Gemini API (user / model)."""

from __future__ import annotations

ROLE_USER = "user"
ROLE_MODEL = "model"
# Legacy rows persisted before v0.4.x
LEGACY_ROLE_MODEL = "assistant"


def to_llm_role(stored_role: str) -> str:
    """Map database role to LLM turn role."""
    if stored_role == ROLE_USER:
        return ROLE_USER
    return ROLE_MODEL


def to_storage_role(llm_role: str) -> str:
    """Role written to assistant_chat_message."""
    if llm_role == ROLE_USER:
        return ROLE_USER
    return ROLE_MODEL
