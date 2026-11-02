"""Verify seed table row counts against manifest expectations."""

from __future__ import annotations

import psycopg
from psycopg import sql

from emporium_operations_assistant.config import postgres_connection_kwargs
from emporium_operations_assistant.seed.manifest import SeedManifest, load_manifest


def verify_counts(manifest: SeedManifest | None = None) -> None:
    manifest = manifest or load_manifest()
    kwargs = postgres_connection_kwargs()
    mismatches: list[str] = []
    with psycopg.connect(**kwargs) as conn:
        with conn.cursor() as cur:
            for key in manifest.load_order:
                spec = manifest.tables[key]
                cur.execute(
                    sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(spec.table))
                )
                count = cur.fetchone()[0]
                status = "ok" if count == spec.expected_rows else "MISMATCH"
                print(f"  {spec.table}: {count} (expected {spec.expected_rows}) [{status}]")
                if count != spec.expected_rows:
                    mismatches.append(
                        f"{spec.table}: got {count}, expected {spec.expected_rows}"
                    )
    if mismatches:
        raise SystemExit("Seed verification failed:\n" + "\n".join(mismatches))


def main() -> None:
    print("[run] Verifying seed row counts...")
    verify_counts()


if __name__ == "__main__":
    main()
