"""Build order-related system context for the assistant."""

from __future__ import annotations

from emporium_operations_assistant.assistant.order_lookup import extract_email, extract_order_id
from emporium_operations_assistant.assistant.order_queries import (
    get_customer_by_email,
    get_order_detail,
    list_orders_for_customer,
)
from emporium_operations_assistant.config import Settings, load_settings


def _format_order_header(header: dict[str, object], *, title: str) -> list[str]:
    lines = [title]
    lines.append(
        f"- Pedido #{header.get('order_id')} — cliente {header.get('customer_name')} "
        f"({header.get('customer_email')})"
    )
    lines.append(
        f"  Data: {header.get('order_date')}, status: {header.get('status')}, "
        f"total R$ {header.get('total_brl')}, pagamento: {header.get('payment_method')}"
    )
    tracking = header.get("tracking_code")
    if tracking:
        lines.append(f"  Rastreio: {tracking}")
    eta = header.get("estimated_delivery")
    if eta:
        lines.append(f"  Entrega prevista: {eta}")
    notes = header.get("notes")
    if notes:
        lines.append(f"  Observações: {notes}")
    return lines


def _format_items(items: list[dict[str, object]]) -> list[str]:
    if not items:
        return ["  (sem itens registrados)"]
    lines: list[str] = ["  Itens:"]
    for row in items:
        lines.append(
            f"  • {row.get('quantity')}× [{row.get('product_id')}] {row.get('product_name')}"
        )
    return lines


def _format_order_list(rows: list[dict[str, object]], customer_label: str) -> list[str]:
    lines = [
        f"Pedidos recentes no PostgreSQL ({customer_label}):",
    ]
    if not rows:
        lines.append("- Nenhum pedido encontrado para este cliente.")
        return lines
    for row in rows:
        line = (
            f"- #{row.get('order_id')} ({row.get('order_date')}) — {row.get('status')}, "
            f"R$ {row.get('total_brl')}, {row.get('payment_method')}"
        )
        if row.get("tracking_code"):
            line += f", rastreio {row.get('tracking_code')}"
        lines.append(line)
    return lines


def build_order_context(
    settings: Settings | None = None,
    user_query: str | None = None,
    session_customer_id: int | None = None,
) -> str:
    """Resolve order context: order number > email > session customer."""
    settings = settings or load_settings()
    query = (user_query or "").strip()
    lines: list[str] = []

    order_id = extract_order_id(query) if query else None
    if order_id is not None:
        detail = get_order_detail(order_id, settings)
        if detail is None:
            lines.append(f"Consulta de pedido: pedido #{order_id} não encontrado no PostgreSQL.")
        else:
            header = detail["header"]
            assert isinstance(header, dict)
            items_obj = detail["items"]
            assert isinstance(items_obj, list)
            items: list[dict[str, object]] = [x for x in items_obj if isinstance(x, dict)]
            lines.extend(
                _format_order_header(
                    header,
                    title="Detalhe do pedido (consulta por número do pedido):",
                )
            )
            lines.extend(_format_items(items))
    else:
        email = extract_email(query) if query else None
        if email:
            customer = get_customer_by_email(email, settings)
            if customer is None:
                lines.append(
                    f"Consulta de pedido: nenhum cliente cadastrado com o e-mail {email!r}."
                )
            else:
                cid = int(customer["customer_id"])
                orders = list_orders_for_customer(cid, settings)
                label = f"{customer.get('name')} <{customer.get('email')}>"
                lines.extend(_format_order_list(orders, label))
        elif session_customer_id is not None:
            orders = list_orders_for_customer(session_customer_id, settings)
            lines.extend(
                _format_order_list(orders, f"cliente_id={session_customer_id} (sessão CLI)")
            )

    if not lines:
        return ""

    lines.append(
        "Use somente estes dados de pedidos. Não invente status, rastreio ou itens. "
        "Se faltar informação, diga com honestidade."
    )
    return "\n".join(lines)
