from sqlalchemy import select
from sqlalchemy.orm import Session
from pathlib import Path
from dataclasses import dataclass

from ..models import Customer, Document, OpenItem
from .file_service import ensure_parent_folder


@dataclass(frozen=True)
class DashboardSummary:
    target_date: str
    delivery_count: int
    open_item_count: int
    due_contact_count: int
    next_steps: tuple[str, str, str]


def get_dashboard_summary(session: Session, target_date: str) -> DashboardSummary:
    return DashboardSummary(
        target_date=target_date,
        delivery_count=len(list_daily_deliveries(session, target_date)),
        open_item_count=len(list_open_items(session)),
        due_contact_count=len(list_due_contacts(session, target_date)),
        next_steps=(
            f"Lieferliste fuer {target_date} pruefen.",
            "Offene Posten kontrollieren und Zahlungseingaenge markieren.",
            "Faellige Kundenkontakte abarbeiten.",
        ),
    )


def list_open_items(session: Session, payment_method: str | None = None) -> list[OpenItem]:
    statement = (
        select(OpenItem)
        .where(OpenItem.status == "offen")
        .order_by(OpenItem.due_date, OpenItem.customer_name, OpenItem.document_number)
    )
    if payment_method:
        statement = statement.where(OpenItem.payment_method == payment_method)
    return list(session.scalars(statement))


def mark_open_item_paid(session: Session, open_item_id: int) -> OpenItem:
    open_item = session.get(OpenItem, open_item_id)
    if open_item is None:
        raise ValueError("Offener Posten wurde nicht gefunden.")

    open_item.status = "bezahlt"
    session.commit()
    session.refresh(open_item)
    return open_item


def list_due_contacts(session: Session, target_date: str) -> list[Customer]:
    return list(
        session.scalars(
            select(Customer)
            .where(Customer.next_contact_date == target_date)
            .order_by(Customer.name)
        )
    )


def list_daily_deliveries(session: Session, target_date: str) -> list[Document]:
    return list(
        session.scalars(
            select(Document)
            .where(Document.delivery_date == target_date)
            .where(Document.document_type == "Lieferschein")
            .where(Document.number_released == False)  # noqa: E712
            .order_by(Document.delivery_slot, Document.document_number)
        )
    )


def export_open_items_csv(session: Session, output_path: Path) -> Path:
    rows = [["Kunde", "Rechnungsnr.", "Rechnungsdatum", "Faelligkeit", "Zahlart", "Betrag EUR", "Status"]]
    for item in list_open_items(session):
        rows.append(
            [
                item.customer_name,
                item.document_number,
                item.document_date or "",
                item.due_date or "",
                item.payment_method,
                _format_cents(item.amount_cents),
                item.status,
            ]
        )
    return _write_csv(output_path, rows)


def export_daily_deliveries_csv(session: Session, target_date: str, output_path: Path) -> Path:
    rows = [["Datum", "Zeitfenster", "Belegnr.", "Kunde", "Adresse", "Hinweise", "Oeffnungszeiten"]]
    for document in list_daily_deliveries(session, target_date):
        rows.append(
            [
                document.delivery_date or "",
                document.delivery_slot or "",
                document.document_number,
                document.customer.name,
                document.customer.address or "",
                document.customer.delivery_notes or "",
                document.customer.opening_hours or "",
            ]
        )
    return _write_csv(output_path, rows)


def export_due_contacts_csv(session: Session, target_date: str, output_path: Path) -> Path:
    rows = [["Kontakttermin", "Kunde", "E-Mail", "Hinweise"]]
    for customer in list_due_contacts(session, target_date):
        rows.append(
            [
                customer.next_contact_date or "",
                customer.name,
                customer.contact_email or "",
                customer.delivery_notes or "",
            ]
        )
    return _write_csv(output_path, rows)


def _format_cents(value: int) -> str:
    return f"{value / 100:.2f}".replace(".", ",")


def _write_csv(output_path: Path, rows: list[list[str]]) -> Path:
    ensure_parent_folder(output_path)
    output_path.write_text(
        "\n".join(";".join(_escape_csv_cell(cell)) for cell in rows) + "\n",
        encoding="utf-8",
    )
    return output_path


def _escape_csv_cell(value: str) -> str:
    if any(character in value for character in ['"', ";", "\n"]):
        return '"' + value.replace('"', '""') + '"'
    return value
