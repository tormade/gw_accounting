from dataclasses import dataclass
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Document, Order


@dataclass(frozen=True)
class NumberSuggestions:
    order_number: str
    delivery_note_number: str
    invoice_number: str


def suggest_next_numbers(session: Session) -> NumberSuggestions:
    return NumberSuggestions(
        order_number=next_order_number(session),
        delivery_note_number=next_document_number(
            session,
            document_type="Lieferschein",
            prefix="LS",
            start=3001,
            aliases=("Lieferauftrag",),
        ),
        invoice_number=next_document_number(session, document_type="Rechnung", prefix="RG", start=3001),
    )


def next_order_number(session: Session) -> str:
    existing_numbers = session.scalars(select(Order.order_number)).all()
    return next_number_for_prefix(existing_numbers, prefix="AUF", start=1001)


def next_document_number(
    session: Session,
    document_type: str,
    prefix: str,
    start: int,
    aliases: tuple[str, ...] = (),
) -> str:
    document_types = (document_type, *aliases)
    existing_numbers = session.scalars(
        select(Document.document_number).where(Document.document_type.in_(document_types))
    ).all()
    return next_number_for_prefix(existing_numbers, prefix=prefix, start=start)


def next_number_for_prefix(existing_numbers: list[str], prefix: str, start: int) -> str:
    highest = start - 1
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    for number in existing_numbers:
        match = pattern.match(number.strip())
        if match is None:
            continue
        highest = max(highest, int(match.group(1)))
    return f"{prefix}-{highest + 1}"
