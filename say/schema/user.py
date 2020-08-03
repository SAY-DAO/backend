from pydantic import constr, BaseModel

from say.validations import USERNAME_PATTERN


class UserNameSchema(BaseModel):
    username: constr(regex=USERNAME_PATTERN)


class NewUserSchema(UserNameSchema):
    pass
