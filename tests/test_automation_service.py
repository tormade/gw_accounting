from pathlib import Path

from getraenkeladen_tool.models import CustomerAssortmentItem, OnboardingIssue
from getraenkeladen_tool.schemas import CustomerCreate, DocumentCreate, DocumentLineItem, OrderCreate, OrderLineCreate, ProductCreate
from getraenkeladen_tool.services.automation_service import (
    find_duplicate_risks,
    get_customer_quickstart,
    list_customer_folder_excel_previews,
    list_customer_folder_updates,
    list_customer_price_deviations,
    list_document_sequence_issues,
    list_month_end_checks,
    list_work_cockpit_items,
    payment_hint_preview,
    suggest_typical_order_lines,
    validate_order_before_save,
    verify_document_assets,
)
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.document_service import create_document
from getraenkeladen_tool.services.order_service import create_order
from getraenkeladen_tool.services.product_service import create_product


def test_customer_quickstart_suggests_last_order_open_items_and_folder(session, tmp_path: Path):
    folder = tmp_path / "Kunden" / "Cafe Nord"
    folder.mkdir(parents=True)
    customer = create_customer(
        session,
        CustomerCreate(name="Cafe Nord", folder_path=str(folder), payment_method="Ueberweisung"),
    )
    product = create_product(session, ProductCreate(name="Wasser", unit="Kiste", standard_price_cents=1000))
    order = create_order(
        session,
        OrderCreate(
            order_number="BEST-1",
            customer_id=customer.id,
            order_date="2026-07-01",
            delivery_date="2026-07-02",
            lines=[OrderLineCreate(product_id=product.id, quantity=2)],
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            order_id=order.id,
            document_type="Rechnung",
            document_number="RE-1",
            delivery_date="2026-07-02",
            line_items=[DocumentLineItem(name="Wasser", quantity=2, unit_price_cents=1000)],
        ),
    )

    quickstart = get_customer_quickstart(session, customer.id)

    assert quickstart.customer_name == "Cafe Nord"
    assert quickstart.folder_exists is True
    assert quickstart.latest_order_number == "BEST-1"
    assert quickstart.open_invoice_numbers == ("RE-1",)
    assert "Letzte Bestellung BEST-1 oeffnen" in quickstart.suggestions


def test_duplicate_risks_warn_for_similar_customer_product_and_document(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Metzgerei Karl", folder_path=str(tmp_path / "Karl")))
    product = create_product(session, ProductCreate(name="Frucade Colamix 20x0,5", unit="Kiste", standard_price_cents=1048))
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RE-0525",
            line_items=[DocumentLineItem(name=product.name, quantity=1, unit_price_cents=1048)],
        ),
    )

    risks = find_duplicate_risks(session, customer_name="Metzgerei Carl", product_name="Frucade Cola Mix", document_number="RE 0525")

    assert ("customer", "Metzgerei Karl") in [(risk.entity_type, risk.existing_label) for risk in risks]
    assert ("product", "Frucade Colamix 20x0,5") in [(risk.entity_type, risk.existing_label) for risk in risks]
    assert ("document", "RE-0525") in [(risk.entity_type, risk.existing_label) for risk in risks]


def test_validate_order_before_save_flags_plausibility_risks(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "Cafe")))
    product = create_product(
        session,
        ProductCreate(name="Spezi", unit="Kiste", standard_price_cents=900, default_deposit_cents=310),
    )
    create_order(
        session,
        OrderCreate(
            order_number="BEST-1",
            customer_id=customer.id,
            order_date="2026-07-01",
            delivery_date="2026-07-02",
            lines=[OrderLineCreate(product_id=product.id, quantity=1, deposit_cents=310)],
        ),
    )
    payload = OrderCreate(
        order_number="BEST-1",
        customer_id=customer.id,
        order_date="2026-07-01",
        delivery_date="2026-07-02",
        lines=[OrderLineCreate(product_id=product.id, quantity=150, unit_price_cents=0, deposit_cents=0)],
    )

    warnings = validate_order_before_save(session, payload)

    codes = {warning.code for warning in warnings}
    assert {"duplicate_order_number", "high_quantity", "zero_price", "deposit_mismatch"} <= codes


