"""Health check: Postgres, Chroma, RAG collection."""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request

from emporium_operations_assistant.config import load_settings
from emporium_operations_assistant.rag.bootstrap import policy_collection_exists


def _line(status: str, message: str) -> None:
    print(f"[{status}] {message}")


def main() -> None:
    settings = load_settings()
    failed = False
    warned = False

    container = __import__("os").environ.get("EMPORIUM_DOCKER_CONTAINER", "emporium_ops_postgres")
    try:
        proc = subprocess.run(
            [
                "docker",
                "exec",
                container,
                "pg_isready",
                "-U",
                settings.postgres_user,
                "-d",
                settings.postgres_db,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            _line("ok", f"PostgreSQL ({container})")
        else:
            _line("fail", f"PostgreSQL ({container}): {proc.stderr.strip() or 'not ready'}")
            failed = True
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        _line("fail", f"PostgreSQL check: {exc}")
        failed = True

    chroma_base = f"http://{settings.chroma_host}:{settings.chroma_port}"
    try:
        with urllib.request.urlopen(f"{chroma_base}/api/v2/heartbeat", timeout=5) as resp:
            _line("ok", f"Chroma heartbeat ({chroma_base})")
    except (urllib.error.URLError, TimeoutError) as exc:
        _line("fail", f"Chroma API: {exc}")
        failed = True

    try:
        with urllib.request.urlopen(f"{chroma_base}/api/v2/version", timeout=5) as resp:
            version = json.loads(resp.read().decode())
            _line("ok", f"Chroma version: {version}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        _line("warn", "Chroma version endpoint unavailable")

    if policy_collection_exists(settings):
        try:
            from emporium_operations_assistant.rag.client import get_policy_collection

            col = get_policy_collection(settings)
            count = col.count()
            _line("ok", f"Collection '{settings.chroma_collection}' — {count} chunk(s)")
        except Exception as exc:
            _line("warn", f"Collection '{settings.chroma_collection}': {exc}")
            warned = True
    else:
        _line("warn", f"Collection '{settings.chroma_collection}' not found (run ingest_rag.sh)")
        warned = True

    for name in (
        __import__("os").environ.get("EMPORIUM_DOCKER_CONTAINER", "emporium_ops_postgres"),
        __import__("os").environ.get("EMPORIUM_CHROMA_CONTAINER", "emporium_ops_chroma"),
        __import__("os").environ.get("EMPORIUM_CHROMA_ADMIN_CONTAINER", "emporium_ops_chroma_admin"),
    ):
        try:
            proc = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if proc.stdout.strip() == "true":
                _line("ok", f"Docker container running: {name}")
            else:
                _line("warn", f"Docker container not running: {name}")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            break

    if failed:
        raise SystemExit(1)
    if warned:
        raise SystemExit(0)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
