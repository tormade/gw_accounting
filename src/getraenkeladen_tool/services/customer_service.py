from sqlalchemy.orm import Session

from ..models import Customer
from ..schemas import CustomerCreate


def create_customer(session: Session, payload: CustomerCreate) -> Customer:
    customer = Customer(**payload.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer
