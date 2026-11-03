"""Extract order id and email hints from user messages."""

from __future__ import annotations

import re

_ORDER_ID_PATTERNS = (
    re.compile(r"\bpedido\s+#?\s*(\d+)\b", re.IGNORECASE),
    re.compile(r"\bn[uú]mero\s+do\s+pedido\s+#?\s*(\d+)\b", re.IGNORECASE),
    re.compile(r"\border\s+#?\s*(\d+)\b", re.IGNORECASE),
)

_EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)


def extract_order_id(text: str) -> int | None:
    """Return order id when the user explicitly references a pedido/order number."""
    for pattern in _ORDER_ID_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))
    return None


def extract_email(text: str) -> str | None:
    match = _EMAIL_PATTERN.search(text)
    if not match:
        return None
    return match.group(0).strip()
