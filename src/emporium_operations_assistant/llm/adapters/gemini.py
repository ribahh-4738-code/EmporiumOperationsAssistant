"""Google Gemini cloud adapter."""

from __future__ import annotations

from google import genai
from google.genai import types

from emporium_operations_assistant.config import Settings
from emporium_operations_assistant.llm.types import ChatTurn, CompletionResult


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
        contents: list[types.Content] = []
        for turn in messages:
            role = "user" if turn.role == "user" else "model"
            contents.append(
                types.Content(role=role, parts=[types.Part.from_text(text=turn.content)])
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
        return CompletionResult(text=text, model=self._model)


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
