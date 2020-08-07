from typing import Optional
from pydantic import constr

from say.schema.base import CamelModel


class NewInvitationSchema(CamelModel):
    family_id: int
    role: Optional[int] = None
    text: Optional[constr(max_length=128)]
