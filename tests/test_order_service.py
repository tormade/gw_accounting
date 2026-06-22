from pathlib import Path

from getraenkeladen_tool.models import Document, OpenItem
from openpyxl import load_workbook

from getraenkeladen_tool.schemas import CustomerCreate, DepositReturnCreate, OrderCreate, OrderLineCreate, ProductCreate
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.order_service import (
    archive_order,
    create_order,
    create_order_delivery_order,
    create_order_documents,
    create_order_invoice,
    get_order,
    list_active_orders,
    update_order,
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


def test_create_order_tracks_deposit_returns(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Verein", folder_path=str(tmp_path / "Verein")))
    product = create_product(session, ProductCreate(name="Wasser", unit="Kiste", standard_price_cents=1030))

    order = create_order(
        session,
        OrderCreate(
            order_number="AUF-1010",
            customer_id=customer.id,
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            lines=[OrderLineCreate(product_id=product.id, quantity=1, deposit_cents=480)],
            deposit_returns=[DepositReturnCreate(name="Leergut Kiste 4,80", quantity=2, deposit_cents=480)],
        ),
    )

    loaded = get_order(session, order.id)

    assert len(loaded.deposit_returns) == 1
    assert loaded.deposit_returns[0].name == "Leergut Kiste 4,80"
    assert loaded.deposit_returns[0].quantity == 2
    assert loaded.deposit_returns[0].deposit_cents == 480


def test_update_order_replaces_header_and_lines(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Hotel Blau", folder_path=str(tmp_path / "Hotel Blau")))
    water = create_product(session, ProductCreate(name="Wasser", unit="Kiste", standard_price_cents=1299))
    spezi = create_product(session, ProductCreate(name="Spezi", unit="Kiste", standard_price_cents=1599))
    order = create_order(
        session,
        OrderCreate(
            order_number="AUF-1006",
            customer_id=customer.id,
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            delivery_slot="vormittag",
            lines=[OrderLineCreate(product_id=water.id, quantity=1)],
        ),
    )

    updated = update_order(
        session,
        order.id,
        OrderCreate(
            order_number="AUF-1006-A",
            customer_id=customer.id,
            order_date="2026-06-23",
            delivery_date="2026-06-24",
            delivery_slot="nachmittag",
            lines=[OrderLineCreate(product_id=spezi.id, quantity=5, unit_price_cents=1499, deposit_cents=330)],
            deposit_returns=[DepositReturnCreate(name="Leergut Kiste 3,30", quantity=1, deposit_cents=330)],
        ),
    )

    assert updated.order_number == "AUF-1006-A"
    assert updated.delivery_date == "2026-06-24"
    assert updated.delivery_slot == "nachmittag"
    assert len(updated.lines) == 1
    assert updated.lines[0].product_id == spezi.id
    assert updated.lines[0].product_name == "Spezi"
    assert updated.lines[0].quantity == 5
    assert updated.lines[0].unit_price_cents == 1499
    assert updated.lines[0].deposit_cents == 330
    assert len(updated.deposit_returns) == 1
    assert updated.deposit_returns[0].name == "Leergut Kiste 3,30"


def test_update_order_keeps_existing_document_status_by_default(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Hotel Gruen", folder_path=str(tmp_path / "Hotel Gruen")))
    product = create_product(session, ProductCreate(name="Wasser", unit="Kiste", standard_price_cents=1299))
    order = create_order(
        session,
        OrderCreate(
            order_number="AUF-1007",
            customer_id=customer.id,
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            lines=[OrderLineCreate(product_id=product.id, quantity=1)],
        ),
    )
    create_order_delivery_order(session, order.id, "LS-1007")

    updated = update_order(
        session,
        order.id,
        OrderCreate(
            order_number="AUF-1007",
            customer_id=customer.id,
            order_date="2026-06-21",
            delivery_date="2026-06-23",
            lines=[OrderLineCreate(product_id=product.id, quantity=2)],
        ),
    )

    assert updated.status == "lieferauftrag_erstellt"


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

    assert [document.document_type for document in documents] == ["Lieferauftrag", "Rechnung"]
    assert [document.order_id for document in documents] == [order.id, order.id]
    assert Path(documents[0].excel_path).exists()
    assert Path(documents[1].pdf_path).exists()
    assert documents[1].datev_export_path is not None
    assert get_order(session, order.id).status == "fakturiert"


def test_create_order_delivery_order_generates_only_ls_document(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(name="Gasthof Nord", folder_path=str(tmp_path / "Kunden" / "Gasthof Nord")),
    )
    product = create_product(
        session,
        ProductCreate(name="Wasser 12x0,7", unit="Kiste", standard_price_cents=1299),
    )
    order = create_order(
        session,
        OrderCreate(
            order_number="AUF-3101",
            customer_id=customer.id,
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            lines=[OrderLineCreate(product_id=product.id, quantity=2, deposit_cents=330)],
        ),
    )

    document = create_order_delivery_order(session, order.id, "LS-3101")

    assert document.document_type == "Lieferauftrag"
    assert document.document_number == "LS-3101"
    assert document.order_id == order.id
    assert Path(document.excel_path).exists()
    assert Path(document.pdf_path).exists()
    assert session.query(Document).count() == 1
    assert get_order(session, order.id).status == "lieferauftrag_erstellt"


def test_create_order_invoice_generates_only_invoice_and_open_item(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Gasthof West",
            folder_path=str(tmp_path / "Kunden" / "Gasthof West"),
            payment_method="SEPA",
        ),
    )
    product = create_product(
        session,
        ProductCreate(name="Spezi 20x0,5", unit="Kiste", standard_price_cents=1599),
    )
    order = create_order(
        session,
        OrderCreate(
            order_number="AUF-3201",
            customer_id=customer.id,
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            lines=[OrderLineCreate(product_id=product.id, quantity=3, deposit_cents=330)],
            deposit_returns=[DepositReturnCreate(name="Leergut Kiste 3,30", quantity=1, deposit_cents=330)],
        ),
    )

    document = create_order_invoice(session, order.id, "RG-3201", datev_upload_dir=tmp_path / "DATEV")

    assert document.document_type == "Rechnung"
    assert document.document_number == "RG-3201"
    assert document.order_id == order.id
    assert Path(document.excel_path).exists()
    assert Path(document.pdf_path).exists()
    assert document.datev_export_path is not None
    assert session.query(Document).count() == 1
    assert session.query(OpenItem).one().amount_cents == 5457
    assert get_order(session, order.id).status == "fakturiert"

    excel_sheet = load_workbook(document.excel_path, data_only=True).active
    assert excel_sheet["F40"].value == -3.3
    assert excel_sheet["F43"].value == 54.57


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


def test_archive_order_hides_order_from_active_list(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "Cafe Nord")))
    product = create_product(session, ProductCreate(name="Wasser", unit="Kiste", standard_price_cents=1299))
    order = create_order(
        session,
        OrderCreate(
            order_number="AUF-2001",
            customer_id=customer.id,
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            lines=[OrderLineCreate(product_id=product.id, quantity=1)],
        ),
    )

    archived = archive_order(session, order.id)

    assert archived.status == "archiviert"
    assert list_active_orders(session) == []
