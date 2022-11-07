from pydantic import constr

from say.schema.base import CamelModel
from say.validations import USERNAME_PATTERN


class UserNameSchema(CamelModel):
    username: constr(regex=USERNAME_PATTERN)
    city_id: int = None


class NewUserSchema(UserNameSchema):
    pass


class UserSearchSchema(CamelModel):
    user_name: str
    avatar_url: str


class UpdateUserSchema(CamelModel):
    receive_email: bool = None
