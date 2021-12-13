import enum
import functools
import os
from typing import Optional

from babel import Locale
from flask import g
from flask import request
from sqlalchemy import FLOAT
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Unicode
from sqlalchemy import and_
from sqlalchemy import event
from sqlalchemy import exc
from sqlalchemy import func
from sqlalchemy import inspect
from sqlalchemy import not_
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.ext.associationproxy import ASSOCIATION_PROXY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import configure_mappers
from sqlalchemy.orm import object_session
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import synonym
from sqlalchemy.pool import Pool
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql.schema import MetaData
from sqlalchemy_utils import Country
from sqlalchemy_utils import PhoneNumber
from sqlalchemy_utils import TranslationHybrid
from sqlalchemy_utils import aggregated
from sqlalchemy_utils import observes
from sqlalchemy_utils.models import Timestamp

from say.date import *
from say.exceptions import HTTPException
from say.formatters import expose_datetime
from say.formatters import int_formatter
from say.langs import LANGS
from say.locale import DEFAULT_LOCALE
from say.locale import get_locale
from say.orm import base
from say.orm import obj_to_dict
from say.orm import session


# FIXME: CIRITICAL
def commit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        try:
            result = func(*args, **kwargs)

            if isinstance(result, tuple) and result[1] >= 300:
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
from .base_user import BaseUser
from .cart import Cart
from .cart import CartNeed
from .cart import CartPayment
from .change_cost import *
from .child_migration_model import ChildMigration
from .child_model import Child
from .child_need_model import ChildNeed
from .family_model import Family
from .invite import Invitation
from .invite import InvitationAccept
from .nakama import *
from .need_family_model import NeedFamily
from .need_model import Need
from .ngo_model import Ngo
from .payment_model import Payment
from .privilege_model import Privilege
from .receipt import NeedReceipt
from .receipt import Receipt
from .reset_password_model import ResetPassword
from .search import Search
from .social_worker_model import SocialWorker
from .user_family_model import UserFamily
from .user_model import User
from .verify_model import EmailVerification
from .verify_model import PhoneVerification
from .verify_model import Verification


configure_mappers()  # You need to call this after the import
