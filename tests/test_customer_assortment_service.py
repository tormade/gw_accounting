from pathlib import Path

from sqlalchemy import select

from getraenkeladen_tool.models import Customer, CustomerAssortmentItem, Order, OrderLine, Product
from getraenkeladen_tool.services.checklist_service import resolve_price_mismatch
from getraenkeladen_tool.services.customer_assortment_service import (
    build_reorder_template,
    list_customer_assortment,
    list_customer_assortment_with_order_fallback,
)
from getraenkeladen_tool.services.master_data_import_service import import_master_data_from_folder
from getraenkeladen_tool.services.onboarding_service import onboard_customer_from_sources


INPUT_DIR = Path("/Users/thomasrumel/Documents/Codex/2026-06-20/Input")


def test_list_customer_assortment_returns_last_quantities_and_current_product_prices(session):
    import_master_data_from_folder(session, INPUT_DIR)
    result = onboard_customer_from_sources(
        session,
        customer_name="Metzgerei Karl",
        customer_list_path=INPUT_DIR / "Lieferkunden Liste.xlsx",
        workbook_path=INPUT_DIR / "_ RE 0525 Metzgerei Karl .xlsx",
    )

    rows = list_customer_assortment(session, result.customer.id)

    assert len(rows) == 16
    frucade = next(row for row in rows if row.source_product_name == "Frucade Colamix 20x0,5")
    assert frucade.product_id is not None
    assert frucade.product_name == "Frucade Colamix 20x0,5"
    assert frucade.last_quantity == 3
    assert frucade.excel_price_cents == 1048
    assert frucade.current_price_cents == 1190
    assert frucade.current_deposit_cents == 310
    assert frucade.price_differs_from_central is True
    assert frucade.price_decision == "offen"
    assert frucade.needs_review is True

    unresolved = next(row for row in rows if row.source_product_name == "Labert. ACE 20x0,5")
    assert unresolved.product_name is None
    assert unresolved.last_quantity == 0
    assert unresolved.excel_price_cents == 1698
    assert unresolved.current_price_cents == 1698
    assert unresolved.current_deposit_cents == 310
    assert unresolved.price_differs_from_central is False
    assert unresolved.needs_review is True


def test_customer_assortment_uses_resolved_excel_price_decision(session):
    import_master_data_from_folder(session, INPUT_DIR)
    result = onboard_customer_from_sources(
        session,
        customer_name="Metzgerei Karl",
        customer_list_path=INPUT_DIR / "Lieferkunden Liste.xlsx",
        workbook_path=INPUT_DIR / "_ RE 0525 Metzgerei Karl .xlsx",
    )
    price_issue = next(issue for issue in result.issues if issue.issue_type == "price_mismatch")

    resolve_price_mismatch(session, price_issue.id, "excel_preis")
    rows = list_customer_assortment(session, result.customer.id)

    frucade = next(row for row in rows if row.source_product_name == "Frucade Colamix 20x0,5")
    assert frucade.current_price_cents == 1048
    assert frucade.current_deposit_cents == 310
    assert frucade.price_decision == "excel_preis"
    assert frucade.price_differs_from_central is True
    assert frucade.needs_review is False

    item = session.scalar(
        select(CustomerAssortmentItem).where(CustomerAssortmentItem.source_product_name == "Frucade Colamix 20x0,5")
    )
    assert item.price_decision == "excel_preis"


def test_build_reorder_template_marks_empty_lines_and_price_review_rows(session):
    import_master_data_from_folder(session, INPUT_DIR)
    result = onboard_customer_from_sources(
        session,
        customer_name="Metzgerei Karl",
        customer_list_path=INPUT_DIR / "Lieferkunden Liste.xlsx",
        workbook_path=INPUT_DIR / "_ RE 0525 Metzgerei Karl .xlsx",
    )

    template = build_reorder_template(session, result.customer.id)

    assert template.customer_id == result.customer.id
    assert template.total_lines == 16
    assert template.quantity_lines == 6
    assert template.empty_lines == 10
    assert template.review_lines >= 1
    empty_line = next(line for line in template.lines if line.source_product_name == "Labert. ACE 20x0,5")
    assert empty_line.suggested_quantity == 0
    assert empty_line.quantity_state == "leer"
    frucade = next(line for line in template.lines if line.source_product_name == "Frucade Colamix 20x0,5")
    assert frucade.suggested_quantity == 3
    assert frucade.quantity_state == "letzte_menge"
    assert frucade.needs_review is True


def test_customer_assortment_falls_back_to_latest_order_when_no_assortment_exists(session):
    customer = Customer(name="Cafe Nord", folder_path="/tmp/Cafe Nord", is_active=True)
    water = Product(
        name="Adelholzener Wasser 12x0,7",
        unit="Kiste",
        standard_price_cents=890,
        default_deposit_cents=330,
        is_active=True,
    )
    spezi = Product(
        name="Paulaner Spezi 20x0,5",
        unit="Kiste",
        standard_price_cents=1490,
        default_deposit_cents=310,
        is_active=True,
    )
    session.add_all([customer, water, spezi])
    session.flush()
    session.add(
        Order(
            order_number="ALT-1",
            customer_id=customer.id,
            order_date="2026-07-01",
            delivery_date="2026-07-01",
            status="geplant",
            lines=[
                OrderLine(
                    product_id=water.id,
                    product_name=water.name,
                    quantity=4,
                    unit_price_cents=890,
                    deposit_cents=330,
                ),
                OrderLine(
                    product_id=spezi.id,
                    product_name=spezi.name,
                    quantity=0,
                    unit_price_cents=1490,
                    deposit_cents=310,
                ),
            ],
        )
    )
    session.commit()

    rows = list_customer_assortment_with_order_fallback(session, customer.id)

    assert [row.source_product_name for row in rows] == [water.name, spezi.name]
    assert [row.last_quantity for row in rows] == [4, 0]
    assert rows[0].current_price_cents == 890
    assert rows[0].current_deposit_cents == 330
    assert rows[0].price_warning_text == "aus letzter Bestellung"
    assert rows[0].needs_review is False
