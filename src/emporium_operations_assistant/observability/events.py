"""Append-only JSONL event log."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from emporium_operations_assistant.observability.paths import assistant_log_path


def emit_event(event_type: str, **fields: Any) -> None:
    """Write one JSON line (safe for multi-process append on local FS)."""
    record: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        **fields,
    }
    line = json.dumps(record, ensure_ascii=False) + "\n"
    path = assistant_log_path()
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)
