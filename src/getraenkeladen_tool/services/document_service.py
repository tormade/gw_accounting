from pathlib import Path
from shutil import copy2
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..kern.regeln.beleg import BelegParameter, BelegSummen, PfandRueckgabe, Position, berechne_beleg
from ..models import Customer, Document, DocumentLine, OpenItem
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
    footer_text = _document_footer_text(document_type, customer, payload)
    due_date = _invoice_due_date(document_type, customer, document_date)
    paths = build_document_paths(
        customer_folder=Path(customer.folder_path),
        document_type=document_type,
        document_number=document_number,
        customer_name=customer.name,
        document_date=document_date,
    )
    source_workbook_path = _latest_customer_excel(Path(customer.folder_path), exclude_path=paths.excel_path)
    line_items = [item.model_dump() for item in payload.line_items]
    deposit_returns = [item.model_dump() for item in payload.deposit_returns]

    if document_type not in {"Rechnung", "Lieferauftrag", "Lieferschein"}:
        raise ValueError("Belegtyp muss Rechnung oder Lieferauftrag sein.")

    if document is not None and is_partial_generation and _has_snapshot(session, document.id):
        expected_lines = _document_snapshot_lines(document.id, payload)
        if not _snapshot_matches_payload(session, document.id, expected_lines):
            raise ValueError("Belegdaten passen nicht zum bereits erzeugten Teil-Export. Bitte Excel und PDF zusammen neu erzeugen.")

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
                delivery_fee_enabled=payload.delivery_fee_enabled,
                invoice_footer_text=footer_text,
                source_workbook_path=source_workbook_path,
            )
        else:
            build_delivery_note_workbook(
                paths.excel_path,
                customer.name,
                document_number,
                line_items,
                document_date=document_date,
                deposit_returns=deposit_returns,
                delivery_fee_enabled=payload.delivery_fee_enabled,
                delivery_comment=payload.delivery_comment,
                footer_text=footer_text,
                source_workbook_path=source_workbook_path,
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
            delivery_fee_enabled=payload.delivery_fee_enabled,
            note_text=payload.delivery_comment,
            footer_text=footer_text,
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
            delivery_fee_enabled=payload.delivery_fee_enabled,
            delivery_comment=payload.delivery_comment,
            footer_text=footer_text,
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
        document.footer_text = footer_text

    snapshot_lines = _document_snapshot_lines(document.id, payload)
    session.query(DocumentLine).filter(DocumentLine.document_id == document.id).delete()
    session.add_all(snapshot_lines)
    snapshot_total_cents = snapshot_lines[-1].total_cents

    if document_type == "Rechnung":
        amount_cents = snapshot_total_cents
        open_item = session.scalar(select(OpenItem).where(OpenItem.document_id == document.id).limit(1))
        if open_item is None:
            session.add(
                OpenItem(
                    document_id=document.id,
                    customer_name=customer.name,
                    document_number=document_number,
                    document_date=payload.delivery_date,
                    due_date=due_date,
                    amount_cents=amount_cents,
                    payment_method=customer.payment_method or "unbekannt",
                    status="offen",
                )
            )
        else:
            open_item.customer_name = customer.name
            open_item.document_number = document_number
            open_item.document_date = payload.delivery_date
            open_item.due_date = due_date
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


def _latest_customer_excel(customer_folder: Path, exclude_path: Path | None = None) -> Path | None:
    if not customer_folder.is_dir():
        return None
    excluded = exclude_path.resolve() if exclude_path is not None else None
    candidates = []
    for path in customer_folder.iterdir():
        if not path.is_file() or path.suffix.lower() != ".xlsx":
            continue
        if path.name.startswith("~$"):
            continue
        if excluded is not None and path.resolve() == excluded:
            continue
        candidates.append(path)
    if not candidates:
        return None
    return max(candidates, key=lambda path: (path.stat().st_mtime, path.name.lower()))


def _document_calculation(payload: DocumentCreate) -> BelegSummen:
    return berechne_beleg(
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


def _document_snapshot_lines(document_id: int, payload: DocumentCreate) -> list[DocumentLine]:
    result = _document_calculation(payload)
    lines: list[DocumentLine] = []
    sort_order = 0
    for item, total_cents in zip(payload.line_items, result.positionssummen_cents, strict=True):
        lines.append(
            DocumentLine(
                document_id=document_id,
                line_type="position",
                name=item.name,
                quantity=item.quantity,
                unit_price_cents=item.unit_price_cents,
                deposit_cents=item.deposit_cents,
                total_cents=total_cents,
                sort_order=sort_order,
            )
        )
        sort_order += 1
    for item, total_cents in zip(payload.deposit_returns, result.ruecknahme_summen_cents, strict=True):
        lines.append(
            DocumentLine(
                document_id=document_id,
                line_type="deposit_return",
                name=item.name,
                quantity=item.quantity,
                unit_price_cents=0,
                deposit_cents=item.deposit_cents,
                total_cents=total_cents,
                sort_order=sort_order,
            )
        )
        sort_order += 1
    if result.lieferpauschale_cents:
        lines.append(
            DocumentLine(
                document_id=document_id,
                line_type="delivery_fee",
                name="Lieferpauschale",
                quantity=1,
                unit_price_cents=result.lieferpauschale_cents,
                deposit_cents=0,
                total_cents=result.lieferpauschale_cents,
                sort_order=sort_order,
            )
        )
        sort_order += 1
    lines.append(
        DocumentLine(
            document_id=document_id,
            line_type="summary",
            name="Brutto",
            quantity=1,
            unit_price_cents=result.brutto_cents,
            deposit_cents=0,
            total_cents=result.brutto_cents,
            sort_order=sort_order,
        )
    )
    return lines


def _document_footer_text(document_type: str, customer: Customer, payload: DocumentCreate) -> str | None:
    if payload.footer_text:
        return payload.footer_text
    if document_type != "Rechnung":
        return None
    if _is_bank_transfer(customer.payment_method):
        due_date = _invoice_due_date(document_type, customer, payload.delivery_date or "ohne-datum")
        if due_date is not None:
            return f"Bitte ueberweisen Sie den Rechnungsbetrag bis zum {due_date}."
        return "Bitte ueberweisen Sie den Rechnungsbetrag."
    if _is_sepa(customer.payment_method):
        return "Rechnungsbetrag wird per Sepa Basis Lastschrift Mandat eingezogen."
    return None


def _invoice_due_date(document_type: str, customer: Customer, document_date: str) -> str | None:
    if document_type != "Rechnung" or not _is_bank_transfer(customer.payment_method):
        return None
    try:
        return (date.fromisoformat(document_date) + timedelta(days=7)).isoformat()
    except ValueError:
        return None


def _is_bank_transfer(payment_method: str | None) -> bool:
    normalized = (payment_method or "").lower().replace("ü", "ue")
    return "ueberweisung" in normalized


def _is_sepa(payment_method: str | None) -> bool:
    return "sepa" in (payment_method or "").lower() or "lastschrift" in (payment_method or "").lower()


def _has_snapshot(session: Session, document_id: int) -> bool:
    return session.scalar(select(DocumentLine.id).where(DocumentLine.document_id == document_id).limit(1)) is not None


def _snapshot_matches_payload(session: Session, document_id: int, expected_lines: list[DocumentLine]) -> bool:
    existing_lines = list(
        session.scalars(
            select(DocumentLine)
            .where(DocumentLine.document_id == document_id)
            .order_by(DocumentLine.sort_order)
        )
    )
    return [_snapshot_signature(line) for line in existing_lines] == [
        _snapshot_signature(line) for line in expected_lines
    ]


def _snapshot_signature(line: DocumentLine) -> tuple[str, str, int, int, int, int]:
    return (
        line.line_type,
        line.name,
        line.quantity,
        line.unit_price_cents,
        line.deposit_cents,
        line.total_cents,
    )
