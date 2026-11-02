"""Normalize chat history for provider APIs (Gemini turn rules)."""

from __future__ import annotations

from emporium_operations_assistant.llm.roles import ROLE_USER
from emporium_operations_assistant.llm.types import ChatTurn


def normalize_turns_for_llm(turns: list[ChatTurn]) -> list[ChatTurn]:
    """
    Gemini requires alternating user/model turns, starting with user, ending with user.
    """
    if not turns:
        return turns

    working = list(turns)
    while working and working[0].role != ROLE_USER:
        working.pop(0)
    if not working:
        return working

    merged: list[ChatTurn] = []
    for turn in working:
        if merged and merged[-1].role == turn.role:
            prev = merged[-1]
            merged[-1] = ChatTurn(
                role=turn.role,
                content=f"{prev.content}\n{turn.content}".strip(),
            )
        else:
            merged.append(turn)

    while merged and merged[-1].role != ROLE_USER:
        merged.pop()

    return merged
