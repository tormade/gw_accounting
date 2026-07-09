from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import CustomerAssortmentItem, Order, OrderLine


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
    last_order_date: str | None
    order_count: int
    total_quantity: int
    sales_hint: str


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
    rows_by_key = {_row_key(row.product_id, row.source_product_name): row for row in (_row_from_item(item) for item in items)}
    for history_row in _history_rows(session, customer_id):
        key = _row_key(history_row.product_id, history_row.source_product_name)
        existing = rows_by_key.get(key)
        rows_by_key[key] = _merge_history(existing, history_row) if existing is not None else history_row
    return sorted(rows_by_key.values(), key=_assortment_sort_key)


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
        last_order_date=None,
        order_count=0,
        total_quantity=0,
        sales_hint="aus Kunden-Excel",
    )


def _price_warning_text(item: CustomerAssortmentItem) -> str:
    product = item.product
    if product is None:
        return ""
    return (
        f"Excel-Preis {item.last_unit_price_cents / 100:.2f} EUR, "
        f"zentraler Preis {product.standard_price_cents / 100:.2f} EUR."
    ).replace(".", ",")


def _history_rows(session: Session, customer_id: int) -> list[CustomerAssortmentRow]:
    order_lines = list(
        session.execute(
            select(OrderLine, Order)
            .join(Order, Order.id == OrderLine.order_id)
            .options(selectinload(OrderLine.product))
            .where(Order.customer_id == customer_id)
            .where(Order.number_released == False)  # noqa: E712
            .order_by(Order.delivery_date.asc(), Order.id.asc(), OrderLine.id.asc())
        )
    )
    history = {}
    for line, order in order_lines:
        key = _row_key(line.product_id, line.product_name)
        product = line.product
        item = history.setdefault(
            key,
            {
                "product_id": line.product_id,
                "source_product_name": line.product_name,
                "product_name": product.name if product is not None else line.product_name,
                "last_quantity": line.quantity,
                "last_order_date": order.delivery_date,
                "order_count": 0,
                "total_quantity": 0,
                "unit_price_cents": line.unit_price_cents,
                "deposit_cents": line.deposit_cents,
                "current_price_cents": product.standard_price_cents if product is not None else line.unit_price_cents,
                "current_deposit_cents": product.default_deposit_cents if product is not None else line.deposit_cents,
                "price_differs_from_central": False,
            },
        )
        item["order_count"] += 1
        item["total_quantity"] += line.quantity
        if order.delivery_date >= item["last_order_date"]:
            item["last_quantity"] = line.quantity
            item["last_order_date"] = order.delivery_date
            item["unit_price_cents"] = line.unit_price_cents
            item["deposit_cents"] = line.deposit_cents
        item["price_differs_from_central"] = (
            product is not None
            and (
                product.standard_price_cents != item["unit_price_cents"]
                or product.default_deposit_cents != item["deposit_cents"]
            )
        )

    return [
        CustomerAssortmentRow(
            id=0,
            product_id=item["product_id"],
            source_product_name=item["source_product_name"],
            product_name=item["product_name"],
            last_quantity=item["last_quantity"],
            excel_price_cents=item["unit_price_cents"],
            excel_deposit_cents=item["deposit_cents"],
            current_price_cents=item["current_price_cents"],
            current_deposit_cents=item["current_deposit_cents"],
            price_decision="zentraler_preis",
            price_differs_from_central=item["price_differs_from_central"],
            price_warning_text=None,
            sort_order=0,
            needs_review=False,
            last_order_date=item["last_order_date"],
            order_count=item["order_count"],
            total_quantity=item["total_quantity"],
            sales_hint=_sales_hint(item["order_count"]),
        )
        for item in history.values()
    ]


def _merge_history(existing: CustomerAssortmentRow, history_row: CustomerAssortmentRow) -> CustomerAssortmentRow:
    return CustomerAssortmentRow(
        id=existing.id,
        product_id=existing.product_id or history_row.product_id,
        source_product_name=existing.source_product_name,
        product_name=existing.product_name or history_row.product_name,
        last_quantity=history_row.last_quantity,
        excel_price_cents=existing.excel_price_cents,
        excel_deposit_cents=existing.excel_deposit_cents,
        current_price_cents=existing.current_price_cents,
        current_deposit_cents=existing.current_deposit_cents,
        price_decision=existing.price_decision,
        price_differs_from_central=existing.price_differs_from_central,
        price_warning_text=existing.price_warning_text,
        sort_order=existing.sort_order,
        needs_review=existing.needs_review,
        last_order_date=history_row.last_order_date,
        order_count=history_row.order_count,
        total_quantity=history_row.total_quantity,
        sales_hint=history_row.sales_hint,
    )


def _row_key(product_id: int | None, product_name: str) -> tuple[str, int | str]:
    if product_id is not None:
        return ("product", product_id)
    return ("name", product_name.strip().casefold())


def _assortment_sort_key(row: CustomerAssortmentRow) -> tuple[int, str, int, int, str]:
    has_history_rank = 0 if row.last_order_date else 1
    return (has_history_rank, _reverse_date(row.last_order_date), -row.order_count, row.sort_order, row.source_product_name)


def _reverse_date(value: str | None) -> str:
    if not value:
        return "9999-99-99"
    return "".join(str(9 - int(char)) if char.isdigit() else char for char in value)


def _sales_hint(order_count: int) -> str:
    if order_count >= 2:
        return "regelmaessig bestellt"
    return "schon mal bestellt"
