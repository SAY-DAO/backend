from typing import Optional
from pydantic import constr, validator

from say.schema.base import CamelModel
from say.validations import VALID_ROLES


class NewInvitationSchema(CamelModel):
    family_id: int
    role: Optional[int] = None
    text: Optional[constr(max_length=128)]

    @validator('role')
    def name_must_contain_space(cls, role):
        if role and role not in VALID_ROLES:
            raise ValueError('invalid role')

        return role
