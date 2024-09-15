from datetime import datetime

from pydantic.types import conint

from .base import CamelModel


class NewPaymentSchema(CamelModel):
    need_id: int
    amount: conint(gt=0)
    donate: conint(ge=0) = 0
    use_credit: bool = True
    gateWay: int = 1

class PaymentSchema(CamelModel):
    id: int
    id_need: int
    id_user: int
    verified: datetime
    need_amount: int
    donation_amount: int
    credit_amount: int
    use_credit: bool = True
