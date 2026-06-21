from pathlib import Path

from sqlalchemy.orm import Session

from ..models import Customer, Document, OpenItem
from ..schemas import DocumentCreate
from .excel_service import build_delivery_note_workbook, build_invoice_workbook
from .pdf_service import build_document_pdf


def _safe_filename_part(value: str) -> str:
    return value.strip().replace("/", "-").replace("\\", "-").replace(" ", "_")


def create_document(session: Session, payload: DocumentCreate) -> Document:
    customer = session.get(Customer, payload.customer_id)
    if customer is None:
        raise ValueError("Kunde wurde nicht gefunden.")

    document_type = payload.document_type.strip()
    document_number = payload.document_number.strip()
    excel_path = (
        Path(customer.folder_path)
        / f"{_safe_filename_part(document_number)}_{_safe_filename_part(document_type)}.xlsx"
    )
    pdf_path = excel_path.with_suffix(".pdf")
    line_items = [item.model_dump() for item in payload.line_items]

    if document_type == "Rechnung":
        build_invoice_workbook(excel_path, customer.name, document_number, line_items)
    elif document_type == "Lieferschein":
        build_delivery_note_workbook(excel_path, customer.name, document_number, line_items)
    else:
        raise ValueError("Belegtyp muss Rechnung oder Lieferschein sein.")
    build_document_pdf(pdf_path, document_type, customer.name, document_number, line_items)

    document = Document(
        customer_id=customer.id,
        document_type=document_type,
        document_number=document_number,
        excel_path=str(excel_path),
        pdf_path=str(pdf_path),
        delivery_date=payload.delivery_date,
        delivery_slot=payload.delivery_slot,
    )
    session.add(document)
    session.flush()

    if document_type == "Rechnung":
        amount_cents = sum(
            (item.unit_price_cents + item.deposit_cents) * item.quantity
            for item in payload.line_items
        )
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

    session.commit()
    session.refresh(document)
    return document
