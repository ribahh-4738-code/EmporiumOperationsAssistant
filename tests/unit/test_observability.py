"""Tests for JSONL events and token budget state."""

from __future__ import annotations

import json

from emporium_operations_assistant.observability.events import emit_event
from emporium_operations_assistant.observability.token_budget import record_gemini_usage


def test_emit_event_appends_jsonl(tmp_run_dir) -> None:
    log_path = tmp_run_dir / "assistant.jsonl"
    emit_event("sql", sql_summary="test_event", row_count=1)
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["type"] == "sql"
    assert record["sql_summary"] == "test_event"


def test_record_gemini_usage_updates_state(tmp_run_dir) -> None:
    total = record_gemini_usage(source="chat_completion", total_tokens=100, model="test")
    assert total == 100
    state_files = list(tmp_run_dir.glob("gemini_tokens_*.json"))
    assert len(state_files) == 1
    state = json.loads(state_files[0].read_text(encoding="utf-8"))
    assert state["total"] == 100
