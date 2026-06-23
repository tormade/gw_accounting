from pathlib import Path

from getraenkeladen_tool.schemas import CustomerCreate, DocumentCreate, DocumentLineItem
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.document_archive_service import list_documents_by_type
from getraenkeladen_tool.services.document_service import create_document


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
