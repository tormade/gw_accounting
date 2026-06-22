from pathlib import Path

from getraenkeladen_tool.schemas import CustomerCreate, DocumentCreate, DocumentLineItem, OrderCreate, OrderLineCreate, ProductCreate
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.document_service import create_document
from getraenkeladen_tool.services.numbering_service import (
    NumberSuggestions,
    next_document_number,
    next_number_for_prefix,
    set_next_number,
    suggest_next_numbers,
)
from getraenkeladen_tool.services.order_service import create_order
from getraenkeladen_tool.services.product_service import create_product


def test_next_number_for_prefix_uses_default_when_no_numbers_exist():
    assert next_number_for_prefix([], prefix="RG", start=3001) == "RG-3001"


def test_next_number_for_prefix_continues_after_highest_matching_number():
    numbers = ["RG-3001", "RG-4500", "LS-9999", "RG-alt"]

    assert next_number_for_prefix(numbers, prefix="RG", start=3001) == "RG-4501"


def test_suggest_next_numbers_uses_database_orders_and_documents(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "Cafe Nord")))
    product = create_product(session, ProductCreate(name="Wasser", unit="Kiste", standard_price_cents=1299))
    create_order(
        session,
        OrderCreate(
            order_number="AUF-2500",
            customer_id=customer.id,
            order_date="2026-06-21",
            delivery_date="2026-06-22",
            lines=[OrderLineCreate(product_id=product.id, quantity=1)],
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Lieferschein",
            document_number="LS-4100",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1299)],
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RG-4500",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1299)],
        ),
    )

    assert suggest_next_numbers(session) == NumberSuggestions(
        order_number="AUF-2501",
        delivery_note_number="LS-4101",
        invoice_number="RG-4501",
    )


def test_suggest_next_numbers_counts_legacy_delivery_order_documents(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Alt", folder_path=str(tmp_path / "Cafe Alt")))
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Lieferauftrag",
            document_number="LS-4999",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1299)],
        ),
    )

    assert suggest_next_numbers(session).delivery_note_number == "LS-5000"


def test_next_document_number_returns_default_for_document_type_without_existing_documents(session):
    assert next_document_number(session, document_type="Rechnung", prefix="RG", start=3001) == "RG-3001"


def test_set_next_number_changes_future_suggestion_when_it_is_higher_than_existing(session):
    set_next_number(session, sequence_key="invoice", prefix="RG", value="RG-4100")

    assert suggest_next_numbers(session).invoice_number == "RG-4100"


def test_number_suggestion_can_go_below_higher_existing_documents_when_number_is_free(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nummer", folder_path=str(tmp_path / "Cafe Nummer")))
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RG-4100",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1299)],
        ),
    )
    set_next_number(session, sequence_key="invoice", prefix="RG", value="RG-3001")

    assert suggest_next_numbers(session).invoice_number == "RG-3001"


def test_manual_next_number_can_reset_to_free_lower_number(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Reset", folder_path=str(tmp_path / "Cafe Reset")))
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RG-4100",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1299)],
        ),
    )
    set_next_number(session, sequence_key="invoice", prefix="RG", value="RG-3001")

    assert suggest_next_numbers(session).invoice_number == "RG-3001"


def test_manual_next_number_skips_used_numbers_when_counting_forward(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Kollision", folder_path=str(tmp_path / "Cafe Kollision")))
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RG-3001",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1299)],
        ),
    )
    set_next_number(session, sequence_key="invoice", prefix="RG", value="RG-3001")

    assert suggest_next_numbers(session).invoice_number == "RG-3002"
