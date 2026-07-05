from pathlib import Path

from sqlalchemy import select

from getraenkeladen_tool.models import CustomerAssortmentItem, OnboardingIssue, ProductAlias
from getraenkeladen_tool.services.onboarding_service import (
    analyze_customer_workbook,
    onboard_customer_from_sources,
    onboard_customer_workbook_folder,
)
from getraenkeladen_tool.services.master_data_import_service import import_master_data_from_folder
from getraenkeladen_tool.services.checklist_service import resolve_price_mismatch


INPUT_DIR = Path("/Users/thomasrumel/Documents/Codex/2026-06-20/Input")


def test_agent_instructions_and_progress_queue_capture_onboarding_loop():
    agents = Path("AGENTS.md").read_text(encoding="utf-8")
    progress = Path("FORTSCHRITT.md").read_text(encoding="utf-8")

    assert "je-Kunde-Excel im Ordner ist die operative Wahrheit" in agents
    assert "Plan -> Entwickeln -> Testen -> Review -> Debuggen -> Anwender-Smoke -> Commit -> Checkpoint" in agents
    assert "Onboarding-/Migrations-Tool" in progress
    assert "Golden-File-Tests" in progress


def test_customer_workbook_parser_reads_metzgerei_karl_by_content_not_position():
    snapshot = analyze_customer_workbook(INPUT_DIR / "_ RE 0525 Metzgerei Karl .xlsx")

    assert snapshot.customer_name == "Metzgerei Karl"
    assert snapshot.address == "Moosburger Str. 55, 85406 Zolling"
    assert snapshot.contact_email == "rechnungen-metzgereikarl@outlook.de"
    assert snapshot.phone == "08167 9890720, 15.00 bis 18.00 Uhr"
    assert snapshot.payment_method == "SEPA"
    assert snapshot.document_number == "2606196"
    assert snapshot.document_date == "2026-06-10"
    assert snapshot.quantity_total == 16
    assert snapshot.delivery_fee_cents == 0
    assert snapshot.delivery_total_cents == 23428
    assert snapshot.deposit_return_total_cents == -4790
    assert snapshot.gross_total_cents == 18638
    assert snapshot.net_total_cents == 15662
    assert snapshot.tax_total_cents == 2976
    assert snapshot.lines[0].name == "Labertaler Apfelschorle 20x0,5"
    assert snapshot.lines[1].name == "Frucade Colamix 20x0,5"
    assert snapshot.lines[1].quantity == 3
    assert snapshot.lines[1].deposit_cents == 310
    assert snapshot.lines[1].unit_price_cents == 1048
    assert snapshot.lines[1].total_cents == 4074


def test_customer_workbook_parser_reads_lieferschein_comment_and_footer_text():
    snapshot = analyze_customer_workbook(INPUT_DIR / "_ LS 0525 Metzgerei Karl .xlsx")

    assert snapshot.customer_name == "Metzgerei Karl"
    assert snapshot.document_date == "2026-06-22"
    assert snapshot.delivery_comment == "bis13Uhr und ab 15 Uhr"
    assert snapshot.footer_text == "Die Ware bleibt bis zur vollständigen Bezahlung Eigentum von Getränke Winklmeier."
    assert snapshot.payment_method is None
    assert snapshot.quantity_total == 15
    assert snapshot.delivery_total_cents == 19870


def test_customer_workbook_parser_reads_overweisung_due_date_from_footer():
    snapshot = analyze_customer_workbook(INPUT_DIR / "Privat Rechnung überweiser.xlsx")

    assert snapshot.customer_name == "Max Huber"
    assert snapshot.address == "Max-Planck-Straße 13, 85716 Unterschleißheim"
    assert snapshot.contact_email == "linas.civinskas@adc-distribution.de"
    assert snapshot.phone == "089 552 634 0"
    assert snapshot.payment_method == "Überweisung"
    assert snapshot.document_number == "2606298"
    assert snapshot.document_date == "2026-06-11"
    assert snapshot.due_date == "2026-06-18"
    assert snapshot.quantity_total == 10
    assert snapshot.delivery_total_cents == 15720


def test_onboarding_merges_folder_operational_truth_with_customer_list_and_keeps_conflicts(session):
    import_master_data_from_folder(session, INPUT_DIR)

    result = onboard_customer_from_sources(
        session,
        customer_name="Metzgerei Karl",
        customer_list_path=INPUT_DIR / "Lieferkunden Liste.xlsx",
        workbook_path=INPUT_DIR / "_ RE 0525 Metzgerei Karl .xlsx",
    )

    assert result.customer.name == "Metzgerei Karl"
    assert result.customer.payment_method == "SEPA"
    assert result.customer.next_contact_date == "2026-07-06"
    assert result.customer.contact_email == "rechnungen-metzgereikarl@outlook.de"
    assert result.customer.address == "Moosburger Str 5, 85406 Zolling"
    assert result.snapshot.quantity_total == 16
    assert result.report.customers_read == 1
    assert result.report.assortment_lines == 16
    assert result.report.conflicts >= 2
    assert result.report.unreadable_files == 0

    issues = list(session.scalars(select(OnboardingIssue).order_by(OnboardingIssue.id)))
    issue_fields = {issue.field_name for issue in issues}
    assert "address" in issue_fields
    assert "phone" in issue_fields
    assert all(issue.status == "offen" for issue in issues)


