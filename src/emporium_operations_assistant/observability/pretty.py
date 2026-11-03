"""Pretty-print assistant JSONL log lines (stdin → stdout)."""

from __future__ import annotations

import json
import sys


def _format_line(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    try:
        ev = json.loads(raw)
    except json.JSONDecodeError:
        return raw

    ts = ev.get("ts", "?")
    kind = ev.get("type", "?")
    level = ev.get("level", "")
    prefix = f"{ts} [{kind}]"
    if level:
        prefix += f" ({level})"

    if kind == "sql":
        return (
            f"{prefix} rows={ev.get('row_count', 0)} limit={ev.get('limit', '?')} "
            f"keywords={ev.get('keywords', [])}\n  {ev.get('sql_summary', '')}"
        )
    if kind == "rag":
        return (
            f"{prefix} collection={ev.get('collection')} chunks={ev.get('n_chunks', 0)} "
            f"query={ev.get('query_preview', '')!r}"
        )
    if kind == "embedding":
        return f"{prefix} model={ev.get('model')} texts={ev.get('n_texts', 1)}"
    if kind == "gemini":
        return (
            f"{prefix} source={ev.get('source')} turn={ev.get('turn_tokens')} "
            f"daily={ev.get('daily_total')} "
            f"(prompt={ev.get('prompt_tokens')} completion={ev.get('completion_tokens')})"
        )
    if kind == "gemini_budget":
        return f"{prefix} {ev.get('message')} daily={ev.get('daily_total')} budget={ev.get('daily_budget')}"

    extras = {k: v for k, v in ev.items() if k not in {"ts", "type", "level"}}
    return f"{prefix} {extras}"


def main() -> None:
    for line in sys.stdin:
        out = _format_line(line)
        if out:
            print(out, flush=True)


if __name__ == "__main__":
    main()
