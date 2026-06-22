from dataclasses import dataclass
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Document, NumberSequence, Order


@dataclass(frozen=True)
class NumberSuggestions:
    order_number: str
    delivery_note_number: str
    invoice_number: str


@dataclass(frozen=True)
class NumberSequenceStatus:
    sequence_key: str
    label: str
    prefix: str
    next_number: str


SEQUENCE_DEFINITIONS = {
    "order": {"label": "Auftrag", "prefix": "AUF", "start": 1001},
    "delivery_note": {"label": "Lieferschein", "prefix": "LS", "start": 3001},
    "invoice": {"label": "Rechnung", "prefix": "RG", "start": 3001},
}


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
    return _next_number_with_manual_floor(
        session,
        sequence_key="order",
        existing_numbers=existing_numbers,
        prefix="AUF",
        start=1001,
    )


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
    sequence_key = _sequence_key_for_prefix(prefix)
    return _next_number_with_manual_floor(
        session,
        sequence_key=sequence_key,
        existing_numbers=existing_numbers,
        prefix=prefix,
        start=start,
    )


def list_number_sequence_statuses(session: Session) -> list[NumberSequenceStatus]:
    suggestions = suggest_next_numbers(session)
    next_numbers = {
        "order": suggestions.order_number,
        "delivery_note": suggestions.delivery_note_number,
        "invoice": suggestions.invoice_number,
    }
    return [
        NumberSequenceStatus(
            sequence_key=sequence_key,
            label=str(definition["label"]),
            prefix=str(definition["prefix"]),
            next_number=next_numbers[sequence_key],
        )
        for sequence_key, definition in SEQUENCE_DEFINITIONS.items()
    ]


def set_next_number(session: Session, sequence_key: str, prefix: str, value: str) -> NumberSequence:
    clean_value = value.strip().upper()
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    match = pattern.match(clean_value)
    if match is None:
        raise ValueError(f"Nummer muss dem Format {prefix}-1234 entsprechen.")
    next_number = int(match.group(1))
    sequence = session.scalar(
        select(NumberSequence).where(NumberSequence.sequence_key == sequence_key).limit(1)
    )
    if sequence is None:
        sequence = NumberSequence(sequence_key=sequence_key, prefix=prefix, next_number=next_number)
        session.add(sequence)
    else:
        sequence.prefix = prefix
        sequence.next_number = next_number
    session.commit()
    session.refresh(sequence)
    return sequence


def next_number_for_prefix(existing_numbers: list[str], prefix: str, start: int) -> str:
    highest = start - 1
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    for number in existing_numbers:
        match = pattern.match(number.strip())
        if match is None:
            continue
        highest = max(highest, int(match.group(1)))
    return f"{prefix}-{highest + 1}"


def _next_number_with_manual_floor(
    session: Session,
    sequence_key: str,
    existing_numbers: list[str],
    prefix: str,
    start: int,
) -> str:
    automatic_next = next_number_for_prefix(existing_numbers, prefix=prefix, start=start)
    automatic_value = int(automatic_next.split("-")[1])
    sequence = session.scalar(
        select(NumberSequence).where(NumberSequence.sequence_key == sequence_key).limit(1)
    )
    manual_value = sequence.next_number if sequence is not None else start
    return f"{prefix}-{max(automatic_value, manual_value)}"


def _sequence_key_for_prefix(prefix: str) -> str:
    for sequence_key, definition in SEQUENCE_DEFINITIONS.items():
        if definition["prefix"] == prefix:
            return sequence_key
    return prefix.lower()
