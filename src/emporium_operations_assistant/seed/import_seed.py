"""Truncate seed tables and import rows from data/*.csv."""

from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

from emporium_operations_assistant.config import postgres_connection_kwargs
from emporium_operations_assistant.seed.manifest import SeedManifest, TableSpec, load_manifest
from emporium_operations_assistant.seed.validate import SCHEMA_CHANGE_HINT, validate_csv_headers


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def _transform_row(spec: TableSpec, row: dict[str, str]) -> tuple[Any, ...]:
    values: list[Any] = []
    for column in spec.columns:
        raw = row.get(column, "")
        if spec.table == "products" and column == "specs":
            text = _blank_to_none(raw)
            values.append(Jsonb(json.loads(text)) if text else None)
        elif spec.table == "promotions" and column == "is_active":
            values.append(raw.strip() in {"1", "true", "True", "TRUE"})
        elif spec.table in {"orders", "customers", "categories"} and column in {
            "tracking_code",
            "estimated_delivery",
            "notes",
            "phone",
            "email",
            "city",
            "description",
        }:
            values.append(_blank_to_none(raw))
        elif column.endswith("_id") or column in {"stock_quantity", "quantity", "discount_percent"}:
            values.append(int(raw))
        elif column in {"price_brl", "total_brl"}:
            values.append(Decimal(raw))
        elif column in {"order_date", "created_at", "estimated_delivery"}:
            values.append(_blank_to_none(raw))
        else:
            values.append(raw)
    return tuple(values)


def _truncate_seed_tables(conn: psycopg.Connection, manifest: SeedManifest) -> None:
    table_names = [manifest.tables[key].table for key in manifest.truncate_order]
    query = sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE").format(
        sql.SQL(", ").join(sql.Identifier(name) for name in table_names)
    )
    with conn.cursor() as cur:
        cur.execute(query)
    conn.commit()
    print(f"[run] Truncated seed tables: {', '.join(table_names)}")


def _import_table(conn: psycopg.Connection, manifest: SeedManifest, key: str) -> None:
    spec = manifest.tables[key]
    csv_path = manifest.data_dir / spec.csv_file
    columns_sql = sql.SQL(", ").join(sql.Identifier(c) for c in spec.columns)
    placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in spec.columns)
    insert_sql = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier(spec.table),
        columns_sql,
        placeholders,
    )
    rows: list[tuple[Any, ...]] = []
    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(_transform_row(spec, row))
    with conn.cursor() as cur:
        cur.executemany(insert_sql, rows)
    conn.commit()
    print(f"[run] Imported {len(rows)} rows into {spec.table} from {spec.csv_file}")


def run_import(manifest: SeedManifest | None = None) -> None:
    manifest = manifest or load_manifest()
    validate_csv_headers(manifest)
    kwargs = postgres_connection_kwargs()
    try:
        with psycopg.connect(**kwargs) as conn:
            _truncate_seed_tables(conn, manifest)
            for key in manifest.load_order:
                _import_table(conn, manifest, key)
    except psycopg.Error as exc:
        raise SystemExit(f"Import failed: {exc}\n\n{SCHEMA_CHANGE_HINT}") from exc


def main() -> None:
    run_import()


if __name__ == "__main__":
    main()
