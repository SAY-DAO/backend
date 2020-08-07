import os
import enum
import functools
from typing import Optional

from babel import Locale
from flask import request, g
from sqlalchemy import Column, ForeignKey, String, Integer, Date, Boolean, \
    Text, Numeric, DateTime, FLOAT, Unicode, Enum, inspect, or_, not_, and_, \
    func, select, event
from sqlalchemy.orm import relationship, synonym, scoped_session, \
    sessionmaker, object_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import ASSOCIATION_PROXY
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.sql.schema import MetaData
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.functions import coalesce
from sqlalchemy_utils import TranslationHybrid, aggregated, observes, \
    PhoneNumber, Country
from sqlalchemy_utils.models import Timestamp
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool


from say.api import db
from say.date import *
from say.langs import LANGS
from say.locale import get_locale, DEFAULT_LOCALE
from say.formatters import int_formatter, expose_datetime
from say.orm import obj_to_dict, base


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


session_factory = sessionmaker(
    db,
    autoflush=False,
    autocommit=False,
    expire_on_commit=True,
    twophase=False,
)

session = scoped_session(session_factory)


# FIXME: CIRITICAL
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


from .activity_model import Activity
from .child_model import Child
from .child_need_model import ChildNeed
from .family_model import Family
from .need_family_model import NeedFamily
from .need_model import Need
from .ngo_model import Ngo
from .payment_model import Payment
from .privilege_model import Privilege
from .revoked_token_model import RevokedToken
from .social_worker_model import SocialWorker
from .user_family_model import UserFamily
from .user_model import User
from .verify_model import PhoneVerification, EmailVerification, Verification
from .reset_password_model import ResetPassword
from .child_migration_model import ChildMigration
from .invite import Invitation, InvitationAccept
from .change_cost import *


# Handling mutliprocess engine
# https://docs.sqlalchemy.org/en/13/core/pooling.html#using-connection-pools-with-multiprocessing
@event.listens_for(db, "connect")
def connect(dbapi_connection, connection_record):
    connection_record.info['pid'] = os.getpid()

@event.listens_for(db, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    pid = os.getpid()
    if connection_record.info['pid'] != pid:
        connection_record.connection = connection_proxy.connection = None
        raise exc.DisconnectionError(
                "Connection record belongs to pid %s, "
                "attempting to check out in pid %s" %
                (connection_record.info['pid'], pid)
        )

