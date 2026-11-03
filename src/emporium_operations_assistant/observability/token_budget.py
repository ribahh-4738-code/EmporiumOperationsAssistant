"""Daily Gemini token counter (warn in log only when budget exceeded)."""

from __future__ import annotations

import json
from typing import Any

from emporium_operations_assistant.config import Settings, load_settings
from emporium_operations_assistant.observability.events import emit_event
from emporium_operations_assistant.observability.paths import daily_token_state_path


def _load_state() -> dict[str, Any]:
    path = daily_token_state_path()
    if not path.is_file():
        return {"total": 0, "turns": 0}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_state(state: dict[str, Any]) -> None:
    path = daily_token_state_path()
    path.write_text(json.dumps(state), encoding="utf-8")


def record_gemini_usage(
    *,
    source: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int | None = None,
    model: str | None = None,
    settings: Settings | None = None,
) -> int:
    """
    Add tokens to daily total, emit gemini event, warn in log if over budget.
    Returns updated daily total.
    """
    settings = settings or load_settings()
    turn_total = total_tokens if total_tokens is not None else prompt_tokens + completion_tokens
    state = _load_state()
    state["total"] = int(state.get("total", 0)) + turn_total
    state["turns"] = int(state.get("turns", 0)) + 1
    _save_state(state)
    daily_total = int(state["total"])

    level = "info"
    budget = settings.gemini_daily_token_budget
    if budget > 0 and daily_total >= budget:
        level = "warn"

    emit_event(
        "gemini",
        level=level,
        source=source,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        turn_tokens=turn_total,
        daily_total=daily_total,
        daily_budget=budget if budget > 0 else None,
    )
    if level == "warn":
        emit_event(
            "gemini_budget",
            level="warn",
            message="Daily Gemini token budget reached (chat continues; warn only)",
            daily_total=daily_total,
            daily_budget=budget,
        )
    return daily_total
