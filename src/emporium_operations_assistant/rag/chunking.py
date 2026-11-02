"""Split long text into overlapping chunks for embedding."""

from __future__ import annotations


def chunk_text(text: str, *, size: int, overlap: int) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []
    if size <= 0:
        raise ValueError("size must be positive")
    overlap = max(0, min(overlap, size - 1))
    step = size - overlap
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        piece = normalized[start : start + size].strip()
        if piece:
            chunks.append(piece)
        if start + size >= len(normalized):
            break
        start += step
    return chunks
