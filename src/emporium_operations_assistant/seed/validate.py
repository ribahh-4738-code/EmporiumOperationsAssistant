"""Validate CSV file headers against the seed manifest."""

from __future__ import annotations

import csv
from pathlib import Path

from emporium_operations_assistant.seed.manifest import SeedManifest, load_manifest

SCHEMA_CHANGE_HINT = (
    "CSV structure changed. Update db/seed/manifest.json, db/schema.sql, "
    "and add db/migrations/NNN_*.sql, then re-run ./install.sh."
)


def _read_csv_header(csv_path: Path) -> list[str]:
    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def validate_csv_headers(manifest: SeedManifest | None = None) -> None:
    manifest = manifest or load_manifest()
    errors: list[str] = []
    for key in manifest.load_order:
        spec = manifest.tables[key]
        csv_path = manifest.data_dir / spec.csv_file
        if not csv_path.is_file():
            errors.append(f"{spec.csv_file}: file not found")
            continue
        header = _read_csv_header(csv_path)
        if header != spec.columns:
            errors.append(
                f"{spec.csv_file}: header mismatch\n"
                f"  expected: {spec.columns}\n"
                f"  actual:   {header}"
            )
    if errors:
        msg = "\n".join(errors) + "\n\n" + SCHEMA_CHANGE_HINT
        raise SystemExit(msg)
