from datetime import datetime
from typing import List

from pydantic.types import conint

from .base import CamelModel


class CartNeedInputSchema(CamelModel):
    need_id: int


class CartNeedSchema(CartNeedInputSchema):
    id: int
    name: str
    title: str
    cost: int
    paid: int
    amount: int
    created: datetime
    deleted: datetime = None

    class Config:
        orm_mode = True


class CartSchema(CamelModel):
    id: int
    user_id: int
    total_amount: int
    needs: List[CartNeedSchema] = []
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True


class CartPaymentInSchema(CamelModel):
    donation: conint(ge=0) = 0
    use_credit: bool = True


class CartPaymentSchema(CamelModel):
    id: int
    cart_id: int
    order_id: str
    bank_amount: int
    credit_amount: int
    donation_amount: int
    needs_amount: int
    total_amount: int
    gateway_payment_id: str = None
    gateway_track_id: str = None
    link: str = None
    verified: datetime = None
    card_no: str = None
    hashed_card_no: str = None
    transaction_date: datetime = None

    class Config:
        orm_mode = True
