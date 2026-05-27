from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Error(BaseModel):
    code: str
    message: str
    details: dict | None = None

    model_config = ConfigDict(extra="forbid")


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal = Field(gt=0, multiple_of=Decimal("0.01"))
    currency: str = Field(default="BRL", min_length=3, max_length=3)
    sku: str | None = Field(default=None, max_length=64)
    stock: int = Field(default=0, ge=0)
    active: bool = True

    model_config = ConfigDict(
        extra="forbid",
        json_encoders={Decimal: lambda v: float(v)},
    )


class ProductCreate(ProductBase):
    pass


class ProductReplace(ProductBase):
    pass


class ProductPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal | None = Field(default=None, gt=0, multiple_of=Decimal("0.01"))
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    sku: str | None = Field(default=None, max_length=64)
    stock: int | None = Field(default=None, ge=0)
    active: bool | None = None

    model_config = ConfigDict(
        extra="forbid",
        json_encoders={Decimal: lambda v: float(v)},
    )

    @model_validator(mode="after")
    def _reject_explicit_nulls(self):
        not_nullable_fields = ("name", "price", "currency", "stock", "active")
        for field_name in not_nullable_fields:
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"Campo '{field_name}' não pode ser null.")
        return self


class Product(ProductBase):
    id: str
    createdAt: datetime
    updatedAt: datetime


class ProductList(BaseModel):
    items: list[Product]
    total: int
    limit: int
    offset: int

    model_config = ConfigDict(extra="forbid")
