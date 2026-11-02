"""Ensure Chroma policy index exists before chat."""

from __future__ import annotations

import logging

from emporium_operations_assistant.config import Settings, load_settings
from emporium_operations_assistant.rag.client import get_chroma_client
from emporium_operations_assistant.rag.ingest import ingest_all

logger = logging.getLogger(__name__)


def policy_collection_exists(settings: Settings | None = None) -> bool:
    settings = settings or load_settings()
    try:
        client = get_chroma_client(settings)
        names = {col.name for col in client.list_collections()}
        return settings.chroma_collection in names
    except Exception as exc:
        logger.debug("Could not list Chroma collections: %s", exc)
        return False


def ensure_policy_index(
    settings: Settings | None = None,
    *,
    quiet: bool = False,
) -> bool:
    """
    Create store_policies collection from manifest PDFs if missing.
    Returns True when the collection exists after this call.
    """
    settings = settings or load_settings()
    if policy_collection_exists(settings):
        return True
    if not settings.gemini_api_key:
        logger.debug("GEMINI_API_KEY missing; cannot build RAG index.")
        return False
    if not quiet:
        print(
            "[run] Coleção RAG ausente; indexando PDF de políticas no ChromaDB...",
            flush=True,
        )
    try:
        ingest_all(settings=settings)
    except Exception as exc:
        logger.warning("RAG ingest failed during bootstrap: %s", exc)
        return False
    ready = policy_collection_exists(settings)
    if ready and not quiet:
        print("[run] Índice de políticas pronto.", flush=True)
    return ready
