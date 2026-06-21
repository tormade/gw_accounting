from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1)
    folder_path: str = Field(min_length=1)
    address: str | None = None
    payment_method: str | None = None


class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    standard_price_cents: int = Field(ge=0)


class DocumentLineItem(BaseModel):
    name: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price_cents: int = Field(ge=0)
    deposit_cents: int = Field(ge=0, default=0)


class DocumentCreate(BaseModel):
    customer_id: int = Field(gt=0)
    document_type: str = Field(min_length=1)
    document_number: str = Field(min_length=1)
    line_items: list[DocumentLineItem] = Field(min_length=1)
