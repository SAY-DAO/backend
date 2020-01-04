from sqlalchemy import Column, ForeignKey, String, Integer, Date, Boolean, \
    Text, Numeric, DateTime, FLOAT
from sqlalchemy.orm import relationship, synonym, scoped_session, sessionmaker
from sqlalchemy import inspect, or_, not_, and_, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import ASSOCIATION_PROXY
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.sql.schema import MetaData

from say.api import db
from say.date import *

session_factory = sessionmaker(db)
session = scoped_session(session_factory)
metadata = MetaData(
    naming_convention={
        "ix": "%(column_0_label)s_idx",
        "uq": "%(table_name)s_%(column_0_name)s_key",
        "ck": "%(table_name)s_%(constraint_name)s_check",
        "fk": "%(table_name)s_%(column_0_name)s_%(referred_table_name)s_fkey",
        "pk": "%(table_name)s_pkey"
    }
)
base = declarative_base(metadata=metadata)

from .activity_model import ActivityModel
from .child_model import ChildModel
from .child_need_model import ChildNeedModel
from .family_model import FamilyModel
from .need_family_model import NeedFamilyModel
from .need_model import NeedModel
from .ngo_model import NgoModel
from .payment_model import PaymentModel
from .privilege_model import PrivilegeModel
from .revoked_token_model import RevokedTokenModel
from .social_worker_model import SocialWorkerModel
from .user_family_model import UserFamilyModel
from .user_model import UserModel
from .verify_model import VerifyModel


# this function converts an object to a python dictionary
def obj_to_dict(obj, relationships=False):
    if isinstance(obj, dict):
        return obj

    result = {}
    for c in columns(obj, relationships):
        key, value = c.key, getattr(obj, c.key)

        if isinstance(value, list):
            result[key] = [obj_to_dict(item) for item in value]

        elif isinstance(value, base):
            result[key] = obj_to_dict(value)

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
                or (not synonyms and k in mapper.synonyms) \
                or (not composites and k in mapper.composites):
            continue

        yield getattr(cls, k)


