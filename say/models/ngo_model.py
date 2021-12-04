from sqlalchemy.orm import column_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.sql.sqltypes import Text
from sqlalchemy_utils.models import Timestamp

from say.orm import base
from say.orm.types import ResourceURL

from .social_worker_model import SocialWorker


"""
NGO Model
"""


class Ngo(base, Timestamp):
    __tablename__ = "ngo"

    id = Column(Integer, primary_key=True, nullable=False, unique=True)

    coordinatorId = Column(Integer, ForeignKey('social_worker.id'), nullable=True)

    country = Column(Integer, nullable=False)
    city = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    postalAddress = Column(Text, nullable=False)
    emailAddress = Column(String, nullable=False)
    phoneNumber = Column(String, nullable=False)
    website = Column(String, nullable=True)
    logoUrl = Column(ResourceURL, nullable=False)
    balance = Column(Integer, nullable=False, default=0)
    childrenCount = Column(Integer, nullable=False, default=0)
    currentChildrenCount = Column(Integer, nullable=False, default=0)
    registerDate = Column(DateTime, nullable=False)
    isActive = Column(Boolean, nullable=False, default=True)
    isDeleted = Column(Boolean, nullable=False, default=False)

    socialWorkerCount = column_property(
        select([coalesce(func.count(1), 0,)]).where(
            SocialWorker.id_ngo == id,
        )
    )

    currentSocialWorkerCount = column_property(
        select([coalesce(func.count(1), 0,)]).where(
            and_(
                SocialWorker.id_ngo == id,
                SocialWorker.isActive.is_(True),
                SocialWorker.isDeleted.is_(False),
            )
        )
    )

    coordinator = relationship(
        'SocialWorker',
        foreign_keys=coordinatorId,
        uselist=False,
    )
