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
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_row: Mapped[int | None] = mapped_column(Integer(), nullable=True)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    unit: Mapped[str] = mapped_column(String(50))
    standard_price_cents: Mapped[int] = mapped_column(Integer())
    default_deposit_cents: Mapped[int] = mapped_column(Integer(), default=0)
    article_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_row: Mapped[int | None] = mapped_column(Integer(), nullable=True)


class MasterDataChange(Base):
    __tablename__ = "master_data_changes"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(30))
    entity_id: Mapped[int] = mapped_column(Integer())
    action: Mapped[str] = mapped_column(String(30))
    field_name: Mapped[str] = mapped_column(String(100))
    old_value: Mapped[str | None] = mapped_column(Text(), nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text(), nullable=True)
    source: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[str] = mapped_column(String(30))


class OnboardingIssue(Base):
    __tablename__ = "onboarding_issues"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(200))
    source_file: Mapped[str] = mapped_column(String(500))
    issue_type: Mapped[str] = mapped_column(String(80))
    field_name: Mapped[str] = mapped_column(String(100))
    list_value: Mapped[str | None] = mapped_column(Text(), nullable=True)
    folder_value: Mapped[str | None] = mapped_column(Text(), nullable=True)
    message: Mapped[str] = mapped_column(Text())
    status: Mapped[str] = mapped_column(String(30), default="offen")
    created_at: Mapped[str] = mapped_column(String(30))


class ProductAlias(Base):
    __tablename__ = "product_aliases"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    alias: Mapped[str] = mapped_column(String(200))
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="offen")

    product: Mapped["Product | None"] = relationship()


class CustomerAssortmentItem(Base):
    __tablename__ = "customer_assortment_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    source_product_name: Mapped[str] = mapped_column(String(200))
    last_quantity: Mapped[int] = mapped_column(Integer(), default=0)
    last_unit_price_cents: Mapped[int] = mapped_column(Integer(), default=0)
    last_deposit_cents: Mapped[int] = mapped_column(Integer(), default=0)
    sort_order: Mapped[int] = mapped_column(Integer(), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)

    customer: Mapped[Customer] = relationship()
    product: Mapped["Product | None"] = relationship()


class DropdownOption(Base):
    __tablename__ = "dropdown_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(String(120))
    sort_order: Mapped[int] = mapped_column(Integer(), default=0)
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
    delivery_fee_enabled: Mapped[bool] = mapped_column(Boolean(), default=False)
    delivery_comment: Mapped[str | None] = mapped_column(Text(), nullable=True)
    footer_text: Mapped[str | None] = mapped_column(Text(), nullable=True)
    number_released: Mapped[bool] = mapped_column(Boolean(), default=False)

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
    number_released: Mapped[bool] = mapped_column(Boolean(), default=False)

    customer: Mapped[Customer] = relationship()
    lines: Mapped[list["OrderLine"]] = relationship(cascade="all, delete-orphan", order_by="OrderLine.id")
    deposit_returns: Mapped[list["OrderDepositReturn"]] = relationship(
        cascade="all, delete-orphan",
        order_by="OrderDepositReturn.id",
    )


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


class OrderDepositReturn(Base):
    __tablename__ = "order_deposit_returns"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[int] = mapped_column(Integer())
    deposit_cents: Mapped[int] = mapped_column(Integer())
