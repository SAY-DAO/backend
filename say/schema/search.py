from say.models.search import SearchType
from say.schema.child import ChildSchema

from .base import CamelModel


class SearchSchema(CamelModel):
    type: SearchType
    token: str
    child: ChildSchema

    class Config:
        orm_mode = True
        use_enum_values = True
