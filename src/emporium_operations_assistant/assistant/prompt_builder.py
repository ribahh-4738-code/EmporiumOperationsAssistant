"""Assemble system and module prompts for the LLM."""

from __future__ import annotations

from emporium_operations_assistant.assistant.repository import AssistantProfile, ModulePrompt


def build_system_instruction(
    profile: AssistantProfile,
    module_prompts: list[ModulePrompt],
    *,
    include_module_keys: list[str] | None = None,
) -> str:
    """Combine persona system_prompt with optional module instructions."""
    parts = [profile.system_prompt.strip()]
    keys = set(include_module_keys) if include_module_keys is not None else None
    for mod in module_prompts:
        if keys is not None and mod.module_key not in keys:
            continue
        parts.append(f"\n\n[{mod.module_key}]\n{mod.prompt.strip()}")
    return "".join(parts)
