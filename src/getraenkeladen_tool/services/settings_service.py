from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import DropdownOption


PRODUCT_UNIT_CATEGORY = "product_unit"
DEFAULT_PRODUCT_UNITS = ("Kiste", "Flasche", "Fass", "Palette", "Stueck", "Karton")


def ensure_default_product_units(session: Session) -> None:
    for sort_order, value in enumerate(DEFAULT_PRODUCT_UNITS):
        _add_option_if_missing(session, PRODUCT_UNIT_CATEGORY, value, sort_order)
    session.commit()


def list_product_units(session: Session) -> list[str]:
    ensure_default_product_units(session)
    return list(
        session.scalars(
            select(DropdownOption.value)
            .where(DropdownOption.category == PRODUCT_UNIT_CATEGORY)
            .where(DropdownOption.is_active == True)  # noqa: E712
            .order_by(DropdownOption.sort_order, DropdownOption.value)
        )
    )


def add_product_unit(session: Session, value: str) -> DropdownOption:
    clean_value = value.strip()
    if not clean_value:
        raise ValueError("Einheit darf nicht leer sein.")
    existing = session.scalar(
        select(DropdownOption)
        .where(DropdownOption.category == PRODUCT_UNIT_CATEGORY)
        .where(DropdownOption.value == clean_value)
        .limit(1)
    )
    if existing is not None:
        existing.is_active = True
        session.commit()
        session.refresh(existing)
        return existing

    max_sort_order = len(list_product_units(session))
    option = DropdownOption(
        category=PRODUCT_UNIT_CATEGORY,
        value=clean_value,
        sort_order=max_sort_order,
        is_active=True,
    )
    session.add(option)
    session.commit()
    session.refresh(option)
    return option


def _add_option_if_missing(session: Session, category: str, value: str, sort_order: int) -> None:
    exists = (
        session.scalar(
            select(DropdownOption.id)
            .where(DropdownOption.category == category)
            .where(DropdownOption.value == value)
            .limit(1)
        )
        is not None
    )
    if not exists:
        session.add(DropdownOption(category=category, value=value, sort_order=sort_order, is_active=True))
