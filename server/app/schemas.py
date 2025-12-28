# Data shapes: defines input and output shapes (Pydantic models)

from pydantic import BaseModel
from decimal import Decimal
from typing import List


# it defines exactly what the data the client should send while registering.
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class HoldingCreate(BaseModel):
    ticker: str
    shares: Decimal
    buy_price: Decimal


class HoldingOut(BaseModel):
    id: int
    ticker: str
    shares: Decimal
    buy_price: Decimal
    current_price: Decimal | None = None
    # optional and default value is None
    market_cap: Decimal | None = None
    change_percent: float | None = None
    gain_loss: Decimal | None = None
    gain_loss_percent: float | None = None

    class Config:
        from_attributes = True


class PortfolioOut(BaseModel):
    total_value: Decimal
    total_cost: Decimal
    total_gain_loss: Decimal
    total_gain_loss_percent: float
    holdings: List[HoldingOut]
