"""Orchestrate user turns: history, LLM, and audit persistence."""

from __future__ import annotations

import logging
import os

from emporium_operations_assistant.assistant.catalog_context import build_catalog_context
from emporium_operations_assistant.assistant.repository import AssistantRepository
from emporium_operations_assistant.assistant.service import AssistantService
from emporium_operations_assistant.config import Settings, load_settings
from emporium_operations_assistant.llm.factory import get_llm_provider
from emporium_operations_assistant.llm.history import normalize_turns_for_llm
from emporium_operations_assistant.llm.roles import ROLE_USER, to_llm_role, to_storage_role
from emporium_operations_assistant.llm.types import ChatTurn

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or load_settings()
        self._assistant = AssistantService(self._settings)
        self._repo = AssistantRepository(self._settings)
        self._llm = get_llm_provider(self._settings)

    @property
    def display_name(self) -> str:
        return self._assistant.build_prompt_context().display_name

    def _system_instruction(self) -> str:
        ctx = self._assistant.build_prompt_context()
        catalog = build_catalog_context(self._settings)
        return f"{ctx.system_instruction}\n\n{catalog}"

    def _history_turns(self, profile_id: int) -> list[ChatTurn]:
        stored = self._repo.list_recent_messages(
            profile_id,
            limit=self._settings.chat_history_limit,
            channel=self._settings.chat_channel,
        )
        turns: list[ChatTurn] = []
        for msg in stored:
            turns.append(
                ChatTurn(role=to_llm_role(msg.role), content=msg.message_text)
            )
        return turns

    def complete_user_message(self, user_text: str) -> str:
        """Persist user message, call LLM with history, persist assistant reply."""
        prompt_ctx = self._assistant.build_prompt_context()
        profile_id = prompt_ctx.profile_id
        channel = self._settings.chat_channel

        self._repo.append_message(
            profile_id,
            "user",
            user_text,
            channel=channel,
        )

        messages = normalize_turns_for_llm(self._history_turns(profile_id))
        if not messages or messages[-1].role != ROLE_USER:
            messages = normalize_turns_for_llm(
                messages + [ChatTurn(role=ROLE_USER, content=user_text)]
            )
        try:
            result = self._llm.complete(
                messages,
                system_instruction=self._system_instruction(),
            )
            reply = result.text
            if not reply:
                reply = (
                    "Desculpe, não consegui formular uma resposta agora. "
                    "Pode reformular a mensagem?"
                )
        except Exception as exc:
            if os.environ.get("CHAT_DEBUG", "").lower() in {"1", "true", "yes"}:
                logger.exception("LLM completion failed")
                print(f"[debug] LLM error: {exc}", flush=True)
            reply = (
                "Desculpe, tive um problema ao processar sua mensagem. "
                "Pode tentar de novo em instantes?"
            )
            self._repo.append_message(
                profile_id,
                to_storage_role("model"),
                reply,
                model=self._settings.gemini_model,
                channel=channel,
                metadata={"error": True, "error_type": type(exc).__name__},
            )
            return reply

        self._repo.append_message(
            profile_id,
            to_storage_role("model"),
            reply,
            model=result.model,
            channel=channel,
        )
        return reply
