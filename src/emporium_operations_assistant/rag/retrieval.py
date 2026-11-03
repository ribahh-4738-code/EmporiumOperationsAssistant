"""Semantic search over indexed store policies."""

from __future__ import annotations

import logging

from emporium_operations_assistant.config import Settings, load_settings
from emporium_operations_assistant.rag.bootstrap import policy_collection_exists
from emporium_operations_assistant.rag.client import get_policy_collection
from emporium_operations_assistant.observability.events import emit_event
from emporium_operations_assistant.rag.embeddings import embed_texts

logger = logging.getLogger(__name__)

_MISSING_COLLECTION_HINT = "Collection store_policies does not exist"


def search_policy_chunks(query: str, settings: Settings | None = None) -> list[str]:
    """Return top matching text chunks for a user query."""
    settings = settings or load_settings()
    query = query.strip()
    if not query:
        return []

    if not policy_collection_exists(settings):
        logger.debug("RAG collection %s not found.", settings.chroma_collection)
        return []

    try:
        collection = get_policy_collection(settings)
        query_vector = embed_texts([query], settings)[0]
    except Exception as exc:
        msg = str(exc)
        if _MISSING_COLLECTION_HINT in msg:
            logger.debug("ChromaDB collection missing: %s", msg)
        else:
            logger.warning("ChromaDB unavailable for RAG: %s", exc)
        return []

    try:
        result = collection.query(
            query_embeddings=[query_vector],
            n_results=settings.rag_top_k,
        )
    except Exception as exc:
        logger.warning("ChromaDB query failed: %s", exc)
        return []

    documents = result.get("documents") or [[]]
    distances = (result.get("distances") or [[]])[0]
    chunks: list[str] = []
    for text in documents[0]:
        if text and text.strip():
            chunks.append(text.strip())
    emit_event(
        "rag",
        collection=settings.chroma_collection,
        query_preview=query[:120],
        n_chunks=len(chunks),
        top_k=settings.rag_top_k,
        distances=distances[: len(chunks)] if distances else [],
    )
    return chunks


def _policy_unavailable_instruction() -> str:
    return (
        "[Políticas da loja — documento não indexado]\n"
        "Não há trechos do PDF de políticas disponíveis no ChromaDB neste momento. "
        "NÃO confirme formas de pagamento, parcelamento, juros ou prazos. "
        "Diga honestamente que não consegue consultar o regulamento agora e oriente "
        "falar com a loja ou rodar ./scripts/chroma/ingest_rag.sh após o install."
    )


def build_policy_context(user_query: str, settings: Settings | None = None) -> str:
    """Format retrieved chunks for the LLM system instruction."""
    settings = settings or load_settings()
    if not policy_collection_exists(settings):
        return _policy_unavailable_instruction()

    chunks = search_policy_chunks(user_query, settings=settings)
    if not chunks:
        return (
            "[Políticas da loja — nenhum trecho relevante]\n"
            "A pergunta não retornou trechos do PDF. Não invente condições de pagamento; "
            "sugira reformular ou contato com a loja."
        )

    lines = [
        "Políticas e regras da loja (trechos relevantes do documento oficial — "
        "priorize estas informações para parcelamento, trocas, prazos e condições):",
    ]
    for i, chunk in enumerate(chunks, start=1):
        lines.append(f"--- Trecho {i} ---")
        lines.append(chunk)
    lines.append(
        "Se a pergunta não estiver coberta pelos trechos acima, diga que não "
        "encontrou no material disponível e oriente falar com a loja."
    )
    return "\n".join(lines)
