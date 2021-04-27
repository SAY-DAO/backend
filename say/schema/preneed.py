from .base import CamelModel


class PreneedSummarySchema(CamelModel):
    id: int
    name: str
    title: str = None
    cost: int
    type: int
    details: str = None
