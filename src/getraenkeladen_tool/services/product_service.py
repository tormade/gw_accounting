from sqlalchemy.orm import Session

from ..models import Product
from ..schemas import ProductCreate


def create_product(session: Session, payload: ProductCreate) -> Product:
    product = Product(**payload.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product
