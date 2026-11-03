"""Keyword search over products for per-turn catalog context."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

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
        "vocês",
        "oi",
        "ola",
        "olá",
        "maiara",
        "pode",
        "me",
        "dizer",
        "the",
        "is",
        "até",
        "ate",
        "reais",
        "real",
        "máximo",
        "maximo",
        "custo",
        "custando",
        "custa",
        "opções",
        "opcoes",
        "disponíveis",
        "disponiveis",
        "quais",
    }
)

_MAX_PRICE_PATTERNS = (
    re.compile(r"\bat[eé]\s+r?\$?\s*([\d.,]+)", re.IGNORECASE),
    re.compile(r"\bm[aá]ximo\s+r?\$?\s*([\d.,]+)", re.IGNORECASE),
    re.compile(r"\bcustando\s+r?\$?\s*([\d.,]+)", re.IGNORECASE),
)


def _parse_brl_amount(raw: str) -> Decimal | None:
    cleaned = raw.strip().replace(" ", "")
    if not cleaned:
        return None
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        return None
    if value <= 0:
        return None
    return value


def extract_max_price_brl(user_query: str) -> Decimal | None:
    """Detect upper price bound from phrases like 'até R$ 1000'."""
    for pattern in _MAX_PRICE_PATTERNS:
        match = pattern.search(user_query)
        if match:
            return _parse_brl_amount(match.group(1))
    return None


def _query_without_price_phrases(user_query: str) -> str:
    text = user_query
    for pattern in _MAX_PRICE_PATTERNS:
        text = pattern.sub(" ", text)
    text = re.sub(r"\br?\$\s*[\d.,]+", " ", text)
    return text


def extract_keywords(user_query: str, *, min_length: int = 3) -> list[str]:
    tokens = re.findall(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ]+", user_query.lower())
    seen: set[str] = set()
    keywords: list[str] = []
    for token in tokens:
        if token.isdigit():
            continue
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
    max_price = extract_max_price_brl(user_query)
    keyword_source = _query_without_price_phrases(user_query)
    keywords = extract_keywords(keyword_source)
    if not keywords:
        emit_event(
            "sql",
            sql_summary="catalog_search skipped (no keywords)",
            row_count=0,
            max_price_brl=float(max_price) if max_price is not None else None,
        )
        return []

    patterns = [f"%{kw}%" for kw in keywords]
    limit = settings.catalog_search_limit
    price_clause = ""
    params: list[object] = [patterns, patterns, patterns]
    if max_price is not None:
        price_clause = " AND p.price_brl <= %s"
        params.append(max_price)
    params.append(limit)

    sql = f"""
SELECT p.product_id, p.name, p.price_brl, p.stock_quantity, c.name AS category,
       left(p.description, 200) AS description_preview
FROM products p
JOIN categories c ON c.category_id = p.category_id
WHERE p.status = 'active'
  AND (
    p.name ILIKE ANY(%s) OR p.description ILIKE ANY(%s) OR c.name ILIKE ANY(%s)
  ){price_clause}
ORDER BY p.price_brl ASC, p.stock_quantity DESC, p.name
LIMIT %s
"""
    with psycopg.connect(**postgres_connection_kwargs(settings)) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
    emit_event(
        "sql",
        sql_summary="catalog_search active products ILIKE keywords",
        keywords=keywords,
        row_count=len(rows),
        limit=limit,
        max_price_brl=float(max_price) if max_price is not None else None,
    )
    return [dict(row) for row in rows]
