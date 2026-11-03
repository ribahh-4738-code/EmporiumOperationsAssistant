"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from emporium_operations_assistant.config import Settings, load_settings


@pytest.fixture
def tmp_run_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolate .run/ and JSONL log under tmp_path."""
    run = tmp_path / ".run"
    run.mkdir()
    log = run / "assistant.jsonl"
    monkeypatch.setenv("ASSISTANT_LOG_PATH", str(log))
    monkeypatch.setattr(
        "emporium_operations_assistant.observability.paths.run_dir",
        lambda: run,
    )
    return run


@pytest.fixture
def settings() -> Settings:
    return load_settings(load_env_file=False)
