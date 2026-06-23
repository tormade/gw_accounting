from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import CustomerAssortmentItem


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


def _row_from_item(item: CustomerAssortmentItem) -> CustomerAssortmentRow:
    product = item.product
    price_differs = (
        product is not None
        and (
            product.standard_price_cents != item.last_unit_price_cents
            or product.default_deposit_cents != item.last_deposit_cents
        )
    )
    return CustomerAssortmentRow(
        id=item.id,
        product_id=item.product_id,
        source_product_name=item.source_product_name,
        product_name=product.name if product is not None else None,
        last_quantity=item.last_quantity,
        excel_price_cents=item.last_unit_price_cents,
        excel_deposit_cents=item.last_deposit_cents,
        current_price_cents=product.standard_price_cents if product is not None else item.last_unit_price_cents,
        current_deposit_cents=product.default_deposit_cents if product is not None else item.last_deposit_cents,
        price_decision=item.price_decision or "offen",
        price_differs_from_central=price_differs,
        price_warning_text=_price_warning_text(item) if price_differs else None,
        sort_order=item.sort_order,
        needs_review=product is None or price_differs,
    )


def _price_warning_text(item: CustomerAssortmentItem) -> str:
    product = item.product
    if product is None:
        return ""
    return (
        f"Excel-Preis {item.last_unit_price_cents / 100:.2f} EUR, "
        f"zentraler Preis {product.standard_price_cents / 100:.2f} EUR."
    ).replace(".", ",")
