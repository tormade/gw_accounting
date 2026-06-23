from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import OnboardingIssue


ISSUE_TYPE_LABELS = {
    "price_mismatch": "Preisabweichung",
    "product_match": "Artikelzuordnung",
    "customer_conflict": "Kundendaten",
    "folder_scan": "Ordnerpruefung",
}


@dataclass(frozen=True, slots=True)
class ChecklistIssueRow:
    id: int
    customer_name: str
    issue_type: str
    issue_type_label: str
    field_name: str
    list_value: str
    folder_value: str
    message: str
    status: str
    created_at: str


def list_checklist_issues(session: Session, include_done: bool = False) -> list[ChecklistIssueRow]:
    statement = select(OnboardingIssue).order_by(OnboardingIssue.status, OnboardingIssue.customer_name, OnboardingIssue.id)
    if not include_done:
        statement = statement.where(OnboardingIssue.status != "erledigt")
    issues = list(session.scalars(statement))
    return [_row_from_issue(issue) for issue in issues]


def mark_issue_resolved(session: Session, issue_id: int) -> OnboardingIssue:
    return _set_issue_status(session, issue_id, "erledigt")


def reopen_issue(session: Session, issue_id: int) -> OnboardingIssue:
    return _set_issue_status(session, issue_id, "offen")


def _set_issue_status(session: Session, issue_id: int, status: str) -> OnboardingIssue:
    issue = session.get(OnboardingIssue, issue_id)
    if issue is None:
        raise ValueError("Pruefpunkt wurde nicht gefunden.")
    issue.status = status
    session.commit()
    session.refresh(issue)
    return issue


def _row_from_issue(issue: OnboardingIssue) -> ChecklistIssueRow:
    return ChecklistIssueRow(
        id=issue.id,
        customer_name=issue.customer_name,
        issue_type=issue.issue_type,
        issue_type_label=ISSUE_TYPE_LABELS.get(issue.issue_type, issue.issue_type),
        field_name=issue.field_name,
        list_value=issue.list_value or "",
        folder_value=issue.folder_value or "",
        message=issue.message,
        status=issue.status,
        created_at=issue.created_at,
    )