def test_verify_document_assets_reports_missing_files(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "Cafe")))
    document = create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RE-1",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1000)],
        ),
    )
    Path(document.pdf_path).unlink()

    result = verify_document_assets(session, document.id)

    assert result.ok is False
    assert any(check.code == "missing_pdf" for check in result.checks)
    assert any(check.code == "snapshot_total" for check in result.checks)


def test_customer_folder_updates_find_new_excel_files_not_in_documents(session, tmp_path: Path):
    folder = tmp_path / "Kunden" / "Cafe"
    folder.mkdir(parents=True)
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(folder)))
    (folder / "neue kundenliste.xlsx").write_text("dummy", encoding="utf-8")
    (folder / "~$temp.xlsx").write_text("dummy", encoding="utf-8")

    updates = list_customer_folder_updates(session, customer.id)

    assert [path.name for path in updates] == ["neue kundenliste.xlsx"]


def test_payment_hint_preview_matches_customer_payment_method(session, tmp_path: Path):
    transfer = create_customer(
        session,
        CustomerCreate(name="Ueberweiser", folder_path=str(tmp_path / "U"), payment_method="Ueberweisung"),
    )
    sepa = create_customer(session, CustomerCreate(name="Sepa Kunde", folder_path=str(tmp_path / "S"), payment_method="SEPA"))

    assert payment_hint_preview(session, transfer.id, "2026-07-05").due_date == "2026-07-12"
    assert "ueberweisen" in payment_hint_preview(session, transfer.id, "2026-07-05").footer_text
    assert "Lastschrift" in payment_hint_preview(session, sepa.id, "2026-07-05").footer_text


def test_month_end_checks_report_missing_assets_and_overdue_open_items(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "Cafe"), payment_method="Ueberweisung"),
    )
    document = create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RE-1",
            delivery_date="2026-07-01",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1000)],
        ),
    )
    Path(document.pdf_path).unlink()

    checks = list_month_end_checks(session, month="2026-07", today="2026-07-20")

    assert any(check.code == "overdue_open_item" for check in checks)
    assert any(check.code == "missing_pdf" for check in checks)


def test_typical_order_lines_use_recent_customer_orders(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "Cafe")))
    water = create_product(session, ProductCreate(name="Wasser", unit="Kiste", standard_price_cents=1000))
    spezi = create_product(session, ProductCreate(name="Spezi", unit="Kiste", standard_price_cents=900))
    for index, water_quantity in enumerate((2, 4, 6), start=1):
        create_order(
            session,
            OrderCreate(
                order_number=f"BEST-{index}",
                customer_id=customer.id,
                order_date=f"2026-07-0{index}",
                delivery_date=f"2026-07-0{index}",
                lines=[
                    OrderLineCreate(product_id=water.id, quantity=water_quantity),
                    OrderLineCreate(product_id=spezi.id, quantity=1),
                ],
            ),
        )

    suggestions = suggest_typical_order_lines(session, customer.id)

    assert [(line.product_name, line.suggested_quantity) for line in suggestions] == [("Wasser", 4), ("Spezi", 1)]


def test_work_cockpit_collects_conflicts_missing_folder_and_missing_email(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "fehlt")))
    session.add(
        CustomerAssortmentItem(
            customer_id=customer.id,
            product_id=None,
            source_product_name="Unklarer Artikel",
            last_quantity=1,
        )
    )
    session.add(
        OnboardingIssue(
            customer_name=customer.name,
            source_file="kunde.xlsx",
            issue_type="product_match",
            field_name="Artikel",
            folder_value="Unklarer Artikel",
            list_value="",
            message="Artikel konnte nicht sicher zugeordnet werden.",
            status="offen",
            created_at="2026-07-05",
        )
    )
    session.commit()

    items = list_work_cockpit_items(session)

    codes = {item.code for item in items}
    assert {"open_checklist_issue", "missing_customer_folder", "missing_contact_email", "unresolved_customer_article"} <= codes


def test_validate_order_before_save_flags_incomplete_orders_before_documents(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "Cafe")))
    product = create_product(session, ProductCreate(name="Wasser", unit="Kiste", standard_price_cents=1000, default_deposit_cents=310))
    payload = OrderCreate(
        order_number="BEST-1",
        customer_id=customer.id,
        order_date="2026-07-05",
        delivery_date="2026-07-05",
        lines=[OrderLineCreate(product_id=product.id, quantity=0, unit_price_cents=1000, deposit_cents=310)],
    )

    warnings = validate_order_before_save(session, payload)

    codes = {warning.code for warning in warnings}
    assert {"missing_customer_address", "missing_customer_payment_method", "no_positive_quantity"} <= codes


