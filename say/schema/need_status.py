from .base import CamelModel


class NeedStatusUpdateSchema(CamelModel):
    id: int
    need_id: int
    sw_id: int
    old_status: int
    new_status: int
