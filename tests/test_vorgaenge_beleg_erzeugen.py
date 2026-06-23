from pathlib import Path

from getraenkeladen_tool.schemas import CustomerCreate, DocumentCreate, DocumentLineItem
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.vorgaenge.beleg_erzeugen import beleg_erzeugen


def test_beleg_erzeugen_is_application_entrypoint_for_document_creation(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(name="Vorgang Kunde", folder_path=str(tmp_path / "Kunden" / "Vorgang Kunde")),
    )

    document = beleg_erzeugen(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RG-V-1",
            delivery_date="2026-06-23",
            line_items=[DocumentLineItem(name="Wasser", quantity=2, unit_price_cents=1000, deposit_cents=330)],
        ),
    )

    assert document.document_number == "RG-V-1"
    assert Path(document.excel_path).exists()
    assert Path(document.pdf_path).exists()
