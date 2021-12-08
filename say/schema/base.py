from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple

import babel
import ujson
from pydantic import BaseModel as PydanticBase
from pydantic.main import BaseModel
from pydantic.main import ModelMetaclass

from say.helpers import to_camel


class BaseModel(PydanticBase):
    @classmethod
    def fields(cls):
        return cls.__fields__.keys()

    # DEPRECETED
    @classmethod
    def from_query(cls, q):
        return cls(**q._asdict())

    # DEPRECETED
    @classmethod
    def from_query_list(cls, q):
        for row in q:
            yield cls.from_query(row)

    @classmethod
    def from_query_(cls, q):
        return cls.from_orm(q)

    @classmethod
    def from_query_list_(cls, q):
        for row in q:
            yield cls.from_query_(row)

    class Config:
        orm_mode = True
        extra = 'ignore'

        json_loads = ujson.loads
        json_encoders = {
            babel.core.Locale: str,
        }


class BaseModelWithId(BaseModel):
    id: int


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class AllOptionalMeta(ModelMetaclass):
    def __new__(cls, name: str, bases: Tuple[type], namespaces: Dict[str, Any], **kwargs):
        annotations: dict = namespaces.get('__annotations__', {})

        for base in bases:
            for base_ in base.__mro__:
                if base_ is BaseModel or base_ is CamelModel or base_ is PydanticBase:
                    break

                annotations.update(base_.__annotations__)

        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]

        namespaces['__annotations__'] = annotations

        return super().__new__(cls, name, bases, namespaces, **kwargs)
