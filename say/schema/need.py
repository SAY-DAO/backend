from .base import CamelModel


class AllNeedQuerySchema(CamelModel):
    is_done: bool = None
    is_confirmed: bool = None
    status: int = None
    ngo_id: int = None
    is_reported: bool = None
    type: int = None
    is_child_confirmed: bool = None
