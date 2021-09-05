from pydantic import validator

from say.schema.base import CamelModel
from say.validations import VALID_ROLES


class JoinFamilySchema(CamelModel):
    family_id: int
    role: int

    @validator('role')
    def name_must_contain_space(cls, role):
        if role and role not in VALID_ROLES:
            raise ValueError('invalid role')

        return role
