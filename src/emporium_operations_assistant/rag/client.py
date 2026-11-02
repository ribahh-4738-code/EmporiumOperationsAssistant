"""ChromaDB HTTP client helpers."""

from __future__ import annotations

import chromadb

from emporium_operations_assistant.config import Settings, load_settings


def get_chroma_client(settings: Settings | None = None) -> chromadb.HttpClient:
    settings = settings or load_settings()
    return chromadb.HttpClient(
        host=settings.chroma_host,
        port=settings.chroma_port,
    )


def get_policy_collection(settings: Settings | None = None, *, name: str | None = None):
    """Get collection by name (embeddings supplied by app on add/query)."""
    settings = settings or load_settings()
    client = get_chroma_client(settings)
    collection_name = name or settings.chroma_collection
    return client.get_collection(name=collection_name)
