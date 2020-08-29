import enum

import pydantic
from babel import Locale
from sqlalchemy import inspect
from sqlalchemy.ext.associationproxy import ASSOCIATION_PROXY
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy_utils import PhoneNumber, Country
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import MetaData

from .base import BaseModel


metadata = MetaData(
    naming_convention={
        "ix": "%(column_0_label)s_idx",
        "uq": "%(table_name)s_%(column_0_name)s_key",
        "ck": "%(table_name)s_%(constraint_name)s_check",
        "fk": "%(table_name)s_%(column_0_name)s_%(referred_table_name)s_fkey",
        "pk": "%(table_name)s_pkey"
    }
)

base = declarative_base(cls=BaseModel, metadata=metadata)


# this function converts an object to a python dictionary
def obj_to_dict(obj, relationships=False):
    if isinstance(obj, dict):
        return obj

    if isinstance(obj, tuple) or isinstance(obj, list):
        return [obj_to_dict(x) for x in obj]

    elif isinstance(obj, pydantic.BaseModel):
        return obj.dict(by_alias=True)

    if not isinstance(obj, base):
        return obj

    result = {}
    for k, c in columns(obj, relationships):
        key, value = k, getattr(obj, k)

        if key.startswith('_'):
            continue

        elif isinstance(value, list):
            result[key] = [obj_to_dict(item) for item in value]

        elif isinstance(value, base):
            result[key] = obj_to_dict(value)

        elif isinstance(value, Locale):
            result[key] = str(value)

        elif isinstance(value, PhoneNumber):
            result[key] = value.e164

        elif isinstance(value, Country):
            result[key] = {'code': value.code, 'name': value.name}

        elif isinstance(value, enum.Enum):
            result[key] = value.name

        else:
            result[key] = value
    return result


def columns(obj, relationships=False, synonyms=True, composites=False,
                 hybrids=True):
    cls = obj.__class__

    mapper = inspect(cls)
    for k, c in mapper.all_orm_descriptors.items():

        if k == '__mapper__':
            continue

        if c.extension_type == ASSOCIATION_PROXY:
            continue

        if (not hybrids and c.extension_type == HYBRID_PROPERTY) \
                or (not relationships and k in mapper.relationships) \
                or (not synonyms and k in mapper.synonyms):
            continue

        yield k, getattr(cls, k)


