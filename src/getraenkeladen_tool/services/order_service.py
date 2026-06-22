from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Customer, Document, Order, OrderDepositReturn, OrderLine, Product
from ..schemas import DepositReturnCreate, DocumentCreate, DocumentLineItem, OrderCreate
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
    _append_deposit_returns(order, payload.deposit_returns)

    session.add(order)
    session.commit()
    return get_order(session, order.id)


def update_order(session: Session, order_id: int, payload: OrderCreate) -> Order:
    customer = session.get(Customer, payload.customer_id)
    if customer is None:
        raise ValueError("Kunde wurde nicht gefunden.")

    order = get_order(session, order_id)
    order.order_number = payload.order_number.strip()
    order.customer_id = payload.customer_id
    order.order_date = payload.order_date
    order.delivery_date = payload.delivery_date
    order.delivery_slot = payload.delivery_slot
    order.tour_area = payload.tour_area
    if order.status == "geplant" or payload.status != "geplant":
        order.status = payload.status
    order.lines.clear()
    order.deposit_returns.clear()

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
    _append_deposit_returns(order, payload.deposit_returns)

    session.commit()
    return get_order(session, order.id)


def get_order(session: Session, order_id: int) -> Order:
    order = session.scalar(
        select(Order)
        .options(selectinload(Order.lines), selectinload(Order.deposit_returns), selectinload(Order.customer))
        .where(Order.id == order_id)
    )
    if order is None:
        raise ValueError("Auftrag wurde nicht gefunden.")
    return order


def list_active_orders(session: Session, customer_id: int | None = None) -> list[Order]:
    query = (
        select(Order)
        .options(selectinload(Order.lines), selectinload(Order.deposit_returns), selectinload(Order.customer))
        .where(Order.status != "archiviert")
        .order_by(Order.delivery_date, Order.delivery_slot, Order.order_number)
    )
    if customer_id is not None:
        query = query.where(Order.customer_id == customer_id)
    return list(session.scalars(query))


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
    delivery_order = create_order_delivery_order(session, order_id, delivery_note_number)
    invoice = create_order_invoice(session, order_id, invoice_number, datev_upload_dir=datev_upload_dir)
    return [delivery_order, invoice]


def create_order_delivery_order(
    session: Session,
    order_id: int,
    delivery_order_number: str,
    line_items: list[DocumentLineItem] | None = None,
    deposit_returns: list[DepositReturnCreate] | None = None,
    assets: set[str] | None = None,
) -> Document:
    order = get_order(session, order_id)
    delivery_order = create_document(
        session,
        DocumentCreate(
            customer_id=order.customer_id,
            order_id=order.id,
            document_type="Lieferauftrag",
            document_number=delivery_order_number,
            delivery_date=order.delivery_date,
            delivery_slot=order.delivery_slot,
            line_items=line_items if line_items is not None else _document_line_items(order),
            deposit_returns=deposit_returns if deposit_returns is not None else _document_deposit_returns(order),
        ),
        assets=assets,
    )
    if order.status != "fakturiert":
        order.status = "lieferauftrag_erstellt"
        session.commit()
    session.refresh(delivery_order)
    return delivery_order


def create_order_invoice(
    session: Session,
    order_id: int,
    invoice_number: str,
    line_items: list[DocumentLineItem] | None = None,
    deposit_returns: list[DepositReturnCreate] | None = None,
    datev_upload_dir: Path | None = None,
    assets: set[str] | None = None,
) -> Document:
    order = get_order(session, order_id)
    invoice = create_document(
        session,
        DocumentCreate(
            customer_id=order.customer_id,
            order_id=order.id,
            document_type="Rechnung",
            document_number=invoice_number,
            delivery_date=order.delivery_date,
            delivery_slot=order.delivery_slot,
            line_items=line_items if line_items is not None else _document_line_items(order),
            deposit_returns=deposit_returns if deposit_returns is not None else _document_deposit_returns(order),
        ),
        datev_upload_dir=datev_upload_dir,
        assets=assets,
    )
    order.status = "fakturiert"
    session.commit()
    session.refresh(invoice)
    return invoice


def _document_line_items(order: Order) -> list[DocumentLineItem]:
    return [
        DocumentLineItem(
            name=line.product_name,
            quantity=line.quantity,
            unit_price_cents=line.unit_price_cents,
            deposit_cents=line.deposit_cents,
        )
        for line in order.lines
    ]


def _document_deposit_returns(order: Order) -> list[DepositReturnCreate]:
    return [
        DepositReturnCreate(
            name=deposit_return.name,
            quantity=deposit_return.quantity,
            deposit_cents=deposit_return.deposit_cents,
        )
        for deposit_return in order.deposit_returns
    ]


def _append_deposit_returns(order: Order, deposit_returns: list[DepositReturnCreate]) -> None:
    for deposit_return in deposit_returns:
        order.deposit_returns.append(
            OrderDepositReturn(
                name=deposit_return.name,
                quantity=deposit_return.quantity,
                deposit_cents=deposit_return.deposit_cents,
            )
        )
