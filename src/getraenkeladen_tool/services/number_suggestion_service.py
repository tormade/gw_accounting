import re
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Document, Order


def suggest_order_number(session: Session, prefix: str = "AUF-", fallback_date: str | None = None) -> str:
    latest = session.scalar(
        select(Order.order_number)
        .where(Order.number_released == False)  # noqa: E712
        .order_by(Order.id.desc())
        .limit(1)
    )
    return _next_number(latest, prefix, fallback_date)


def suggest_document_number(
    session: Session,
    document_type: str,
    prefix: str | None = None,
    fallback_date: str | None = None,
) -> str:
    effective_prefix = prefix or ("RE-" if document_type == "Rechnung" else "LS-")
    latest = session.scalar(
        select(Document.document_number)
        .where(Document.document_type == document_type)
        .where(Document.number_released == False)  # noqa: E712
        .order_by(Document.id.desc())
        .limit(1)
    )
    return _next_number(latest, effective_prefix, fallback_date)


def _next_number(latest: str | None, prefix: str, fallback_date: str | None) -> str:
    if latest:
        match = re.search(r"(\d+)$", latest.strip())
        if match:
            number = match.group(1)
            return f"{latest[: match.start(1)]}{int(number) + 1:0{len(number)}d}"
    compact_date = (fallback_date or date.today().isoformat()).replace("-", "")
    return f"{prefix}{compact_date}-1"
