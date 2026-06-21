from pathlib import Path

from getraenkeladen_tool.schemas import CustomerCreate, DocumentCreate, DocumentLineItem
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.document_service import create_document
from getraenkeladen_tool.services.report_service import list_open_items, mark_open_item_paid


def test_list_open_items_and_mark_payment_received(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Cafe Nord",
            folder_path=str(tmp_path / "Kunden" / "Cafe Nord"),
            payment_method="Ueberweisung",
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RG-1004",
            line_items=[
                DocumentLineItem(
                    name="Wasser 0,7",
                    quantity=3,
                    unit_price_cents=1299,
                    deposit_cents=330,
                )
            ],
        ),
    )

    open_items = list_open_items(session)
    assert len(open_items) == 1
    assert open_items[0].customer_name == "Cafe Nord"
    assert open_items[0].document_number == "RG-1004"
    assert open_items[0].amount_cents == 4887
    assert open_items[0].status == "offen"

    paid_item = mark_open_item_paid(session, open_items[0].id)

    assert paid_item.status == "bezahlt"
    assert list_open_items(session) == []
