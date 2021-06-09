from datetime import datetime
from typing import List

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
