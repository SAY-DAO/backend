from typing import Optional
from pydantic import constr, BaseModel

from say.validations import USERNAME_PATTERN


class AcceptInvitationSchema(BaseModel):
    role: int


class NewPendingInvitationSchema(BaseModel):
    invited_username: constr(regex=USERNAME_PATTERN)
    family_id: int
    role: Optional[int]
