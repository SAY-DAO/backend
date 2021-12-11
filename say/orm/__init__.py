import enum
from decimal import Decimal

import pydantic
from babel import Locale
from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy import inspect
from sqlalchemy.ext.associationproxy import ASSOCIATION_PROXY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import MetaData
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum import plugins
from sqlalchemy_utils import Country
from sqlalchemy_utils import PhoneNumber

from say.orm.versioning import flask_versioning_plugin

from .base import BaseModel
from .base import columns


make_versioned(
    user_cls='SocialWorker',
    plugins=[flask_versioning_plugin, plugins.TransactionChangesPlugin()],
)

metadata = MetaData(
    naming_convention={
        "ix": "%(column_0_label)s_idx",
        "uq": "%(table_name)s_%(column_0_name)s_key",
        "ck": "%(table_name)s_%(constraint_name)s_check",
        "fk": "%(table_name)s_%(column_0_name)s_%(referred_table_name)s_fkey",
        "pk": "%(table_name)s_pkey",
    }
)

base: BaseModel = declarative_base(cls=BaseModel, metadata=metadata)

session_factory = sessionmaker(
    autoflush=False,
    autocommit=False,
    expire_on_commit=True,
    twophase=False,
)
session = scoped_session(session_factory)


def create_engine(url, *args, **kwargs):
    return sa_create_engine(url, pool_pre_ping=True, *args, **kwargs)


def setup_schema(session_):
    engine = session_.bind
    engine.execute('CREATE EXTENSION IF NOT EXISTS HSTORE;')
    metadata.create_all(bind=engine)


def init_model(engine):
    """
    Call me before using any of the tables or classes in the model.
    :param engine: SqlAlchemy engine to bind the session
    :return:
    """
    session.remove()
    session.configure(bind=engine)


# this function converts an object to a python dictionary
def obj_to_dict(obj, relationships=False, proxys=False):
    if isinstance(obj, dict):
        return obj

    if isinstance(obj, tuple) or isinstance(obj, list):
        return [obj_to_dict(x) for x in obj]

    elif isinstance(obj, pydantic.BaseModel):
        return obj.dict(by_alias=True)

    if not isinstance(obj, base):
        return obj

    result = {}
    for k, c in columns(obj, relationships, proxys=proxys):
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

        elif isinstance(value, Decimal):
            result[key] = int(value)

        else:
            result[key] = value
    return result


def safe_commit(session):
    try:
        session.commit()
    except:
        session.rollback()
        raise
