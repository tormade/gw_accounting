from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models import Customer, MasterDataChange
from ..schemas import CustomerCreate
from .audit_service import list_master_data_changes, log_master_data_change


def create_customer(session: Session, payload: CustomerCreate) -> Customer:
    customer = Customer(**payload.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


def list_customers(session: Session) -> list[Customer]:
    return list(session.scalars(select(Customer).order_by(Customer.name)))


def list_active_customers(session: Session) -> list[Customer]:
    return list(
        session.scalars(
            select(Customer)
            .where(Customer.is_active == True)  # noqa: E712
            .order_by(Customer.name)
        )
    )


def update_customer(session: Session, customer_id: int, payload: CustomerCreate) -> Customer:
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise ValueError("Kunde wurde nicht gefunden.")

    for field, value in payload.model_dump().items():
        old_value = getattr(customer, field)
        log_master_data_change(
            session,
            entity_type="customer",
            entity_id=customer.id,
            action="update",
            field_name=field,
            old_value=old_value,
            new_value=value,
            source=payload.source_file,
        )
        setattr(customer, field, value)
    session.commit()
    session.refresh(customer)
    return customer


def archive_customer(session: Session, customer_id: int) -> Customer:
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise ValueError("Kunde wurde nicht gefunden.")

    log_master_data_change(
        session,
        entity_type="customer",
        entity_id=customer.id,
        action="archive",
        field_name="is_active",
        old_value=customer.is_active,
        new_value=False,
    )
    customer.is_active = False
    session.commit()
    session.refresh(customer)
    return customer


def restore_customer(session: Session, customer_id: int) -> Customer:
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise ValueError("Kunde wurde nicht gefunden.")

    log_master_data_change(
        session,
        entity_type="customer",
        entity_id=customer.id,
        action="restore",
        field_name="is_active",
        old_value=customer.is_active,
        new_value=True,
    )
    customer.is_active = True
    session.commit()
    session.refresh(customer)
    return customer


def list_customer_changes(session: Session, customer_id: int) -> list[MasterDataChange]:
    return list_master_data_changes(session, "customer", customer_id)


def revert_customer_change(session: Session, change_id: int) -> Customer:
    change = session.get(MasterDataChange, change_id)
    if change is None or change.entity_type != "customer":
        raise ValueError("Aenderung wurde nicht gefunden.")
    customer = session.get(Customer, change.entity_id)
    if customer is None:
        raise ValueError("Kunde wurde nicht gefunden.")
    setattr(customer, change.field_name, _deserialize_customer_value(change.field_name, change.old_value))
    log_master_data_change(
        session,
        entity_type="customer",
        entity_id=customer.id,
        action="revert",
        field_name=change.field_name,
        old_value=change.new_value,
        new_value=change.old_value,
        source=f"revert:{change.id}",
    )
    session.commit()
    session.refresh(customer)
    return customer


def _deserialize_customer_value(field_name: str, value: str | None):
    if field_name in {"is_active"}:
        return value == "True"
    if field_name in {"source_row"}:
        return int(value) if value not in (None, "") else None
    return value
