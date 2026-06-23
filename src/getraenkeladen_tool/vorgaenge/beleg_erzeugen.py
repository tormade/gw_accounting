from pathlib import Path

from sqlalchemy.orm import Session

from ..models import Document
from ..schemas import DocumentCreate
from ..services.document_service import create_document


def beleg_erzeugen(
    session: Session,
    payload: DocumentCreate,
    datev_upload_dir: Path | None = None,
    assets: set[str] | None = None,
) -> Document:
    return create_document(
        session=session,
        payload=payload,
        datev_upload_dir=datev_upload_dir,
        assets=assets,
    )
