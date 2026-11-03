"""Light RAG ingest/retrieval without Gemini HTTP or Chroma Docker."""

from __future__ import annotations

from pathlib import Path

import chromadb
import pytest

from emporium_operations_assistant.config import Settings
from emporium_operations_assistant.rag.chunking import chunk_text
from emporium_operations_assistant.rag.ingest import ingest_document
from emporium_operations_assistant.rag.manifest import RagDocument
from emporium_operations_assistant.rag import retrieval


FIXTURE_TEXT = (
    Path(__file__).resolve().parents[1] / "fixtures" / "rag" / "sample_policy.txt"
).read_text(encoding="utf-8")
EMBED_DIM = 8
MARKER = "UNIQUE_MARKER_RAG_TEST_42"


@pytest.fixture
def rag_settings(settings: Settings) -> Settings:
    from dataclasses import replace

    return replace(
        settings,
        rag_chunk_size=120,
        rag_chunk_overlap=20,
        chroma_collection="test_store_policies",
        gemini_embedding_model="test-embed",
    )


@pytest.fixture
def ephemeral_chroma(monkeypatch: pytest.MonkeyPatch) -> chromadb.ClientAPI:
    client = chromadb.EphemeralClient()

    def _fake_client(_settings=None):
        return client

    monkeypatch.setattr(
        "emporium_operations_assistant.rag.ingest.get_chroma_client",
        _fake_client,
    )
    monkeypatch.setattr(
        "emporium_operations_assistant.rag.client.get_chroma_client",
        _fake_client,
    )
    return client


@pytest.fixture
def mock_rag_io(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.setattr(
        "emporium_operations_assistant.rag.ingest.project_root",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        "emporium_operations_assistant.rag.ingest.extract_pdf_text",
        lambda _path: FIXTURE_TEXT,
    )

    def fake_embed(texts: list[str], settings=None) -> list[list[float]]:
        return [[0.1 * (i + 1)] * EMBED_DIM for i in range(len(texts))]

    monkeypatch.setattr(
        "emporium_operations_assistant.rag.ingest.embed_texts",
        fake_embed,
    )
    monkeypatch.setattr(
        "emporium_operations_assistant.rag.retrieval.embed_texts",
        fake_embed,
    )
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    pdf_path = data_dir / "mini.pdf"
    pdf_path.write_bytes(b"fake-pdf-bytes-for-hash")
    return pdf_path


def test_ingest_document_indexes_chunks(
    rag_settings: Settings,
    ephemeral_chroma: chromadb.ClientAPI,
    mock_rag_io: Path,
    tmp_run_dir,
) -> None:
    doc = RagDocument(
        path="data/mini.pdf",
        collection=rag_settings.chroma_collection,
        title="Test policies",
    )
    expected_chunks = chunk_text(
        FIXTURE_TEXT,
        size=rag_settings.rag_chunk_size,
        overlap=rag_settings.rag_chunk_overlap,
    )
    count = ingest_document(doc, rag_settings, force=True)
    assert count == len(expected_chunks)
    assert count >= 1

    collection = ephemeral_chroma.get_collection(rag_settings.chroma_collection)
    assert collection.count() == count
    meta = collection.metadata or {}
    assert meta.get("source_sha256")
    stored = collection.get(include=["documents"])
    docs = stored.get("documents") or []
    flat = " ".join(docs)
    assert MARKER in flat


def test_ingest_skips_unchanged_hash(
    rag_settings: Settings,
    ephemeral_chroma: chromadb.ClientAPI,
    mock_rag_io: Path,
    tmp_run_dir,
) -> None:
    doc = RagDocument(
        path="data/mini.pdf",
        collection=rag_settings.chroma_collection,
        title="Test policies",
    )
    first = ingest_document(doc, rag_settings, force=True)
    assert first >= 1
    second = ingest_document(doc, rag_settings, force=False)
    assert second == 0


def test_search_policy_chunks_with_ephemeral_collection(
    rag_settings: Settings,
    ephemeral_chroma: chromadb.ClientAPI,
    mock_rag_io: Path,
    monkeypatch: pytest.MonkeyPatch,
    tmp_run_dir,
) -> None:
    doc = RagDocument(
        path="data/mini.pdf",
        collection=rag_settings.chroma_collection,
        title="Test policies",
    )
    ingest_document(doc, rag_settings, force=True)

    monkeypatch.setattr(
        "emporium_operations_assistant.rag.retrieval.policy_collection_exists",
        lambda _settings=None: True,
    )

    chunks = retrieval.search_policy_chunks("parcelas PIX", settings=rag_settings)
    assert chunks
    assert any(MARKER in c or "PIX" in c for c in chunks)
