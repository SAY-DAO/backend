from datetime import datetime
from typing import List, Optional

from .base import BaseModel
from .base import CamelModel
from .child import Participant


class AllNeedQuerySchema(CamelModel):
    is_done: bool = None
    is_confirmed: bool = None
    status: int = None
    ngo_id: int = None
    is_reported: bool = None
    type: int = None
    is_child_confirmed: bool = None
    unpayable: bool = None


class NeedSummary(BaseModel):
    id: int
    imageUrl: str
    name: str
    progress: str
    cost: int
    isDone: bool
    isUrgent: bool
    category: Optional[int] = None
    type: int
    participants: List[Participant] = []
    created: datetime
    doneAt: datetime = None
    unpayable: bool = None

    class Config:
        orm_mode = True


class NeedSchema(NeedSummary):
    child_id: int
    childSayName: str

    description: str
    description_translations: dict
    name_translations: dict
    details: str = None
    informations: str = None
    unpaid_cost: int
    paid: int
    donated: int
    pretty_cost: str
    pretty_paid: str
    pretty_donated: str
    receipt_count: int
    purchase_cost: int = None
    link: str = None
    affiliateLinkUrl: str = None
    isDeleted: bool
    isConfirmed: bool
    confirmUser: int = None
    confirmDate: datetime = None
    isReported: bool
    isDone: bool
    is_done: bool
    oncePurchased: bool
    doing_duration: int
    status: int
    status_description: str = None
    status_updated_at: datetime = None
    img: str = None
    title: str = None
    clean_title: str = None
    bank_track_id: str = None
    doneAt: datetime = None
    purchase_date: datetime = None
    expected_delivery_date: datetime = None
    ngo_delivery_date: datetime = None
    child_delivery_date: datetime = None
    deleted_at: datetime = None
    unconfirmed_at: datetime = None
    unavailable_from: datetime = None
    unpayable_from: datetime = None
    dkc: str = None
    type_name: str
    receipts: str = None
    updated: datetime = None

    class Config:
        orm_mode = True
