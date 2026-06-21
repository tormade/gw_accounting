from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1)
    folder_path: str = Field(min_length=1)
    address: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    payment_method: str | None = None
    next_contact_date: str | None = None
    delivery_notes: str | None = None
    opening_hours: str | None = None
    internal_notes: str | None = None
    is_active: bool = True


class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    standard_price_cents: int = Field(ge=0)
    article_number: str | None = None
    is_active: bool = True


class DocumentLineItem(BaseModel):
    name: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price_cents: int = Field(ge=0)
    deposit_cents: int = Field(ge=0, default=0)


class DocumentCreate(BaseModel):
    customer_id: int = Field(gt=0)
    document_type: str = Field(min_length=1)
    document_number: str = Field(min_length=1)
    delivery_date: str | None = None
    delivery_slot: str | None = None
    line_items: list[DocumentLineItem] = Field(min_length=1)
    order_id: int | None = Field(default=None, gt=0)


class OrderLineCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    unit_price_cents: int | None = Field(default=None, ge=0)
    deposit_cents: int = Field(default=0, ge=0)


class OrderCreate(BaseModel):
    order_number: str = Field(min_length=1)
    customer_id: int = Field(gt=0)
    order_date: str = Field(min_length=1)
    delivery_date: str = Field(min_length=1)
    delivery_slot: str | None = None
    tour_area: str | None = None
    status: str = "geplant"
    lines: list[OrderLineCreate] = Field(min_length=1)
