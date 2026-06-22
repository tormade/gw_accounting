from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import MasterDataChange


def log_master_data_change(
    session: Session,
    *,
    entity_type: str,
    entity_id: int,
    action: str,
    field_name: str,
    old_value: object,
    new_value: object,
    source: str | None = None,
) -> MasterDataChange | None:
    old_text = _serialize_value(old_value)
    new_text = _serialize_value(new_value)
    if old_text == new_text:
        return None
    change = MasterDataChange(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        field_name=field_name,
        old_value=old_text,
        new_value=new_text,
        source=source,
        created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    session.add(change)
    return change


def list_master_data_changes(session: Session, entity_type: str, entity_id: int) -> list[MasterDataChange]:
    return list(
        session.scalars(
            select(MasterDataChange)
            .where(MasterDataChange.entity_type == entity_type, MasterDataChange.entity_id == entity_id)
            .order_by(MasterDataChange.id.desc())
        )
    )


def _serialize_value(value: object) -> str | None:
    if value is None:
        return None
    return str(value)
