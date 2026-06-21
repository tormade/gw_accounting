from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import OpenItem


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
