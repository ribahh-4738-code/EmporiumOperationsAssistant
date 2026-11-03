"""Smoke test: repo CSV headers match seed manifest."""

from __future__ import annotations

from emporium_operations_assistant.seed.validate import validate_csv_headers


def test_validate_csv_headers_matches_manifest() -> None:
    validate_csv_headers()
