from sqlalchemy import select
from sqlalchemy.orm import Session
from pathlib import Path

from ..models import Customer, Document, OpenItem
from .file_service import ensure_parent_folder


def list_open_items(session: Session) -> list[OpenItem]:
    return list(
        session.scalars(
            select(OpenItem)
            .where(OpenItem.status == "offen")
            .order_by(OpenItem.customer_name, OpenItem.document_number)
        )
    )


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
            .order_by(Document.delivery_slot, Document.document_number)
        )
    )


def export_open_items_csv(session: Session, output_path: Path) -> Path:
    rows = [["Kunde", "Rechnungsnr.", "Betrag EUR", "Zahlungsart", "Status"]]
    for item in list_open_items(session):
        rows.append(
            [
                item.customer_name,
                item.document_number,
                _format_cents(item.amount_cents),
                item.payment_method,
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
