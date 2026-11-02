"""Short operational snapshot from PostgreSQL for the LLM system context."""

from __future__ import annotations

import psycopg
from psycopg.rows import dict_row

from emporium_operations_assistant.config import Settings, load_settings, postgres_connection_kwargs


def build_catalog_context(settings: Settings | None = None) -> str:
    """Summarize catalog and orders for the assistant (no ChromaDB yet)."""
    settings = settings or load_settings()
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
    lines.append(
        "Use esses dados quando o cliente perguntar sobre catálogo, pedidos ou promoções. "
        "Se precisar de detalhe que não estiver aqui, seja honesta e sugira reformular ou falar com a loja."
    )
    return "\n".join(lines)
