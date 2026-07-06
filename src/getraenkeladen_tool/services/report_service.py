from sqlalchemy import select
from sqlalchemy.orm import Session
from pathlib import Path
from dataclasses import dataclass

from ..models import Customer, Document, OpenItem, Order
from .file_service import ensure_parent_folder


@dataclass(frozen=True)
class DashboardSummary:
    target_date: str
    delivery_count: int
    open_item_count: int
    due_contact_count: int
    next_steps: tuple[str, str, str]


@dataclass(frozen=True, slots=True)
class InvoiceWorkItem:
    id: int
    customer_name: str
    document_number: str
    document_date: str | None
    due_date: str | None
    amount_cents: int
    payment_method: str
    status: str
    status_bucket: str


@dataclass(frozen=True, slots=True)
class DeliveryReturnWorkItem:
    order_id: int
    order_number: str
    customer_name: str
    delivery_date: str
    delivery_slot: str | None
    delivery_note_number: str


@dataclass(frozen=True, slots=True)
class CustomerInvoiceWarning:
    open_count: int
    due_count: int
    overdue_count: int
    amount_cents: int


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


def list_invoice_worklist(session: Session, status_filter: str = "offen", target_date: str | None = None) -> list[InvoiceWorkItem]:
    statement = select(OpenItem).order_by(OpenItem.due_date, OpenItem.customer_name, OpenItem.document_number)
    if status_filter != "bezahlt":
        statement = statement.where(OpenItem.status != "bezahlt")
    items = sorted(
        (_invoice_work_item(item, target_date) for item in session.scalars(statement)),
        key=_invoice_sort_key,
    )
    if status_filter == "alle":
        return items
    return [item for item in items if item.status_bucket == status_filter or item.status == status_filter]


def get_customer_invoice_warning(session: Session, customer_name: str, target_date: str | None = None) -> CustomerInvoiceWarning:
    items = list(
        session.scalars(
            select(OpenItem)
            .where(OpenItem.customer_name == customer_name)
            .where(OpenItem.status != "bezahlt")
            .order_by(OpenItem.due_date, OpenItem.document_number)
        )
    )
    due_count = 0
    overdue_count = 0
    if target_date:
        for item in items:
            if item.due_date == target_date:
                due_count += 1
            elif item.due_date and item.due_date < target_date:
                overdue_count += 1
    return CustomerInvoiceWarning(
        open_count=len(items),
        due_count=due_count,
        overdue_count=overdue_count,
        amount_cents=sum(item.amount_cents for item in items),
    )


def list_open_delivery_returns(session: Session) -> list[DeliveryReturnWorkItem]:
    orders = session.scalars(
        select(Order)
        .where(Order.status == "lieferauftrag_erstellt")
        .order_by(Order.delivery_date, Order.delivery_slot, Order.customer_id, Order.order_number)
    )
    items: list[DeliveryReturnWorkItem] = []
    for order in orders:
        invoice_exists = session.scalar(
            select(Document.id)
            .where(Document.order_id == order.id)
            .where(Document.document_type == "Rechnung")
            .limit(1)
        )
        if invoice_exists is not None:
            continue
        delivery_note = session.scalar(
            select(Document)
            .where(Document.order_id == order.id)
            .where(Document.document_type == "Lieferschein")
            .order_by(Document.id.desc())
            .limit(1)
        )
        if delivery_note is None:
            continue
        items.append(
            DeliveryReturnWorkItem(
                order_id=order.id,
                order_number=order.order_number,
                customer_name=order.customer.name,
                delivery_date=order.delivery_date,
                delivery_slot=order.delivery_slot,
                delivery_note_number=delivery_note.document_number,
            )
        )
    return items


def mark_open_item_paid(session: Session, open_item_id: int) -> OpenItem:
    open_item = session.get(OpenItem, open_item_id)
    if open_item is None:
        raise ValueError("Offener Posten wurde nicht gefunden.")

    open_item.status = "bezahlt"
    session.commit()
    session.refresh(open_item)
    return open_item


def mark_open_item_partially_paid(session: Session, open_item_id: int) -> OpenItem:
    open_item = session.get(OpenItem, open_item_id)
    if open_item is None:
        raise ValueError("Offener Posten wurde nicht gefunden.")

    open_item.status = "teilbezahlt"
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


def _invoice_work_item(item: OpenItem, target_date: str | None) -> InvoiceWorkItem:
    return InvoiceWorkItem(
        id=item.id,
        customer_name=item.customer_name,
        document_number=item.document_number,
        document_date=item.document_date,
        due_date=item.due_date,
        amount_cents=item.amount_cents,
        payment_method=item.payment_method,
        status=item.status,
        status_bucket=_invoice_status_bucket(item, target_date),
    )


def _invoice_status_bucket(item: OpenItem, target_date: str | None) -> str:
    if item.status == "teilbezahlt":
        return "teilbezahlt"
    if item.status == "bezahlt":
        return "bezahlt"
    if item.due_date and target_date:
        if item.due_date < target_date:
            return "ueberfaellig"
        if item.due_date == target_date:
            return "faellig"
    return "offen"


def _invoice_sort_key(item: InvoiceWorkItem) -> tuple[int, str, str, str]:
    priority = {
        "ueberfaellig": 0,
        "faellig": 1,
        "teilbezahlt": 2,
        "offen": 3,
        "bezahlt": 4,
    }.get(item.status_bucket, 9)
    return (priority, item.due_date or "9999-12-31", item.customer_name, item.document_number)


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
