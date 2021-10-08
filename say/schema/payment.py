from pydantic.types import conint

from .base import CamelModel


class NewPaymentSchema(CamelModel):
    need_id: int
    amount: conint(gt=0)
    donate: conint(gt=0) = 0
    use_credit: bool = True
