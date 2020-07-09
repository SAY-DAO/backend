from pydantic import constr, BaseModel


class NewUserSchema(BaseModel):
    username: constr(regex='[A-Za-z0-9][.A-Za-z0-9]{3,11}$')
