"""Conversation preparation (system prompt and profile context)."""

from __future__ import annotations

from dataclasses import dataclass

from emporium_operations_assistant.assistant.prompt_builder import build_system_instruction
from emporium_operations_assistant.assistant.repository import AssistantRepository
from emporium_operations_assistant.config import Settings, load_settings


@dataclass(frozen=True)
class PromptContext:
    profile_id: int
    profile_name: str
    display_name: str
    system_instruction: str


class AssistantService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or load_settings()
        self._repo = AssistantRepository(self._settings)

    def build_prompt_context(
        self,
        *,
        module_keys: list[str] | None = None,
    ) -> PromptContext:
        profile = self._repo.get_profile_by_name(self._settings.assistant_profile_name)
        if not profile:
            raise LookupError(
                f"Assistant profile not found: {self._settings.assistant_profile_name!r}. "
                "Run ./install.sh or seed_assistant.sh."
            )
        modules = self._repo.list_module_prompts(profile.id)
        instruction = build_system_instruction(profile, modules, include_module_keys=module_keys)
        return PromptContext(
            profile_id=profile.id,
            profile_name=profile.profile_name,
            display_name=profile.display_name,
            system_instruction=instruction,
        )
