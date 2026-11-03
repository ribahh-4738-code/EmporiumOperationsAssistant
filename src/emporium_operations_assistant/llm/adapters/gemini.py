"""Google Gemini cloud adapter."""

from __future__ import annotations

from google import genai
from google.genai import types

from emporium_operations_assistant.config import Settings
from emporium_operations_assistant.llm.history import normalize_turns_for_llm
from emporium_operations_assistant.llm.roles import ROLE_USER, to_llm_role
from emporium_operations_assistant.llm.types import ChatTurn, CompletionResult, TokenUsage
from emporium_operations_assistant.observability.token_budget import record_gemini_usage


def _parse_usage(response: object) -> TokenUsage | None:
    meta = getattr(response, "usage_metadata", None)
    if meta is None:
        return None
    prompt = int(getattr(meta, "prompt_token_count", 0) or 0)
    completion = int(getattr(meta, "candidates_token_count", 0) or 0)
    total = int(getattr(meta, "total_token_count", 0) or 0)
    if total == 0:
        total = prompt + completion
    if total == 0 and prompt == 0 and completion == 0:
        return None
    return TokenUsage(
        prompt_tokens=prompt,
        completion_tokens=completion,
        total_tokens=total,
    )


class GeminiAdapter:
    """Gemini API via google-genai SDK."""

    def __init__(self, settings: Settings) -> None:
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is required when LLM_PROVIDER=gemini. Set it in .env."
            )
        self._settings = settings
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model

    def complete(
        self,
        messages: list[ChatTurn],
        *,
        system_instruction: str | None = None,
    ) -> CompletionResult:
        turns = normalize_turns_for_llm(messages)
        if not turns:
            turns = [ChatTurn(role=ROLE_USER, content="Olá")]

        contents: list[types.Content] = []
        for turn in turns:
            api_role = to_llm_role(turn.role)
            contents.append(
                types.Content(
                    role=api_role,
                    parts=[types.Part.from_text(text=turn.content)],
                )
            )
        config = types.GenerateContentConfig(
            temperature=self._settings.llm_temperature,
            system_instruction=system_instruction,
        )
        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=config,
        )
        text = (response.text or "").strip()
        usage = _parse_usage(response)
        if usage:
            record_gemini_usage(
                source="chat_completion",
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                model=self._model,
                settings=self._settings,
            )
        return CompletionResult(text=text, model=self._model, usage=usage)


def main() -> None:
    """Optional smoke test: GEMINI_API_KEY must be set."""
    import os

    if os.environ.get("DRY_RUN") == "1":
        print("Gemini adapter dry-run OK (no API call).")
        return
    from emporium_operations_assistant.config import load_settings

    adapter = GeminiAdapter(load_settings())
    result = adapter.complete(
        [ChatTurn(role="user", content="Responda apenas: ok")],
        system_instruction="Responda de forma breve.",
    )
    print(result.text)


if __name__ == "__main__":
    main()
