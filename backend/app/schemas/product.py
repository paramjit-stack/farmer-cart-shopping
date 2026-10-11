from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class ProductInput(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    category: str = Field(min_length=1, max_length=100)
    farmer_name: str = Field(min_length=1, max_length=150)
    description: str = ""
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    available_quantity: int = Field(ge=0)
    image_url: str | None = Field(default=None, max_length=500)
    status: Literal["active", "inactive"] = "active"

class ProductOutput(ProductInput):
    id: int
    model_config = ConfigDict(from_attributes=True)

class StockInput(BaseModel):
    available_quantity: int = Field(ge=0)

class StatusInput(BaseModel):
    status: Literal["active", "inactive"]
