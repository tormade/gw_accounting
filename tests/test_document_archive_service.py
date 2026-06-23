from pathlib import Path

from getraenkeladen_tool.schemas import (
    CustomerCreate,
    DepositReturnCreate,
    DocumentCreate,
    DocumentLineItem,
    OrderCreate,
    OrderLineCreate,
    ProductCreate,
)
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.document_archive_service import list_documents_by_type
from getraenkeladen_tool.services.document_archive_service import regenerate_document_asset
from getraenkeladen_tool.services.document_service import create_document
from getraenkeladen_tool.services.order_service import create_order, create_order_invoice
from getraenkeladen_tool.services.product_service import create_product


def test_list_documents_by_type_returns_existing_invoices_with_customer_and_paths(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Cafe Nord",
            folder_path=str(tmp_path / "Kunden" / "Cafe Nord"),
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RG-1001",
            delivery_date="2026-06-21",
            line_items=[DocumentLineItem(name="Wasser", quantity=2, unit_price_cents=1299)],
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Lieferschein",
            document_number="LS-1001",
            delivery_date="2026-06-21",
            line_items=[DocumentLineItem(name="Wasser", quantity=2, unit_price_cents=1299)],
        ),
    )

    invoices = list_documents_by_type(session, "Rechnung")

    assert len(invoices) == 1
    assert invoices[0].document_number == "RG-1001"
    assert invoices[0].customer.name == "Cafe Nord"
    assert Path(invoices[0].excel_path).exists()
    assert Path(invoices[0].pdf_path).exists()


def test_list_documents_by_type_hides_released_numbers_and_sorts_newest_first(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Gasthof Sued",
            folder_path=str(tmp_path / "Kunden" / "Gasthof Sued"),
        ),
    )
    older = create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Lieferschein",
            document_number="LS-1001",
            delivery_date="2026-06-20",
            line_items=[DocumentLineItem(name="Limo", quantity=1, unit_price_cents=1200)],
        ),
    )
    newer = create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Lieferschein",
            document_number="LS-1002",
            delivery_date="2026-06-22",
            line_items=[DocumentLineItem(name="Spezi", quantity=1, unit_price_cents=1400)],
        ),
    )
    released = create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Lieferschein",
            document_number="LS-1003",
            delivery_date="2026-06-23",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1000)],
        ),
    )
    released.number_released = True
    session.commit()

    delivery_notes = list_documents_by_type(session, "Lieferschein")

    assert [document.document_number for document in delivery_notes] == [newer.document_number, older.document_number]


def test_regenerate_document_asset_recreates_missing_pdf_with_existing_document_number(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Cafe Nord",
            folder_path=str(tmp_path / "Kunden" / "Cafe Nord"),
        ),
    )
    product = create_product(
        session,
        ProductCreate(name="Wasser", unit="Kiste", standard_price_cents=1299),
    )
    order = create_order(
        session,
        OrderCreate(
            customer_id=customer.id,
            order_number="AUF-2001",
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            lines=[OrderLineCreate(product_id=product.id, quantity=1, unit_price_cents=1299)],
        ),
    )
    document = create_order_invoice(
        session,
        order.id,
        "RG-2001",
        assets={"excel"},
    )
    pdf_path = Path(document.pdf_path)
    assert not pdf_path.exists()

    regenerated = regenerate_document_asset(session, document.id, "pdf")

    assert regenerated.document_number == "RG-2001"
    assert pdf_path.exists()


def test_regenerate_document_asset_uses_existing_excel_snapshot_not_changed_order(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Cafe Nord",
            folder_path=str(tmp_path / "Kunden" / "Cafe Nord"),
        ),
    )
    product = create_product(
        session,
        ProductCreate(name="Wasser Original", unit="Kiste", standard_price_cents=1299),
    )
    order = create_order(
        session,
        OrderCreate(
            customer_id=customer.id,
            order_number="AUF-2002",
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            lines=[OrderLineCreate(product_id=product.id, quantity=1, unit_price_cents=1299)],
        ),
    )
    document = create_order_invoice(session, order.id, "RG-2002", assets={"excel"})
    order.lines[0].product_name = "Nachtraeglich geaendert"
    session.commit()

    regenerate_document_asset(session, document.id, "pdf")

    pdf_text = Path(document.pdf_path).read_bytes().decode("latin-1")
    assert "Wasser Original" in pdf_text
    assert "Nachtraeglich geaendert" not in pdf_text


def test_regenerate_document_asset_reads_first_deposit_return_row_from_excel_snapshot(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Cafe Nord",
            folder_path=str(tmp_path / "Kunden" / "Cafe Nord"),
        ),
    )
    product = create_product(
        session,
        ProductCreate(name="Wasser Original", unit="Kiste", standard_price_cents=1299),
    )
    order = create_order(
        session,
        OrderCreate(
            customer_id=customer.id,
            order_number="AUF-2003",
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            lines=[OrderLineCreate(product_id=product.id, quantity=1, unit_price_cents=1299, deposit_cents=330)],
            deposit_returns=[DepositReturnCreate(name="Leergut Kiste 3,30", quantity=1, deposit_cents=330)],
        ),
    )
    document = create_order_invoice(session, order.id, "RG-2003", assets={"excel"})

    regenerate_document_asset(session, document.id, "pdf")

    pdf_text = Path(document.pdf_path).read_bytes().decode("latin-1")
    assert "Leergut Kiste 3,30" in pdf_text
    assert "-3,30 EUR" in pdf_text


def test_regenerate_document_asset_refuses_excel_recreation_without_safe_snapshot(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Cafe Nord",
            folder_path=str(tmp_path / "Kunden" / "Cafe Nord"),
        ),
    )
    document = create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Lieferschein",
            document_number="LS-2001",
            delivery_date="2026-06-22",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1299)],
        ),
        assets={"excel"},
    )

    try:
        regenerate_document_asset(session, document.id, "excel")
    except ValueError as error:
        assert "Excel-Datei kann nicht sicher automatisch neu erzeugt" in str(error)
    else:
        raise AssertionError("Excel-Nacherzeugung ohne sicheren Snapshot muss fehlschlagen.")
