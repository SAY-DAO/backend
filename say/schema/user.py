from pydantic import constr, BaseModel

from say.constants import DEFAULT_AVATAR_URI
from say.schema.base import CamelModel
from say.validations import USERNAME_PATTERN


class UserNameSchema(BaseModel):
    username: constr(regex=USERNAME_PATTERN)


class NewUserSchema(UserNameSchema):
    pass


class UserSearchSchema(CamelModel):
    user_name: str
    avatar_url: str

