"""Index manifest PDFs into ChromaDB."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from emporium_operations_assistant.config import Settings, load_settings, project_root
from emporium_operations_assistant.rag.chunking import chunk_text
from emporium_operations_assistant.rag.client import get_chroma_client
from emporium_operations_assistant.rag.embeddings import embed_texts
from emporium_operations_assistant.rag.manifest import RagDocument, load_rag_manifest
from emporium_operations_assistant.rag.pdf_extract import extract_pdf_text


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def ingest_document(doc: RagDocument, settings: Settings, *, force: bool = False) -> int:
    root = project_root()
    pdf_path = root / doc.path
    if not pdf_path.is_file():
        raise FileNotFoundError(f"RAG document not found: {pdf_path}")

    content_hash = _file_sha256(pdf_path)
    client = get_chroma_client(settings)

    try:
        collection = client.get_collection(name=doc.collection)
        stored_hash = (collection.metadata or {}).get("source_sha256")
        if not force and stored_hash == content_hash:
            print(f"[skip] {doc.path} unchanged (collection={doc.collection}).")
            return 0
        client.delete_collection(doc.collection)
    except Exception:
        pass

    text = extract_pdf_text(pdf_path)
    chunks = chunk_text(
        text,
        size=settings.rag_chunk_size,
        overlap=settings.rag_chunk_overlap,
    )
    if not chunks:
        print(f"[warn] No text extracted from {doc.path}", file=sys.stderr)
        return 0

    print(f"[run] Embedding {len(chunks)} chunk(s) with Gemini...")
    embeddings = embed_texts(chunks, settings)

    collection = client.create_collection(
        name=doc.collection,
        metadata={
            "source_sha256": content_hash,
            "source_path": doc.path,
            "title": doc.title,
            "embedding_model": settings.gemini_embedding_model,
        },
    )

    ids = [f"{content_hash[:16]}_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "source": doc.path,
            "title": doc.title,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]
    collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    print(
        f"[run] Indexed {len(chunks)} chunk(s) from {doc.path} "
        f"→ collection '{doc.collection}'."
    )
    return len(chunks)


def ingest_all(*, force: bool = False, settings: Settings | None = None) -> int:
    settings = settings or load_settings()
    total = 0
    for doc in load_rag_manifest():
        total += ingest_document(doc, settings, force=force)
    return total


def main() -> None:
    force = "--force" in sys.argv
    settings = load_settings()
    if not settings.gemini_api_key:
        print(
            "[skip] GEMINI_API_KEY not set; RAG ingest skipped (set key in .env and re-run).",
            file=sys.stderr,
        )
        raise SystemExit(0)
    try:
        count = ingest_all(force=force, settings=settings)
    except Exception as exc:
        print(f"RAG ingest failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    if count == 0 and not force:
        print("[run] RAG ingest complete (no reindex needed).")
    else:
        print(f"[run] RAG ingest complete ({count} new chunk(s) indexed).")


if __name__ == "__main__":
    main()
