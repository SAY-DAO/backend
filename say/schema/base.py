from pydantic import BaseModel as PydanticBase

from say.helpers import to_camel


class BaseModel(PydanticBase):
    
    @classmethod
    def fields(cls):
        return cls.__fields__.keys()

    @classmethod
    def from_query(cls, q):
        return cls(**q._asdict())

    @classmethod
    def from_query_list(cls, q):
        for row in q:
            yield cls.from_query(row)


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
