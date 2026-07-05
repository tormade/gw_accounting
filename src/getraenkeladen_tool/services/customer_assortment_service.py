from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import CustomerAssortmentItem, Order


@dataclass(frozen=True, slots=True)
class CustomerAssortmentRow:
    id: int
    product_id: int | None
    source_product_name: str
    product_name: str | None
    last_quantity: int
    excel_price_cents: int
    excel_deposit_cents: int
    current_price_cents: int
    current_deposit_cents: int
    price_decision: str
    price_differs_from_central: bool
    price_warning_text: str | None
    sort_order: int
    needs_review: bool


@dataclass(frozen=True, slots=True)
class ReorderTemplateLine:
    product_id: int | None
    source_product_name: str
    product_name: str | None
    suggested_quantity: int
    quantity_state: str
    unit_price_cents: int
    deposit_cents: int
    needs_review: bool
    warning_text: str | None


@dataclass(frozen=True, slots=True)
class ReorderTemplate:
    customer_id: int
    lines: tuple[ReorderTemplateLine, ...]

    @property
    def total_lines(self) -> int:
        return len(self.lines)

    @property
    def quantity_lines(self) -> int:
        return sum(1 for line in self.lines if line.suggested_quantity > 0)

    @property
    def empty_lines(self) -> int:
        return sum(1 for line in self.lines if line.suggested_quantity == 0)

    @property
    def review_lines(self) -> int:
        return sum(1 for line in self.lines if line.needs_review)


def list_customer_assortment(session: Session, customer_id: int) -> list[CustomerAssortmentRow]:
    items = list(
        session.scalars(
            select(CustomerAssortmentItem)
            .options(selectinload(CustomerAssortmentItem.product))
            .where(CustomerAssortmentItem.customer_id == customer_id)
            .where(CustomerAssortmentItem.is_active == True)  # noqa: E712
            .order_by(CustomerAssortmentItem.sort_order, CustomerAssortmentItem.source_product_name)
        )
    )
    return [_row_from_item(item) for item in items]


def list_customer_assortment_with_order_fallback(session: Session, customer_id: int) -> list[CustomerAssortmentRow]:
    rows = list_customer_assortment(session, customer_id)
    if rows:
        return rows
    latest_order = session.scalar(
        select(Order)
        .options(selectinload(Order.lines))
        .where(Order.customer_id == customer_id)
        .where(Order.status != "archiviert")
        .where(Order.number_released == False)  # noqa: E712
        .order_by(Order.delivery_date.desc(), Order.id.desc())
        .limit(1)
    )
    if latest_order is None:
        return []
    return [
        CustomerAssortmentRow(
            id=0,
            product_id=line.product_id,
            source_product_name=line.product_name,
            product_name=line.product_name,
            last_quantity=line.quantity,
            excel_price_cents=line.unit_price_cents,
            excel_deposit_cents=line.deposit_cents,
            current_price_cents=line.unit_price_cents,
            current_deposit_cents=line.deposit_cents,
            price_decision="letzte_bestellung",
            price_differs_from_central=False,
            price_warning_text="aus letzter Bestellung",
            sort_order=index,
            needs_review=line.product_id is None,
        )
        for index, line in enumerate(latest_order.lines, start=1)
    ]


def build_reorder_template(session: Session, customer_id: int) -> ReorderTemplate:
    rows = list_customer_assortment_with_order_fallback(session, customer_id)
    return ReorderTemplate(
        customer_id=customer_id,
        lines=tuple(_template_line_from_row(row) for row in rows),
    )


def _row_from_item(item: CustomerAssortmentItem) -> CustomerAssortmentRow:
    product = item.product
    price_differs = (
        product is not None
        and (
            product.standard_price_cents != item.last_unit_price_cents
            or product.default_deposit_cents != item.last_deposit_cents
        )
    )
    price_decision = item.price_decision or "offen"
    current_price_cents = product.standard_price_cents if product is not None else item.last_unit_price_cents
    current_deposit_cents = product.default_deposit_cents if product is not None else item.last_deposit_cents
    if product is not None and price_decision == "excel_preis":
        current_price_cents = item.last_unit_price_cents
        current_deposit_cents = item.last_deposit_cents
    return CustomerAssortmentRow(
        id=item.id,
        product_id=item.product_id,
        source_product_name=item.source_product_name,
        product_name=product.name if product is not None else None,
        last_quantity=item.last_quantity,
        excel_price_cents=item.last_unit_price_cents,
        excel_deposit_cents=item.last_deposit_cents,
        current_price_cents=current_price_cents,
        current_deposit_cents=current_deposit_cents,
        price_decision=price_decision,
        price_differs_from_central=price_differs,
        price_warning_text=_price_warning_text(item) if price_differs else None,
        sort_order=item.sort_order,
        needs_review=product is None or (price_differs and price_decision == "offen"),
    )


def _template_line_from_row(row: CustomerAssortmentRow) -> ReorderTemplateLine:
    return ReorderTemplateLine(
        product_id=row.product_id,
        source_product_name=row.source_product_name,
        product_name=row.product_name,
        suggested_quantity=row.last_quantity,
        quantity_state="letzte_menge" if row.last_quantity > 0 else "leer",
        unit_price_cents=row.current_price_cents,
        deposit_cents=row.current_deposit_cents,
        needs_review=row.needs_review,
        warning_text=row.price_warning_text or ("Artikel muss zugeordnet werden." if row.product_id is None else None),
    )


def _price_warning_text(item: CustomerAssortmentItem) -> str:
    product = item.product
    if product is None:
        return ""
    return (
        f"Excel-Preis {item.last_unit_price_cents / 100:.2f} EUR, "
        f"zentraler Preis {product.standard_price_cents / 100:.2f} EUR."
    ).replace(".", ",")
