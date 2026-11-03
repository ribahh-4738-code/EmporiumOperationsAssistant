"""Gemini embeddings (computed in app; not passed as Chroma server embedding function)."""

from __future__ import annotations

from google import genai

from emporium_operations_assistant.config import Settings, load_settings
from emporium_operations_assistant.observability.events import emit_event


def _gemini_client(settings: Settings) -> genai.Client:
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is required for embeddings.")
    return genai.Client(api_key=settings.gemini_api_key)


def embed_texts(texts: list[str], settings: Settings | None = None) -> list[list[float]]:
    """Embed one or more texts with Gemini text-embedding model."""
    if not texts:
        return []
    settings = settings or load_settings()
    client = _gemini_client(settings)
    model = settings.gemini_embedding_model
    vectors: list[list[float]] = []
    for text in texts:
        response = client.models.embed_content(model=model, contents=text)
        if not response.embeddings:
            raise RuntimeError("Gemini embed_content returned no embeddings.")
        values = response.embeddings[0].values
        if values is None:
            raise RuntimeError("Gemini embedding values missing.")
        vectors.append(list(values))
        meta = getattr(response, "usage_metadata", None)
        total = int(getattr(meta, "total_token_count", 0) or 0) if meta else 0
        emit_event(
            "embedding",
            model=model,
            n_texts=1,
            text_len=len(text),
            total_tokens=total or None,
        )
        if total:
            from emporium_operations_assistant.observability.token_budget import record_gemini_usage

            record_gemini_usage(
                source="embedding",
                total_tokens=total,
                model=model,
                settings=settings,
            )
    return vectors
