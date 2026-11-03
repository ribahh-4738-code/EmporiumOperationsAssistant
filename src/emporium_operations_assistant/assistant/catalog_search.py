"""Keyword search over products for per-turn catalog context."""

from __future__ import annotations

import re

import psycopg
from psycopg.rows import dict_row

from emporium_operations_assistant.config import Settings, load_settings, postgres_connection_kwargs
from emporium_operations_assistant.observability.events import emit_event

_STOPWORDS = frozenset(
    {
        "a",
        "o",
        "as",
        "os",
        "de",
        "da",
        "do",
        "das",
        "dos",
        "e",
        "em",
        "no",
        "na",
        "nos",
        "nas",
        "um",
        "uma",
        "para",
        "por",
        "com",
        "que",
        "qual",
        "quais",
        "como",
        "você",
        "voce",
        "oi",
        "ola",
        "olá",
        "maiara",
        "pode",
        "me",
        "dizer",
        "the",
        "is",
    }
)

_PRODUCT_SEARCH_SQL = """
SELECT p.product_id, p.name, p.price_brl, p.stock_quantity, c.name AS category,
       left(p.description, 200) AS description_preview
FROM products p
JOIN categories c ON c.category_id = p.category_id
WHERE p.status = 'active'
  AND (
    p.name ILIKE ANY(%s) OR p.description ILIKE ANY(%s) OR c.name ILIKE ANY(%s)
  )
ORDER BY p.stock_quantity DESC, p.name
LIMIT %s
"""


def extract_keywords(user_query: str, *, min_length: int = 3) -> list[str]:
    tokens = re.findall(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ]+", user_query.lower())
    seen: set[str] = set()
    keywords: list[str] = []
    for token in tokens:
        if len(token) < min_length or token in _STOPWORDS:
            continue
        if token not in seen:
            seen.add(token)
            keywords.append(token)
    return keywords


def search_products_by_keywords(
    user_query: str,
    settings: Settings | None = None,
) -> list[dict[str, object]]:
    settings = settings or load_settings()
    keywords = extract_keywords(user_query)
    if not keywords:
        emit_event("sql", sql_summary="catalog_search skipped (no keywords)", row_count=0)
        return []

    patterns = [f"%{kw}%" for kw in keywords]
    limit = settings.catalog_search_limit
    with psycopg.connect(**postgres_connection_kwargs(settings)) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                _PRODUCT_SEARCH_SQL,
                (patterns, patterns, patterns, limit),
            )
            rows = cur.fetchall()
    emit_event(
        "sql",
        sql_summary="catalog_search active products ILIKE keywords",
        keywords=keywords,
        row_count=len(rows),
        limit=limit,
    )
    return [dict(row) for row in rows]
