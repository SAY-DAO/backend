from say.models.search import SearchType
from say.schema.child import ChildSchemaV3

from .base import CamelModel


class SearchSchema(CamelModel):
    type: SearchType
    token: str
    child: ChildSchemaV3

    class Config:
        orm_mode = True
        use_enum_values = True
