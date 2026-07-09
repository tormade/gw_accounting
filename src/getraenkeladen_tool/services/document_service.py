from pathlib import Path
from shutil import copy2
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..kern.regeln.beleg import BelegParameter, PfandRueckgabe, Position, berechne_beleg
from ..models import Customer, Document, DocumentLineSnapshot, OpenItem
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
    temporary_excel_path = _temporary_output_path(paths.excel_path) if "excel" in requested_assets else None
    temporary_pdf_path = _temporary_output_path(paths.pdf_path) if "pdf" in requested_assets else None
    existing_output_paths = {path: path.exists() for path in (paths.excel_path, paths.pdf_path)}
    published_paths: list[Path] = []
    try:
        if temporary_excel_path is not None and document_type == "Rechnung":
            build_invoice_workbook(
                temporary_excel_path,
                customer.name,
                document_number,
                line_items,
                document_date=document_date,
                deposit_returns=deposit_returns,
                delivery_fee_enabled=payload.delivery_fee_enabled,
                invoice_footer_text=payload.footer_text,
            )
        elif temporary_excel_path is not None:
            build_delivery_note_workbook(
                temporary_excel_path,
                customer.name,
                document_number,
                line_items,
                document_date=document_date,
                deposit_returns=deposit_returns,
                delivery_fee_enabled=payload.delivery_fee_enabled,
                delivery_comment=payload.delivery_comment,
                footer_text=payload.footer_text,
            )

        if temporary_pdf_path is not None:
            build_document_pdf(
                temporary_pdf_path,
            document_type,
            customer.name,
            document_number,
            line_items,
            deposit_returns=deposit_returns,
            document_date=document_date,
            customer_address=customer.address,
            delivery_fee_enabled=payload.delivery_fee_enabled,
            note_text=payload.delivery_comment,
            footer_text=payload.footer_text,
            )

        for temporary_path, output_path in ((temporary_excel_path, paths.excel_path), (temporary_pdf_path, paths.pdf_path)):
            if temporary_path is None:
                continue
            temporary_path.replace(output_path)
            published_paths.append(output_path)

        if document_type == "Rechnung" and datev_upload_dir is not None and "pdf" in requested_assets:
            datev_export_path = _copy_invoice_pdf_to_datev(paths.pdf_path, datev_upload_dir, document_date)
    except Exception:
        for path in (temporary_excel_path, temporary_pdf_path):
            if path is not None and path.exists():
                path.unlink()
        for path in published_paths:
            if not existing_output_paths[path] and path.exists():
                path.unlink()
        raise


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
            delivery_fee_enabled=payload.delivery_fee_enabled,
            delivery_comment=payload.delivery_comment,
            footer_text=payload.footer_text,
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
        document.delivery_fee_enabled = payload.delivery_fee_enabled
        document.delivery_comment = payload.delivery_comment
        document.footer_text = payload.footer_text

    _replace_document_line_snapshots(document, payload)

    if document_type == "Rechnung":
        amount_cents = _document_total_cents(payload)
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


def _replace_document_line_snapshots(document: Document, payload: DocumentCreate) -> None:
    document.line_snapshots.clear()
    sort_order = 1
    for item in payload.line_items:
        document.line_snapshots.append(
            DocumentLineSnapshot(
                kind="position",
                name=item.name,
                quantity=item.quantity,
                unit_price_cents=item.unit_price_cents,
                deposit_cents=item.deposit_cents,
                sort_order=sort_order,
            )
        )
        sort_order += 1
    for item in payload.deposit_returns:
        document.line_snapshots.append(
            DocumentLineSnapshot(
                kind="deposit_return",
                name=item.name,
                quantity=item.quantity,
                unit_price_cents=0,
                deposit_cents=item.deposit_cents,
                sort_order=sort_order,
            )
        )
        sort_order += 1


def _copy_invoice_pdf_to_datev(pdf_path: Path, datev_upload_dir: Path, document_date: str) -> Path:
    month_folder = datev_upload_dir / document_date[:7]
    target_path = month_folder / pdf_path.name
    ensure_parent_folder(target_path)
    copy2(pdf_path, target_path)
    return target_path


def _temporary_output_path(output_path: Path) -> Path:
    return output_path.with_name(f".{output_path.stem}.{uuid4().hex}.tmp{output_path.suffix}")


def _document_total_cents(payload: DocumentCreate) -> int:
    result = berechne_beleg(
        positionen=[
            Position(item.name, item.quantity, item.unit_price_cents, item.deposit_cents)
            for item in payload.line_items
        ],
        ruecknahmen=[
            PfandRueckgabe(item.name, item.quantity, item.deposit_cents)
            for item in payload.deposit_returns
        ],
        parameter=BelegParameter(lieferpauschale_aktiv=payload.delivery_fee_enabled),
    )
    return result.brutto_cents
