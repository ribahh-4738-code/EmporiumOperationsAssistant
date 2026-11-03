"""PostgreSQL reads for order context."""

from __future__ import annotations

import psycopg
from psycopg.rows import dict_row

from emporium_operations_assistant.config import Settings, load_settings, postgres_connection_kwargs
from emporium_operations_assistant.observability.events import emit_event

_ORDER_DETAIL_SQL = """
SELECT o.order_id, o.customer_id, o.order_date, o.status, o.total_brl,
       o.payment_method, o.tracking_code, o.estimated_delivery, o.notes,
       c.name AS customer_name, c.email AS customer_email, c.city AS customer_city
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.order_id = %s
"""

_ORDER_ITEMS_SQL = """
SELECT oi.quantity, p.product_id, p.name AS product_name
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
WHERE oi.order_id = %s
ORDER BY p.name
LIMIT %s
"""

_CUSTOMER_BY_EMAIL_SQL = """
SELECT customer_id, name, email, city
FROM customers
WHERE lower(trim(email)) = lower(trim(%s))
LIMIT 1
"""

_ORDERS_FOR_CUSTOMER_SQL = """
SELECT order_id, order_date, status, total_brl, payment_method,
       tracking_code, estimated_delivery, notes
FROM orders
WHERE customer_id = %s
ORDER BY order_date DESC, order_id DESC
LIMIT %s
"""


def get_order_detail(
    order_id: int,
    settings: Settings | None = None,
    *,
    max_items: int | None = None,
) -> dict[str, object] | None:
    settings = settings or load_settings()
    item_limit = max_items if max_items is not None else settings.order_detail_max_items
    with psycopg.connect(**postgres_connection_kwargs(settings)) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(_ORDER_DETAIL_SQL, (order_id,))
            header = cur.fetchone()
            if not header:
                emit_event(
                    "sql",
                    sql_summary="order_by_id",
                    order_id=order_id,
                    row_count=0,
                )
                return None
            cur.execute(_ORDER_ITEMS_SQL, (order_id, item_limit))
            items = cur.fetchall()
    emit_event(
        "sql",
        sql_summary="order_by_id",
        order_id=order_id,
        customer_id=header["customer_id"],
        row_count=1,
        item_count=len(items),
    )
    return {"header": dict(header), "items": [dict(row) for row in items]}


def get_customer_by_email(
    email: str,
    settings: Settings | None = None,
) -> dict[str, object] | None:
    settings = settings or load_settings()
    with psycopg.connect(**postgres_connection_kwargs(settings)) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(_CUSTOMER_BY_EMAIL_SQL, (email,))
            row = cur.fetchone()
    emit_event(
        "sql",
        sql_summary="customer_by_email",
        email=email,
        row_count=1 if row else 0,
    )
    return dict(row) if row else None


def list_orders_for_customer(
    customer_id: int,
    settings: Settings | None = None,
    *,
    limit: int | None = None,
) -> list[dict[str, object]]:
    settings = settings or load_settings()
    row_limit = limit if limit is not None else settings.order_context_limit
    with psycopg.connect(**postgres_connection_kwargs(settings)) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(_ORDERS_FOR_CUSTOMER_SQL, (customer_id, row_limit))
            rows = cur.fetchall()
    emit_event(
        "sql",
        sql_summary="orders_for_customer",
        customer_id=customer_id,
        row_count=len(rows),
        limit=row_limit,
    )
    return [dict(row) for row in rows]