def test_onboarding_builds_customer_assortment_and_product_aliases(session):
    import_master_data_from_folder(session, INPUT_DIR)

    result = onboard_customer_from_sources(
        session,
        customer_name="Metzgerei Karl",
        customer_list_path=INPUT_DIR / "Lieferkunden Liste.xlsx",
        workbook_path=INPUT_DIR / "_ RE 0525 Metzgerei Karl .xlsx",
    )

    assortment = list(
        session.scalars(
            select(CustomerAssortmentItem)
            .where(CustomerAssortmentItem.customer_id == result.customer.id)
            .order_by(CustomerAssortmentItem.sort_order)
        )
    )
    assert len(assortment) == 16
    frucade = next(item for item in assortment if item.source_product_name == "Frucade Colamix 20x0,5")
    assert frucade.product is not None
    assert frucade.product.name == "Frucade Colamix 20x0,5"
    assert frucade.last_quantity == 3
    assert frucade.last_unit_price_cents == 1048
    assert frucade.last_deposit_cents == 310
    assert frucade.price_decision == "offen"
    assert frucade.is_active is True

    alias = session.scalar(select(ProductAlias).where(ProductAlias.alias == "Frucade Colamix 20x0,5"))
    assert alias is not None
    assert alias.product_id == frucade.product_id
    assert alias.status == "bestaetigt"

    unresolved = next(item for item in assortment if item.source_product_name == "Labert. ACE 20x0,5")
    assert unresolved.product_id is None
    product_issues = list(
        session.scalars(
            select(OnboardingIssue)
            .where(OnboardingIssue.issue_type == "product_match")
            .order_by(OnboardingIssue.id)
        )
    )
    assert any("Labert. ACE 20x0,5" in issue.folder_value for issue in product_issues if issue.folder_value)

    price_issues = list(
        session.scalars(
            select(OnboardingIssue)
            .where(OnboardingIssue.issue_type == "price_mismatch")
            .order_by(OnboardingIssue.id)
        )
    )
    assert any("Frucade Colamix 20x0,5" in issue.folder_value for issue in price_issues if issue.folder_value)
    assert any("10,48" in issue.folder_value and "11,90" in issue.list_value for issue in price_issues)


def test_re_onboarding_keeps_resolved_price_decisions_and_does_not_duplicate_issues(session):
    import_master_data_from_folder(session, INPUT_DIR)
    first_result = onboard_customer_from_sources(
        session,
        customer_name="Metzgerei Karl",
        customer_list_path=INPUT_DIR / "Lieferkunden Liste.xlsx",
        workbook_path=INPUT_DIR / "_ RE 0525 Metzgerei Karl .xlsx",
    )
    frucade_issue = session.scalar(
        select(OnboardingIssue)
        .where(OnboardingIssue.issue_type == "price_mismatch")
        .where(OnboardingIssue.folder_value.like("%Frucade Colamix 20x0,5%"))
    )
    resolve_price_mismatch(session, frucade_issue.id, "excel_preis")

    onboard_customer_from_sources(
        session,
        customer_name="Metzgerei Karl",
        customer_list_path=INPUT_DIR / "Lieferkunden Liste.xlsx",
        workbook_path=INPUT_DIR / "_ RE 0525 Metzgerei Karl .xlsx",
    )

    frucade_item = session.scalar(
        select(CustomerAssortmentItem)
        .where(CustomerAssortmentItem.customer_id == first_result.customer.id)
        .where(CustomerAssortmentItem.source_product_name == "Frucade Colamix 20x0,5")
    )
    frucade_issues = list(
        session.scalars(
            select(OnboardingIssue)
            .where(OnboardingIssue.issue_type == "price_mismatch")
            .where(OnboardingIssue.folder_value.like("%Frucade Colamix 20x0,5%"))
        )
    )

    assert frucade_item.price_decision == "excel_preis"
    assert len(frucade_issues) == 1
    assert frucade_issues[0].status == "erledigt"


def test_folder_onboarding_reports_readable_customers_and_skips_outliers(session, tmp_path):
    import_master_data_from_folder(session, INPUT_DIR)

    customer_dir = tmp_path / "Kundenordner"
    customer_dir.mkdir()
    readable = customer_dir / "_ RE 0525 Metzgerei Karl .xlsx"
    readable.write_bytes((INPUT_DIR / "_ RE 0525 Metzgerei Karl .xlsx").read_bytes())
    unreadable = customer_dir / "defekt.xlsx"
    unreadable.write_text("keine echte Excel-Datei", encoding="utf-8")

    result = onboard_customer_workbook_folder(
        session,
        customer_list_path=INPUT_DIR / "Lieferkunden Liste.xlsx",
        folder_path=customer_dir,
    )

    assert result.report.customers_read == 1
    assert result.report.assortment_lines == 16
    assert result.report.conflicts >= 2
    assert result.report.unreadable_files == 1
    assert result.results[0].customer.name == "Metzgerei Karl"
    assert result.skipped_files[0].path == unreadable
    assert "defekt.xlsx" in result.skipped_files[0].message
