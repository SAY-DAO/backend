from typing import List
from typing import Optional

from say.schema.base import BaseModel


class UserSchema(BaseModel):
    id: int
    userName: str
    firstName: str
    lastName: str
    avatarUrl: Optional[str] = None


class ChildSchema(BaseModel):
    id: int
    avatarUrl: str
    done_needs_count: int
    sayName: str
    spent_credit: int


class DashboardSchema(BaseModel):
    user: UserSchema
    children: List[ChildSchema]
