from pathlib import Path

from getraenkeladen_tool.models import Document
from getraenkeladen_tool.schemas import CustomerCreate, OrderCreate, OrderLineCreate, ProductCreate
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.order_service import (
    create_order,
    create_order_documents,
    get_order,
    list_active_orders,
)
from getraenkeladen_tool.services.product_service import create_product


def test_create_order_copies_product_prices_into_order_lines(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "Cafe Nord")))
    product = create_product(
        session,
        ProductCreate(
            name="Wasser 12x0,7",
            unit="Kiste",
            standard_price_cents=1299,
            article_number="W-070",
        ),
    )

    order = create_order(
        session,
        OrderCreate(
            order_number="AUF-1001",
            customer_id=customer.id,
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            delivery_slot="vormittag",
            tour_area="Nord",
            lines=[OrderLineCreate(product_id=product.id, quantity=10, deposit_cents=330)],
        ),
    )

    loaded = get_order(session, order.id)

    assert loaded.order_number == "AUF-1001"
    assert loaded.status == "geplant"
    assert loaded.lines[0].product_id == product.id
    assert loaded.lines[0].product_name == "Wasser 12x0,7"
    assert loaded.lines[0].unit_price_cents == 1299
    assert loaded.lines[0].deposit_cents == 330


def test_create_order_allows_price_override(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Hotel Blau", folder_path=str(tmp_path / "Hotel Blau")))
    product = create_product(
        session,
        ProductCreate(name="Helles 20x0,5", unit="Kiste", standard_price_cents=1899),
    )

    order = create_order(
        session,
        OrderCreate(
            order_number="AUF-1002",
            customer_id=customer.id,
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            lines=[OrderLineCreate(product_id=product.id, quantity=2, unit_price_cents=1799)],
        ),
    )

    assert order.lines[0].unit_price_cents == 1799


def test_create_order_documents_generates_delivery_note_and_invoice_from_same_order(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Gasthof Sued",
            folder_path=str(tmp_path / "Kunden" / "Gasthof Sued"),
            payment_method="SEPA",
        ),
    )
    product = create_product(
        session,
        ProductCreate(name="Apfelschorle 12x1,0", unit="Kiste", standard_price_cents=1499),
    )
    order = create_order(
        session,
        OrderCreate(
            order_number="AUF-1003",
            customer_id=customer.id,
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            delivery_slot="nachmittag",
            lines=[OrderLineCreate(product_id=product.id, quantity=3, deposit_cents=330)],
        ),
    )

    documents = create_order_documents(
        session,
        order_id=order.id,
        delivery_note_number="LS-3001",
        invoice_number="RG-3001",
        datev_upload_dir=tmp_path / "DATEV",
    )

    assert [document.document_type for document in documents] == ["Lieferschein", "Rechnung"]
    assert [document.order_id for document in documents] == [order.id, order.id]
    assert Path(documents[0].excel_path).exists()
    assert Path(documents[1].pdf_path).exists()
    assert documents[1].datev_export_path is not None
    assert get_order(session, order.id).status == "fakturiert"


def test_list_active_orders_excludes_archived_orders(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "Cafe Nord")))
    product = create_product(session, ProductCreate(name="Wasser", unit="Kiste", standard_price_cents=1299))
    active = create_order(
        session,
        OrderCreate(
            order_number="AUF-1004",
            customer_id=customer.id,
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            lines=[OrderLineCreate(product_id=product.id, quantity=1)],
        ),
    )
    archived = create_order(
        session,
        OrderCreate(
            order_number="AUF-1005",
            customer_id=customer.id,
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            status="archiviert",
            lines=[OrderLineCreate(product_id=product.id, quantity=1)],
        ),
    )

    orders = list_active_orders(session)

    assert orders == [active]
    assert archived not in orders
