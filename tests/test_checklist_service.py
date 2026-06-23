from sqlalchemy import select

from getraenkeladen_tool.models import Customer, CustomerAssortmentItem, OnboardingIssue, Product, ProductAlias
from getraenkeladen_tool.services.checklist_service import (
    confirm_product_alias,
    list_checklist_issues,
    mark_issue_resolved,
    reopen_issue,
    resolve_price_mismatch,
)


def test_checklist_service_lists_open_issues_and_updates_status(session):
    issue = OnboardingIssue(
        customer_name="Metzgerei Karl",
        source_file="Input/_ RE 0525 Metzgerei Karl .xlsx",
        issue_type="price_mismatch",
        field_name="price",
        list_value="Zentral: 11,90 EUR",
        folder_value="Excel: 10,48 EUR",
        message="Preisabweichung gefunden.",
        status="offen",
        created_at="2026-06-23T10:00:00",
    )
    session.add(issue)
    session.commit()

    rows = list_checklist_issues(session)

    assert len(rows) == 1
    assert rows[0].customer_name == "Metzgerei Karl"
    assert rows[0].issue_type_label == "Preisabweichung"
    assert rows[0].status == "offen"

    mark_issue_resolved(session, rows[0].id)
    assert session.scalar(select(OnboardingIssue).where(OnboardingIssue.id == issue.id)).status == "erledigt"

    reopen_issue(session, rows[0].id)
    assert session.scalar(select(OnboardingIssue).where(OnboardingIssue.id == issue.id)).status == "offen"


def test_resolve_price_mismatch_stores_decision_on_customer_assortment(session):
    customer = Customer(name="Metzgerei Karl", folder_path="Kunden/Metzgerei Karl")
    product = Product(name="Frucade Colamix 20x0,5", unit="Kiste", standard_price_cents=1190, default_deposit_cents=310)
    session.add_all([customer, product])
    session.flush()
    item = CustomerAssortmentItem(
        customer_id=customer.id,
        product_id=product.id,
        source_product_name="Frucade Colamix 20x0,5",
        last_quantity=3,
        last_unit_price_cents=1048,
        last_deposit_cents=310,
        price_decision="offen",
    )
    issue = OnboardingIssue(
        customer_name="Metzgerei Karl",
        source_file="Input/_ RE 0525 Metzgerei Karl .xlsx",
        issue_type="price_mismatch",
        field_name="price",
        list_value="Frucade Colamix 20x0,5: zentraler Preis 11,90 EUR",
        folder_value="Frucade Colamix 20x0,5: Preis aus Excel 10,48 EUR",
        message="Preisabweichung gefunden.",
        status="offen",
        created_at="2026-06-23T10:00:00",
    )
    session.add_all([item, issue])
    session.commit()

    resolve_price_mismatch(session, issue.id, "excel_preis")

    session.refresh(item)
    session.refresh(issue)
    assert item.price_decision == "excel_preis"
    assert issue.status == "erledigt"


def test_confirm_product_alias_links_unmatched_assortment_and_alias(session):
    customer = Customer(name="Metzgerei Karl", folder_path="Kunden/Metzgerei Karl")
    product = Product(name="Labertaler ACE 20x0,5", unit="Kiste", standard_price_cents=1698, default_deposit_cents=310)
    session.add_all([customer, product])
    session.flush()
    item = CustomerAssortmentItem(
        customer_id=customer.id,
        product_id=None,
        source_product_name="Labert. ACE 20x0,5",
        last_quantity=1,
        last_unit_price_cents=1698,
        last_deposit_cents=310,
    )
    issue = OnboardingIssue(
        customer_name="Metzgerei Karl",
        source_file="Input/_ RE 0525 Metzgerei Karl .xlsx",
        issue_type="product_match",
        field_name="product",
        list_value=None,
        folder_value="Labert. ACE 20x0,5",
        message="Artikel konnte nicht sicher zugeordnet werden.",
        status="offen",
        created_at="2026-06-23T10:00:00",
    )
    session.add_all([item, issue])
    session.commit()

    confirm_product_alias(session, issue.id, product.id)

    session.refresh(item)
    session.refresh(issue)
    alias = session.scalar(select(ProductAlias).where(ProductAlias.alias == "Labert. ACE 20x0,5"))
    assert item.product_id == product.id
    assert issue.status == "erledigt"
    assert alias is not None
    assert alias.product_id == product.id
    assert alias.status == "bestaetigt"
