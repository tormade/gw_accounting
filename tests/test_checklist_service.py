from sqlalchemy import select

from getraenkeladen_tool.models import OnboardingIssue
from getraenkeladen_tool.services.checklist_service import (
    list_checklist_issues,
    mark_issue_resolved,
    reopen_issue,
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
