from typing import Optional

from pydantic import constr
from pydantic.class_validators import validator

from say.models.invite.invitation import TEXT_LENGHT
from say.schema.base import CamelModel
from say.schema.child import ChildSchema
from say.schema.family import JoinFamilySchema
from say.validations import VALID_ROLES


class NewInvitationSchema(CamelModel):
    family_id: int
    role: Optional[int] = None
    text: Optional[constr(max_length=TEXT_LENGHT)]

    @validator('role')
    def name_must_contain_space(cls, role):
        if role and role not in VALID_ROLES:
            raise ValueError('invalid role')

        return role


class NewInvitationSchemaV3(JoinFamilySchema):
    text: Optional[constr(max_length=TEXT_LENGHT)]


class InvitationSchemaV3(CamelModel):
    role: int = None
    inviter_id: int = None
    family_id: int
    text: str = None
    token: str
    link: str
    link_v3: str
    child: ChildSchema

    class Config:
        orm_mode = True
