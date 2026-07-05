from getraenkeladen_tool.models import Order
from getraenkeladen_tool.schemas import CustomerCreate, DocumentCreate, DocumentLineItem
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.document_service import create_document
from getraenkeladen_tool.services.number_suggestion_service import (
    suggest_document_number,
    suggest_order_number,
)


def test_suggest_document_number_increments_latest_matching_number(session, tmp_path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "Cafe")))
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RE-0525",
            delivery_date="2026-07-05",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1000)],
        ),
    )

    assert suggest_document_number(session, "Rechnung", prefix="RE-") == "RE-0526"


def test_suggest_document_number_uses_date_fallback_when_no_numeric_suffix_exists(session):
    assert suggest_document_number(session, "Lieferschein", prefix="LS-", fallback_date="2026-07-05") == "LS-20260705-1"


def test_suggest_order_number_increments_latest_order_number(session):
    session.add(Order(order_number="AUF-1009", customer_id=1, order_date="2026-07-05", delivery_date="2026-07-05"))
    session.commit()

    assert suggest_order_number(session, prefix="AUF-") == "AUF-1010"
