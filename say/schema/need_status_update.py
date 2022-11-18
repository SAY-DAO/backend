from datetime import datetime

from .base import CamelModel


class NeedStatusUpdateSchema(CamelModel):
    id: int
    sw_id: int
    need_id: int
    new_status: int
    old_status: int
    created: datetime
    updated: datetime
