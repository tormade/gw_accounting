from pathlib import Path

from sqlalchemy import select

from getraenkeladen_tool.models import CustomerAssortmentItem
from getraenkeladen_tool.services.checklist_service import resolve_price_mismatch
from getraenkeladen_tool.services.customer_assortment_service import list_customer_assortment
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
