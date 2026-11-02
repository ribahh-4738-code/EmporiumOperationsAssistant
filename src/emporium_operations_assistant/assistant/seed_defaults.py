"""Idempotent seed for assistant profile and module prompts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import psycopg

from emporium_operations_assistant.config import load_settings, postgres_connection_kwargs


def _default_seed_path() -> Path:
    return Path(__file__).resolve().parents[3] / "db" / "seed" / "assistant" / "default.json"


def _load_seed_file(path: Path | None = None) -> dict[str, Any]:
    seed_path = path or _default_seed_path()
    return json.loads(seed_path.read_text(encoding="utf-8"))


def seed_assistant_defaults(*, force_profile: bool = False) -> None:
    """
    Insert default profile and prompts if missing.
    Does not truncate assistant_chat_message or overwrite existing prompt text.
    """
    settings = load_settings()
    data = _load_seed_file()
    profile_data = data["profile"]
    profile_name = profile_data["profile_name"]
    display_name = settings.assistant_display_name

    with psycopg.connect(**postgres_connection_kwargs(settings)) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, system_prompt FROM assistant_profile WHERE profile_name = %s",
                (profile_name,),
            )
            existing = cur.fetchone()
            if existing:
                profile_id = existing[0]
                print(f"[skip] Profile '{profile_name}' already exists (id={profile_id}).")
                if force_profile:
                    cur.execute(
                        """
                        UPDATE assistant_profile
                        SET display_name = %s, timezone = %s, system_prompt = %s, updated_at = now()
                        WHERE id = %s
                        """,
                        (
                            display_name,
                            profile_data["timezone"],
                            profile_data["system_prompt"],
                            profile_id,
                        ),
                    )
                    print(f"[run] Profile '{profile_name}' updated (--force-profile).")
            else:
                cur.execute(
                    """
                    INSERT INTO assistant_profile
                        (profile_name, display_name, timezone, system_prompt, enabled)
                    VALUES (%s, %s, %s, %s, TRUE)
                    RETURNING id
                    """,
                    (
                        profile_name,
                        display_name,
                        profile_data["timezone"],
                        profile_data["system_prompt"],
                    ),
                )
                profile_id = cur.fetchone()[0]
                print(f"[run] Created profile '{profile_name}' (id={profile_id}).")

            for item in data.get("prompts", []):
                module_key = item["module_key"]
                cur.execute(
                    """
                    SELECT id FROM assistant_prompt
                    WHERE profile_id = %s AND module_key = %s
                    """,
                    (profile_id, module_key),
                )
                if cur.fetchone():
                    print(f"[skip] Prompt module '{module_key}' already exists.")
                    continue
                cur.execute(
                    """
                    INSERT INTO assistant_prompt (profile_id, module_key, prompt, enabled)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (profile_id, module_key, item["prompt"], item.get("enabled", True)),
                )
                print(f"[run] Inserted prompt module '{module_key}'.")
        conn.commit()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Seed assistant profile and prompts.")
    parser.add_argument(
        "--force-profile",
        action="store_true",
        help="Overwrite system_prompt/timezone/display_name for existing profile.",
    )
    args = parser.parse_args()
    seed_assistant_defaults(force_profile=args.force_profile)


if __name__ == "__main__":
    main()
