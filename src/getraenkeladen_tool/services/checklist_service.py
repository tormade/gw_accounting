from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Customer, CustomerAssortmentItem, OnboardingIssue, Product, ProductAlias


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


def resolve_price_mismatch(session: Session, issue_id: int, decision: str) -> OnboardingIssue:
    if decision not in {"zentraler_preis", "excel_preis"}:
        raise ValueError("Preisentscheidung ist ungueltig.")
    issue = _issue_or_error(session, issue_id)
    if issue.issue_type != "price_mismatch":
        raise ValueError("Dieser Pruefpunkt ist keine Preisabweichung.")
    item = _assortment_item_for_issue(session, issue)
    item.price_decision = decision
    issue.status = "erledigt"
    session.commit()
    session.refresh(issue)
    return issue


def confirm_product_alias(session: Session, issue_id: int, product_id: int) -> OnboardingIssue:
    issue = _issue_or_error(session, issue_id)
    if issue.issue_type != "product_match":
        raise ValueError("Dieser Pruefpunkt ist keine Artikelzuordnung.")
    product = session.get(Product, product_id)
    if product is None:
        raise ValueError("Produkt wurde nicht gefunden.")
    item = _assortment_item_for_issue(session, issue)
    item.product_id = product.id
    _ensure_alias(session, product, item.source_product_name, issue.source_file)
    issue.list_value = product.name
    issue.status = "erledigt"
    session.commit()
    session.refresh(issue)
    return issue


def resolve_customer_conflict(session: Session, issue_id: int, source: str) -> OnboardingIssue:
    if source not in {"list", "folder"}:
        raise ValueError("Quelle fuer Kundendaten ist ungueltig.")
    issue = _issue_or_error(session, issue_id)
    if issue.issue_type != "merge_conflict":
        raise ValueError("Dieser Pruefpunkt ist kein Kundendaten-Konflikt.")
    if issue.field_name not in _CUSTOMER_CONFLICT_FIELDS:
        raise ValueError("Dieses Kundenfeld kann noch nicht automatisch uebernommen werden.")
    customer = _customer_for_issue(session, issue)
    value = issue.list_value if source == "list" else issue.folder_value
    setattr(customer, issue.field_name, value)
    issue.status = "erledigt"
    session.commit()
    session.refresh(issue)
    return issue


def _set_issue_status(session: Session, issue_id: int, status: str) -> OnboardingIssue:
    issue = _issue_or_error(session, issue_id)
    issue.status = status
    session.commit()
    session.refresh(issue)
    return issue


def _issue_or_error(session: Session, issue_id: int) -> OnboardingIssue:
    issue = session.get(OnboardingIssue, issue_id)
    if issue is None:
        raise ValueError("Pruefpunkt wurde nicht gefunden.")
    return issue


_CUSTOMER_CONFLICT_FIELDS = {
    "address",
    "phone",
    "contact_email",
    "delivery_notes",
    "opening_hours",
    "internal_notes",
}


def _customer_for_issue(session: Session, issue: OnboardingIssue) -> Customer:
    customer = session.scalar(select(Customer).where(Customer.name == issue.customer_name).limit(1))
    if customer is None:
        raise ValueError("Kunde zum Pruefpunkt wurde nicht gefunden.")
    return customer


def _assortment_item_for_issue(session: Session, issue: OnboardingIssue) -> CustomerAssortmentItem:
    customer = _customer_for_issue(session, issue)
    source_name = _source_product_name(issue)
    item = session.scalar(
        select(CustomerAssortmentItem)
        .where(CustomerAssortmentItem.customer_id == customer.id)
        .where(CustomerAssortmentItem.source_product_name == source_name)
        .limit(1)
    )
    if item is None:
        raise ValueError("Kundensortiment zum Pruefpunkt wurde nicht gefunden.")
    return item


def _source_product_name(issue: OnboardingIssue) -> str:
    value = issue.folder_value or ""
    if ":" in value:
        return value.split(":", 1)[0].strip()
    return value.strip()


def _ensure_alias(session: Session, product: Product, alias: str, source_file: str) -> None:
    existing = session.scalar(
        select(ProductAlias)
        .where(ProductAlias.product_id == product.id)
        .where(ProductAlias.alias == alias)
        .limit(1)
    )
    if existing is not None:
        existing.status = "bestaetigt"
        existing.source_file = source_file
        return
    session.add(ProductAlias(product_id=product.id, alias=alias, source_file=source_file, status="bestaetigt"))


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
