from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Customer, Document, Order, OrderLine, Product
from ..schemas import DocumentCreate, DocumentLineItem, OrderCreate
from .document_service import create_document


def create_order(session: Session, payload: OrderCreate) -> Order:
    customer = session.get(Customer, payload.customer_id)
    if customer is None:
        raise ValueError("Kunde wurde nicht gefunden.")

    order = Order(
        order_number=payload.order_number.strip(),
        customer_id=payload.customer_id,
        order_date=payload.order_date,
        delivery_date=payload.delivery_date,
        delivery_slot=payload.delivery_slot,
        tour_area=payload.tour_area,
        status=payload.status,
    )
    for line in payload.lines:
        product = session.get(Product, line.product_id)
        if product is None:
            raise ValueError("Produkt wurde nicht gefunden.")
        order.lines.append(
            OrderLine(
                product_id=product.id,
                product_name=product.name,
                quantity=line.quantity,
                unit_price_cents=(
                    line.unit_price_cents
                    if line.unit_price_cents is not None
                    else product.standard_price_cents
                ),
                deposit_cents=line.deposit_cents,
            )
        )

    session.add(order)
    session.commit()
    return get_order(session, order.id)


def get_order(session: Session, order_id: int) -> Order:
    order = session.scalar(
        select(Order)
        .options(selectinload(Order.lines), selectinload(Order.customer))
        .where(Order.id == order_id)
    )
    if order is None:
        raise ValueError("Auftrag wurde nicht gefunden.")
    return order


def list_active_orders(session: Session) -> list[Order]:
    return list(
        session.scalars(
            select(Order)
            .options(selectinload(Order.lines), selectinload(Order.customer))
            .where(Order.status != "archiviert")
            .order_by(Order.delivery_date, Order.delivery_slot, Order.order_number)
        )
    )


def archive_order(session: Session, order_id: int) -> Order:
    order = get_order(session, order_id)
    order.status = "archiviert"
    session.commit()
    return get_order(session, order_id)


def create_order_documents(
    session: Session,
    order_id: int,
    delivery_note_number: str,
    invoice_number: str,
    datev_upload_dir: Path | None = None,
) -> list[Document]:
    order = get_order(session, order_id)
    line_items = [
        DocumentLineItem(
            name=line.product_name,
            quantity=line.quantity,
            unit_price_cents=line.unit_price_cents,
            deposit_cents=line.deposit_cents,
        )
        for line in order.lines
    ]
    delivery_note = create_document(
        session,
        DocumentCreate(
            customer_id=order.customer_id,
            order_id=order.id,
            document_type="Lieferschein",
            document_number=delivery_note_number,
            delivery_date=order.delivery_date,
            delivery_slot=order.delivery_slot,
            line_items=line_items,
        ),
    )
    invoice = create_document(
        session,
        DocumentCreate(
            customer_id=order.customer_id,
            order_id=order.id,
            document_type="Rechnung",
            document_number=invoice_number,
            delivery_date=order.delivery_date,
            delivery_slot=order.delivery_slot,
            line_items=line_items,
        ),
        datev_upload_dir=datev_upload_dir,
    )
    order.status = "fakturiert"
    session.commit()
    session.refresh(delivery_note)
    session.refresh(invoice)
    return [delivery_note, invoice]
