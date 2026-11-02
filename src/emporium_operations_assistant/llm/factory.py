"""Instantiate LLM providers from settings."""

from __future__ import annotations

from emporium_operations_assistant.config import Settings, load_settings
from emporium_operations_assistant.llm.adapters.gemini import GeminiAdapter
from emporium_operations_assistant.llm.adapters.stub_local import LocalGemmaAdapter
from emporium_operations_assistant.llm.base import LLMProvider


def get_llm_provider(settings: Settings | None = None) -> LLMProvider:
    settings = settings or load_settings()
    provider = settings.llm_provider
    if provider == "gemini":
        return GeminiAdapter(settings)
    if provider in {"gemma", "local", "local_gemma"}:
        return LocalGemmaAdapter()
    raise ValueError(f"Unsupported LLM_PROVIDER: {provider!r}")
