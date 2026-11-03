"""Log and runtime state paths under .run/."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from emporium_operations_assistant.config import project_root


def run_dir() -> Path:
    path = project_root() / ".run"
    path.mkdir(parents=True, exist_ok=True)
    return path


def assistant_log_path() -> Path:
    raw = os.environ.get("ASSISTANT_LOG_PATH", "")
    if raw:
        path = Path(raw)
        if not path.is_absolute():
            path = project_root() / path
    else:
        path = run_dir() / "assistant.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def daily_token_state_path(day: date | None = None) -> Path:
    d = day or date.today()
    return run_dir() / f"gemini_tokens_{d.isoformat()}.json"
