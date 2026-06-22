from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models import MasterDataChange, Product
from ..schemas import ProductCreate
from .audit_service import list_master_data_changes, log_master_data_change


def create_product(session: Session, payload: ProductCreate) -> Product:
    product = Product(**payload.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def list_active_products(session: Session) -> list[Product]:
    return list(
        session.scalars(
            select(Product)
            .where(Product.is_active == True)  # noqa: E712
            .order_by(Product.name)
        )
    )


def list_products(session: Session) -> list[Product]:
    return list(session.scalars(select(Product).order_by(Product.name)))


def update_product(session: Session, product_id: int, payload: ProductCreate) -> Product:
    product = session.get(Product, product_id)
    if product is None:
        raise ValueError("Produkt wurde nicht gefunden.")

    for field, value in payload.model_dump().items():
        old_value = getattr(product, field)
        log_master_data_change(
            session,
            entity_type="product",
            entity_id=product.id,
            action="update",
            field_name=field,
            old_value=old_value,
            new_value=value,
            source=payload.source_file,
        )
        setattr(product, field, value)
    session.commit()
    session.refresh(product)
    return product


def deactivate_product(session: Session, product_id: int) -> Product:
    product = session.get(Product, product_id)
    if product is None:
        raise ValueError("Produkt wurde nicht gefunden.")

    log_master_data_change(
        session,
        entity_type="product",
        entity_id=product.id,
        action="deactivate",
        field_name="is_active",
        old_value=product.is_active,
        new_value=False,
    )
    product.is_active = False
    session.commit()
    session.refresh(product)
    return product


def restore_product(session: Session, product_id: int) -> Product:
    product = session.get(Product, product_id)
    if product is None:
        raise ValueError("Produkt wurde nicht gefunden.")

    log_master_data_change(
        session,
        entity_type="product",
        entity_id=product.id,
        action="restore",
        field_name="is_active",
        old_value=product.is_active,
        new_value=True,
    )
    product.is_active = True
    session.commit()
    session.refresh(product)
    return product


def list_product_changes(session: Session, product_id: int) -> list[MasterDataChange]:
    return list_master_data_changes(session, "product", product_id)


def revert_product_change(session: Session, change_id: int) -> Product:
    change = session.get(MasterDataChange, change_id)
    if change is None or change.entity_type != "product":
        raise ValueError("Aenderung wurde nicht gefunden.")
    product = session.get(Product, change.entity_id)
    if product is None:
        raise ValueError("Produkt wurde nicht gefunden.")
    setattr(product, change.field_name, _deserialize_product_value(change.field_name, change.old_value))
    log_master_data_change(
        session,
        entity_type="product",
        entity_id=product.id,
        action="revert",
        field_name=change.field_name,
        old_value=change.new_value,
        new_value=change.old_value,
        source=f"revert:{change.id}",
    )
    session.commit()
    session.refresh(product)
    return product


def _deserialize_product_value(field_name: str, value: str | None):
    if field_name in {"is_active"}:
        return value == "True"
    if field_name in {"source_row", "standard_price_cents", "default_deposit_cents"}:
        return int(value) if value not in (None, "") else 0
    return value
