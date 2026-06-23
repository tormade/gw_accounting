from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Document


def list_documents_by_type(session: Session, document_type: str) -> list[Document]:
    return list(
        session.scalars(
            select(Document)
            .options(selectinload(Document.customer))
            .where(Document.document_type == document_type)
            .where(Document.number_released == False)  # noqa: E712
            .order_by(Document.delivery_date.desc(), Document.id.desc())
        )
    )
