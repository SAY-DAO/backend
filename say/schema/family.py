from pydantic import BaseModel


class AvailableRolesSchema(BaseModel):
    username: str
