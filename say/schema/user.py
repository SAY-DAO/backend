from pydantic import constr, BaseModel

from say.validations import USERNAME_PATTERN


class UsernameSchema(BaseModel):
    username: constr(regex=USERNAME_PATTERN)


class NewUserSchema(UsernameSchema):
    pass
