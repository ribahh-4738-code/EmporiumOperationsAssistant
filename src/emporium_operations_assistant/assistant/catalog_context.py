"""Operational snapshot from PostgreSQL for the LLM system context."""

from __future__ import annotations

import psycopg
from psycopg.rows import dict_row

from emporium_operations_assistant.assistant.catalog_search import search_products_by_keywords
from emporium_operations_assistant.config import Settings, load_settings, postgres_connection_kwargs


def _aggregate_summary(settings: Settings) -> list[str]:
    with psycopg.connect(**postgres_connection_kwargs(settings)) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT count(*) AS n FROM products WHERE status = 'active'")
            active_products = cur.fetchone()["n"]
            cur.execute("SELECT count(*) AS n FROM customers")
            customers = cur.fetchone()["n"]
            cur.execute("SELECT count(*) AS n FROM orders")
            orders = cur.fetchone()["n"]
            cur.execute(
                """
                SELECT c.name, count(p.product_id) AS products
                FROM categories c
                LEFT JOIN products p ON p.category_id = c.category_id
                GROUP BY c.category_id, c.name
                ORDER BY products DESC
                LIMIT 5
                """
            )
            top_categories = cur.fetchall()
            cur.execute(
                """
                SELECT count(*) AS n FROM promotions WHERE is_active = TRUE
                """
            )
            active_promos = cur.fetchone()["n"]

    lines = [
        "Resumo atual do emporium (PostgreSQL):",
        f"- Produtos ativos: {active_products}",
        f"- Clientes cadastrados: {customers}",
        f"- Pedidos registrados: {orders}",
        f"- Promoções ativas: {active_promos}",
        "- Principais categorias (por quantidade de produtos):",
    ]
    for row in top_categories:
        lines.append(f"  • {row['name']}: {row['products']} produto(s)")
    return lines


def _format_product_hits(rows: list[dict[str, object]]) -> list[str]:
    lines = [
        "Produtos relacionados à pergunta (consulta SQL por palavras-chave):",
    ]
    for row in rows:
        price = row.get("price_brl")
        lines.append(
            f"- [{row.get('product_id')}] {row.get('name')} — "
            f"R$ {price}, estoque {row.get('stock_quantity')}, "
            f"categoria {row.get('category')}"
        )
        preview = row.get("description_preview")
        if preview:
            lines.append(f"  {preview}")
    return lines


def build_catalog_context(
    settings: Settings | None = None,
    user_query: str | None = None,
) -> str:
    """Summarize catalog; optionally add keyword-matched products for this turn."""
    settings = settings or load_settings()
    lines = _aggregate_summary(settings)

    if user_query and user_query.strip():
        hits = search_products_by_keywords(user_query, settings)
        if hits:
            lines.append("")
            lines.extend(_format_product_hits(hits))

    lines.append(
        "Use esses dados para catálogo e promoções. Detalhes de pedidos vêm em bloco separado "
        "(número do pedido, e-mail ou sessão CLI)."
    )
    return "\n".join(lines)
