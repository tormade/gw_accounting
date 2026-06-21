from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    folder_path: Mapped[str] = mapped_column(String(500))
    address: Mapped[str | None] = mapped_column(Text(), nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    next_contact_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    delivery_notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    opening_hours: Mapped[str | None] = mapped_column(Text(), nullable=True)
    internal_notes: Mapped[str | None] = mapped_column(Text(), nullable=True)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    unit: Mapped[str] = mapped_column(String(50))
    standard_price_cents: Mapped[int] = mapped_column(Integer())
    article_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"), nullable=True)
    document_type: Mapped[str] = mapped_column(String(30))
    document_number: Mapped[str] = mapped_column(String(50))
    excel_path: Mapped[str] = mapped_column(String(500))
    pdf_path: Mapped[str] = mapped_column(String(500))
    datev_export_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    delivery_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    delivery_slot: Mapped[str | None] = mapped_column(String(30), nullable=True)

    customer: Mapped[Customer] = relationship()
    order: Mapped["Order | None"] = relationship()


class OpenItem(Base):
    __tablename__ = "open_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    customer_name: Mapped[str] = mapped_column(String(200))
    document_number: Mapped[str] = mapped_column(String(50))
    amount_cents: Mapped[int] = mapped_column(Integer())
    payment_method: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="offen")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(String(50))
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    order_date: Mapped[str] = mapped_column(String(20))
    delivery_date: Mapped[str] = mapped_column(String(20))
    delivery_slot: Mapped[str | None] = mapped_column(String(30), nullable=True)
    tour_area: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="geplant")

    customer: Mapped[Customer] = relationship()
    lines: Mapped[list["OrderLine"]] = relationship(cascade="all, delete-orphan", order_by="OrderLine.id")


class OrderLine(Base):
    __tablename__ = "order_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    product_name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[int] = mapped_column(Integer())
    unit_price_cents: Mapped[int] = mapped_column(Integer())
    deposit_cents: Mapped[int] = mapped_column(Integer(), default=0)

    product: Mapped[Product | None] = relationship()