def test_document_sequence_issues_find_missing_invoice_and_duplicate_documents(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "Cafe")))
    product = create_product(session, ProductCreate(name="Wasser", unit="Kiste", standard_price_cents=1000))
    order = create_order(
        session,
        OrderCreate(
            order_number="BEST-1",
            customer_id=customer.id,
            order_date="2026-07-05",
            delivery_date="2026-07-05",
            lines=[OrderLineCreate(product_id=product.id, quantity=1)],
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            order_id=order.id,
            document_type="Lieferschein",
            document_number="LS-1",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1000)],
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            order_id=order.id,
            document_type="Lieferschein",
            document_number="LS-2",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1000)],
        ),
    )

    issues = list_document_sequence_issues(session)

    codes = {issue.code for issue in issues}
    assert {"missing_invoice_after_delivery_note", "duplicate_delivery_note_for_order"} <= codes


def test_customer_folder_excel_preview_shows_probable_document_context(session, tmp_path: Path):
    from openpyxl import Workbook

    folder = tmp_path / "Kunden" / "Cafe"
    folder.mkdir(parents=True)
    file_path = folder / "RE-777 Cafe Nord.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet["A1"] = "Re. Nr."
    sheet["B1"] = "RE-777"
    sheet["A2"] = "05.07.2026"
    sheet["A10"] = "Wasser"
    sheet["B10"] = 2
    sheet["C10"] = 10.0
    workbook.save(file_path)
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(folder)))

    previews = list_customer_folder_excel_previews(session, customer.id)

    assert [(preview.path.name, preview.document_number, preview.document_date) for preview in previews] == [
        ("RE-777 Cafe Nord.xlsx", "RE-777", "2026-07-05")
    ]
    assert previews[0].filled_quantity_rows == 1


def test_typical_order_lines_include_last_range_and_frequency(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "Cafe")))
    water = create_product(session, ProductCreate(name="Wasser", unit="Kiste", standard_price_cents=1000))
    spezi = create_product(session, ProductCreate(name="Spezi", unit="Kiste", standard_price_cents=900))
    for index, water_quantity in enumerate((2, 4, 8), start=1):
        lines = [OrderLineCreate(product_id=water.id, quantity=water_quantity)]
        if index != 2:
            lines.append(OrderLineCreate(product_id=spezi.id, quantity=1))
        create_order(
            session,
            OrderCreate(
                order_number=f"BEST-{index}",
                customer_id=customer.id,
                order_date=f"2026-07-0{index}",
                delivery_date=f"2026-07-0{index}",
                lines=lines,
            ),
        )

    suggestions = suggest_typical_order_lines(session, customer.id)

    water_suggestion = next(line for line in suggestions if line.product_name == "Wasser")
    spezi_suggestion = next(line for line in suggestions if line.product_name == "Spezi")
    assert water_suggestion.last_quantity == 8
    assert water_suggestion.min_quantity == 2
    assert water_suggestion.max_quantity == 8
    assert water_suggestion.frequency_label == "meistens bestellt"
    assert spezi_suggestion.frequency_label == "manchmal bestellt"


def test_customer_price_deviations_list_customer_price_against_master_price(session, tmp_path: Path):
    customer = create_customer(session, CustomerCreate(name="Cafe Nord", folder_path=str(tmp_path / "Cafe")))
    product = create_product(session, ProductCreate(name="Wasser", unit="Kiste", standard_price_cents=1000, default_deposit_cents=310))
    session.add(
        CustomerAssortmentItem(
            customer_id=customer.id,
            product_id=product.id,
            source_product_name=product.name,
            last_quantity=2,
            last_unit_price_cents=1200,
            last_deposit_cents=310,
            price_decision="offen",
        )
    )
    session.commit()

    deviations = list_customer_price_deviations(session, customer.id)

    assert [(item.product_name, item.customer_price_cents, item.master_price_cents, item.decision) for item in deviations] == [
        ("Wasser", 1200, 1000, "offen")
    ]
