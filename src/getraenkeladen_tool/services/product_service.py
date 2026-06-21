from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models import Product
from ..schemas import ProductCreate


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
        setattr(product, field, value)
    session.commit()
    session.refresh(product)
    return product


def deactivate_product(session: Session, product_id: int) -> Product:
    product = session.get(Product, product_id)
    if product is None:
        raise ValueError("Produkt wurde nicht gefunden.")

    product.is_active = False
    session.commit()
    session.refresh(product)
    return product


def restore_product(session: Session, product_id: int) -> Product:
    product = session.get(Product, product_id)
    if product is None:
        raise ValueError("Produkt wurde nicht gefunden.")

    product.is_active = True
    session.commit()
    session.refresh(product)
    return product
