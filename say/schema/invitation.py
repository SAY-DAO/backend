from datetime import datetime
from typing import Optional
from pydantic import constr

from say.constants import INVITATION_REJECT_REASON_LENGTH
from say.schema.base import CamelModel
from say.validations import USERNAME_PATTERN


class NewInvitationSchema(CamelModel):
    invitee_username: Optional[constr(regex=USERNAME_PATTERN)]
    family_id: int
    role: Optional[int] = None
    text: Optional[constr(max_length=128)]


class InvitationSchema(NewInvitationSchema):
    token: str
    created: datetime
    updated: datetime
    status: str
    see_count: str


class RejectInvitationSchema(CamelModel):
    reject_reason: constr(max_length=INVITATION_REJECT_REASON_LENGTH)
