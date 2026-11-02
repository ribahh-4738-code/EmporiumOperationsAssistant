"""PostgreSQL access for assistant_* tables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from emporium_operations_assistant.config import Settings, load_settings, postgres_connection_kwargs


@dataclass(frozen=True)
class AssistantProfile:
    id: int
    profile_name: str
    display_name: str
    timezone: str
    system_prompt: str
    enabled: bool


@dataclass(frozen=True)
class ModulePrompt:
    module_key: str
    prompt: str
    enabled: bool


class AssistantRepository:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or load_settings()

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(**postgres_connection_kwargs(self._settings))

    def get_profile_by_name(self, profile_name: str) -> AssistantProfile | None:
        with self._connect() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT id, profile_name, display_name, timezone, system_prompt, enabled
                    FROM assistant_profile
                    WHERE profile_name = %s AND enabled = TRUE
                    """,
                    (profile_name,),
                )
                row = cur.fetchone()
        if not row:
            return None
        return AssistantProfile(**row)

    def list_module_prompts(self, profile_id: int, *, enabled_only: bool = True) -> list[ModulePrompt]:
        query = """
            SELECT module_key, prompt, enabled
            FROM assistant_prompt
            WHERE profile_id = %s
        """
        params: list[Any] = [profile_id]
        if enabled_only:
            query += " AND enabled = TRUE"
        query += " ORDER BY module_key"
        with self._connect() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
        return [ModulePrompt(**row) for row in rows]

    def append_message(
        self,
        profile_id: int,
        role: str,
        message_text: str,
        *,
        model: str | None = None,
        channel: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO assistant_chat_message
                        (profile_id, role, message_text, model, channel, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        profile_id,
                        role,
                        message_text,
                        model,
                        channel,
                        Jsonb(metadata or {}),
                    ),
                )
                message_id = cur.fetchone()[0]
            conn.commit()
        return int(message_id)

    def profile_seed_complete(self, profile_name: str, expected_module_keys: list[str]) -> bool:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM assistant_profile WHERE profile_name = %s",
                    (profile_name,),
                )
                row = cur.fetchone()
                if not row:
                    return False
                profile_id = row[0]
                for key in expected_module_keys:
                    cur.execute(
                        """
                        SELECT 1 FROM assistant_prompt
                        WHERE profile_id = %s AND module_key = %s
                        """,
                        (profile_id, key),
                    )
                    if not cur.fetchone():
                        return False
        return True
