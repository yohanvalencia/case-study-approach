from datetime import date
from decimal import Decimal

from pydantic import BaseModel, field_validator


class Transaction(BaseModel):
    transaction_id: int
    customer_id: int
    transaction_date: date
    product_id: int
    product_name: str
    quantity: int
    price: Decimal
    tax: Decimal

    @field_validator("customer_id", "quantity", mode="before")
    @classmethod
    def coerce_to_int(cls, value: str) -> int:
        # The CSV stores these as floats (e.g. "501.0")
        return int(float(value))
