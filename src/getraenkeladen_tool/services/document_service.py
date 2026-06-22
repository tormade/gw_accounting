from pathlib import Path
from shutil import copy2

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Customer, Document, OpenItem
from ..schemas import DocumentCreate
from .excel_service import build_delivery_note_workbook, build_invoice_workbook
from .file_naming_service import build_document_paths
from .file_service import ensure_parent_folder
from .pdf_service import build_document_pdf


def create_document(
    session: Session,
    payload: DocumentCreate,
    datev_upload_dir: Path | None = None,
    assets: set[str] | None = None,
) -> Document:
    is_partial_generation = assets is not None
    requested_assets = assets or {"excel", "pdf"}
    if not requested_assets <= {"excel", "pdf"}:
        raise ValueError("assets darf nur excel und pdf enthalten.")

    customer = session.get(Customer, payload.customer_id)
    if customer is None:
        raise ValueError("Kunde wurde nicht gefunden.")

    document_type = payload.document_type.strip()
    document_number = payload.document_number.strip()
    document = _existing_document(session, document_type, document_number)
    if document is not None and not is_partial_generation:
        raise ValueError("Rechnungsnummer ist bereits vorhanden.")
    if document is not None and (document.customer_id != customer.id or document.order_id != payload.order_id):
        raise ValueError("Rechnungsnummer ist bereits vorhanden.")

    document_date = payload.delivery_date or "ohne-datum"
    paths = build_document_paths(
        customer_folder=Path(customer.folder_path),
        document_type=document_type,
        document_number=document_number,
        customer_name=customer.name,
        document_date=document_date,
    )
    line_items = [item.model_dump() for item in payload.line_items]
    deposit_returns = [item.model_dump() for item in payload.deposit_returns]

    if document_type not in {"Rechnung", "Lieferauftrag", "Lieferschein"}:
        raise ValueError("Belegtyp muss Rechnung oder Lieferauftrag sein.")

    datev_export_path = None
    if "excel" in requested_assets:
        if document_type == "Rechnung":
            build_invoice_workbook(
                paths.excel_path,
                customer.name,
                document_number,
                line_items,
                document_date=document_date,
                deposit_returns=deposit_returns,
            )
        else:
            build_delivery_note_workbook(
                paths.excel_path,
                customer.name,
                document_number,
                line_items,
                document_date=document_date,
                deposit_returns=deposit_returns,
            )

    if "pdf" in requested_assets:
        build_document_pdf(
            paths.pdf_path,
            document_type,
            customer.name,
            document_number,
            line_items,
            deposit_returns=deposit_returns,
            document_date=document_date,
            customer_address=customer.address,
        )

    if document_type == "Rechnung" and datev_upload_dir is not None and "pdf" in requested_assets:
        datev_export_path = _copy_invoice_pdf_to_datev(paths.pdf_path, datev_upload_dir, document_date)

    if document is None:
        document = Document(
            customer_id=customer.id,
            order_id=payload.order_id,
            document_type=document_type,
            document_number=document_number,
            excel_path=str(paths.excel_path),
            pdf_path=str(paths.pdf_path),
            datev_export_path=str(datev_export_path) if datev_export_path is not None else None,
            delivery_date=payload.delivery_date,
            delivery_slot=payload.delivery_slot,
        )
        session.add(document)
        session.flush()
    else:
        document.excel_path = str(paths.excel_path)
        document.pdf_path = str(paths.pdf_path)
        if datev_export_path is not None:
            document.datev_export_path = str(datev_export_path)
        document.delivery_date = payload.delivery_date
        document.delivery_slot = payload.delivery_slot

    if document_type == "Rechnung":
        amount_cents = sum(
            (item.unit_price_cents + item.deposit_cents) * item.quantity
            for item in payload.line_items
        ) - sum(
            item.deposit_cents * item.quantity
            for item in payload.deposit_returns
        )
        open_item = session.scalar(select(OpenItem).where(OpenItem.document_id == document.id).limit(1))
        if open_item is None:
            session.add(
                OpenItem(
                    document_id=document.id,
                    customer_name=customer.name,
                    document_number=document_number,
                    amount_cents=amount_cents,
                    payment_method=customer.payment_method or "unbekannt",
                    status="offen",
                )
            )
        else:
            open_item.customer_name = customer.name
            open_item.document_number = document_number
            open_item.amount_cents = amount_cents
            open_item.payment_method = customer.payment_method or "unbekannt"

    session.commit()
    session.refresh(document)
    return document


def latest_invoice_number(session: Session) -> str | None:
    return session.scalar(
        select(Document.document_number)
        .where(Document.document_type == "Rechnung")
        .order_by(Document.id.desc())
        .limit(1)
    )


def _existing_document(session: Session, document_type: str, document_number: str) -> Document | None:
    return session.scalar(
        select(Document)
        .where(Document.document_type == document_type)
        .where(Document.document_number == document_number)
        .where(Document.number_released == False)  # noqa: E712
        .limit(1)
    )


def _copy_invoice_pdf_to_datev(pdf_path: Path, datev_upload_dir: Path, document_date: str) -> Path:
    month_folder = datev_upload_dir / document_date[:7]
    target_path = month_folder / pdf_path.name
    ensure_parent_folder(target_path)
    copy2(pdf_path, target_path)
    return target_path
