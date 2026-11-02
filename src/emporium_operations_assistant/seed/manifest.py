"""Load db/seed/manifest.json."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TableSpec:
    key: str
    csv_file: str
    table: str
    columns: list[str]
    expected_rows: int


@dataclass(frozen=True)
class SeedManifest:
    load_order: list[str]
    truncate_order: list[str]
    tables: dict[str, TableSpec]
    data_dir: Path
    root_dir: Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_manifest(root_dir: Path | None = None) -> SeedManifest:
    root = root_dir or project_root()
    manifest_path = root / "db" / "seed" / "manifest.json"
    raw: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    tables: dict[str, TableSpec] = {}
    for key, spec in raw["tables"].items():
        tables[key] = TableSpec(
            key=key,
            csv_file=spec["csv_file"],
            table=spec["table"],
            columns=list(spec["columns"]),
            expected_rows=int(spec["expected_rows"]),
        )
    return SeedManifest(
        load_order=list(raw["load_order"]),
        truncate_order=list(raw["truncate_order"]),
        tables=tables,
        data_dir=root / "data",
        root_dir=root,
    )
