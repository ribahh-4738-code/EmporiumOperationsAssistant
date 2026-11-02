"""Load RAG document manifest."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from emporium_operations_assistant.config import project_root


@dataclass(frozen=True)
class RagDocument:
    path: str
    collection: str
    title: str


def load_rag_manifest(manifest_path: Path | None = None) -> list[RagDocument]:
    path = manifest_path or (project_root() / "db" / "seed" / "rag_manifest.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    docs: list[RagDocument] = []
    for item in data.get("documents", []):
        docs.append(
            RagDocument(
                path=str(item["path"]),
                collection=str(item.get("collection", "store_policies")),
                title=str(item.get("title", item["path"])),
            )
        )
    return docs
