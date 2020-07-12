import enum
import functools
import os

from babel import Locale
from sqlalchemy import inspect, event, exc
from sqlalchemy.ext.associationproxy import ASSOCIATION_PROXY
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.pool import Pool
from sqlalchemy_utils import PhoneNumber, Country, TranslationHybrid
from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.schema import MetaData
from sqlalchemy.ext.declarative import declarative_base

from .base import BaseModel
from ..config import config
from ..locale import get_locale, DEFAULT_LOCALE


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


def create_engine(url, *args, **kwargs):
    return sa_create_engine(url, pool_pre_ping=True, *args, **kwargs)


session_factory = sessionmaker(
    autoflush=False,
    autocommit=False,
    expire_on_commit=True,
    twophase=False,
)
session = scoped_session(session_factory)


# this function converts an object to a python dictionary
def obj_to_dict(obj, relationships=False):
    if isinstance(obj, dict):
        return obj

    if isinstance(obj, tuple) or isinstance(obj, list):
        return [obj_to_dict(x) for x in obj]

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


def init_model(engine):
    """
    Call me before using any of the tables or classes in the model.
    :param engine: SqlAlchemy engine to bind the session
    :return:
    """
    session.remove()
    session.configure(bind=engine)


def setup_schema(session_=session):
    engine = session_.bind
    engine.execute('CREATE EXTENSION IF NOT EXISTS HSTORE;')
    metadata.create_all(bind=engine)


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        # connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()


def commit(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        try:
            result = func(*args, **kwargs)

            if isinstance(result, tuple):
                session.rollback()
                return result

            session.commit()
            return result

        except Exception as ex:
            session.rollback()
            raise

    return wrapper


translation_hybrid = TranslationHybrid(
    current_locale=get_locale,
    default_locale=DEFAULT_LOCALE,
)


# @event.listens_for(engine, "connect")
# def connect(dbapi_connection, connection_record):
#     connection_record.info['pid'] = os.getpid()
#
#
# @event.listens_for(engine, "checkout")
# def checkout(dbapi_connection, connection_record, connection_proxy):
#     pid = os.getpid()
#     if connection_record.info['pid'] != pid:
#         connection_record.connection = connection_proxy.connection = None
#         raise exc.DisconnectionError(
#                 "Connection record belongs to pid %s, "
#                 "attempting to check out in pid %s" %
#                 (connection_record.info['pid'], pid)
#         )