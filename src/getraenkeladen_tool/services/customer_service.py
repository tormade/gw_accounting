from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models import Customer
from ..schemas import CustomerCreate


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
        setattr(customer, field, value)
    session.commit()
    session.refresh(customer)
    return customer


def archive_customer(session: Session, customer_id: int) -> Customer:
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise ValueError("Kunde wurde nicht gefunden.")

    customer.is_active = False
    session.commit()
    session.refresh(customer)
    return customer


def restore_customer(session: Session, customer_id: int) -> Customer:
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise ValueError("Kunde wurde nicht gefunden.")

    customer.is_active = True
    session.commit()
    session.refresh(customer)
    return customer
