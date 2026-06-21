from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Customer, Document, OpenItem


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
