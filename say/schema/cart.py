from typing import List

from pydantic.types import conint

from say.config import configs

from .base import CamelModel


class CartNeedInputSchema(CamelModel):
    need_id: int
    amount: conint(ge=configs.MIN_BANK_AMOUNT) = None
    donation: conint(ge=0) = 0


class CartNeedDeleteSchema(CamelModel):
    need_id: int


class CartNeedSchema(CartNeedInputSchema):
    id: int
    name: str
    title: str
    cost: int
    paid: int

    class Config:
        orm_mode = True


class CartSchema(CamelModel):
    id: int
    user_id: int
    need_amount: int
    donation_amount: int
    total_amount: int
    needs: List[CartNeedSchema] = []

    class Config:
        orm_mode = True
