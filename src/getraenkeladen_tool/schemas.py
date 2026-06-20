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
