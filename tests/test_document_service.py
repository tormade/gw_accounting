from pathlib import Path

from getraenkeladen_tool.models import OpenItem
from getraenkeladen_tool.schemas import CustomerCreate, DocumentCreate, DocumentLineItem
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.document_service import create_document


def test_create_invoice_writes_excel_file_and_open_item(session, tmp_path: Path):
    customer_folder = tmp_path / "Kunden" / "Cafe Nord"
    customer = create_customer(
        session,
        CustomerCreate(
            name="Cafe Nord",
            folder_path=str(customer_folder),
            payment_method="SEPA",
        ),
    )

    document = create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RG-1001",
            line_items=[
                DocumentLineItem(
                    name="Wasser 0,7",
                    quantity=10,
                    unit_price_cents=1299,
                    deposit_cents=330,
                )
            ],
        ),
    )

    excel_path = Path(document.excel_path)
    assert excel_path == customer_folder / "RG-1001_Rechnung.xlsx"
    assert excel_path.exists()

    open_item = session.query(OpenItem).one()
    assert open_item.customer_name == "Cafe Nord"
    assert open_item.document_number == "RG-1001"
    assert open_item.amount_cents == 16290
    assert open_item.payment_method == "SEPA"
    assert open_item.status == "offen"
