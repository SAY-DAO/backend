from datetime import date
from datetime import datetime
from typing import List

from pydantic import Field

from .base import BaseModel
from .base import CamelModel


class FamilyMembers(CamelModel):
    username: str
    avatar_url: str = None
    is_participated: bool

    class Config:
        orm_mode = True


class Family(CamelModel):
    current_members: List[FamilyMembers]

    class Config:
        orm_mode = True


class ChildWithFamily(BaseModel):
    id: int
    avatarUrl: str
    sayName: str
    family: Family

    class Config:
        orm_mode = True
