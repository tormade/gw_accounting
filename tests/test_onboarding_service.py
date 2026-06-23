from pathlib import Path

from sqlalchemy import select

from getraenkeladen_tool.models import OnboardingIssue
from getraenkeladen_tool.services.onboarding_service import (
    analyze_customer_workbook,
    onboard_customer_from_sources,
)


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


def test_onboarding_merges_folder_operational_truth_with_customer_list_and_keeps_conflicts(session):
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
