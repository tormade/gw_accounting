from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Customer, Document, Order


@dataclass(frozen=True, slots=True)
class CustomerFolderFile:
    path: Path
    kind: str
    label: str
    can_seed_order: bool


@dataclass(frozen=True, slots=True)
class CustomerFolderSnapshot:
    customer: Customer
    folder_path: Path
    folder_exists: bool
    files: list[CustomerFolderFile]
    documents: list[Document]
    orders: list[Order]


def get_customer_folder_snapshot(session: Session, customer_id: int) -> CustomerFolderSnapshot:
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise ValueError("Kunde wurde nicht gefunden.")

    folder_path = Path(customer.folder_path)
    folder_exists = folder_path.is_dir()
    return CustomerFolderSnapshot(
        customer=customer,
        folder_path=folder_path,
        folder_exists=folder_exists,
        files=_folder_files(folder_path) if folder_exists else [],
        documents=_customer_documents(session, customer_id),
        orders=_customer_orders(session, customer_id),
    )


def _customer_documents(session: Session, customer_id: int) -> list[Document]:
    return list(
        session.scalars(
            select(Document)
            .options(selectinload(Document.customer))
            .where(Document.customer_id == customer_id)
            .where(Document.number_released == False)  # noqa: E712
            .order_by(Document.delivery_date.desc(), Document.id.desc())
        )
    )


def _customer_orders(session: Session, customer_id: int) -> list[Order]:
    return list(
        session.scalars(
            select(Order)
            .options(selectinload(Order.lines), selectinload(Order.deposit_returns), selectinload(Order.customer))
            .where(Order.customer_id == customer_id)
            .where(Order.status != "archiviert")
            .where(Order.number_released == False)  # noqa: E712
            .order_by(Order.delivery_date.desc(), Order.id.desc())
        )
    )


def _folder_files(folder_path: Path) -> list[CustomerFolderFile]:
    files = []
    for path in sorted(folder_path.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file() or path.suffix.lower() not in {".xlsx", ".pdf"}:
            continue
        files.append(
            CustomerFolderFile(
                path=path,
                kind=_file_kind(path),
                label=path.name,
                can_seed_order=path.suffix.lower() == ".xlsx",
            )
        )
    return files


def _file_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    name = path.name.lower()
    if suffix == ".pdf":
        return "PDF"
    if "_re" in name or "rechnung" in name:
        return "Excel-Rechnung"
    if "_ls" in name or "lieferschein" in name:
        return "Excel-Lieferschein"
    return "Excel-Datei"
