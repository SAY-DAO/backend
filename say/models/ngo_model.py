from sqlalchemy.ext.hybrid import hybrid_property
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

from .child_model import Child
from .social_worker_model import SocialWorker


"""
NGO Model
"""


class Ngo(base, Timestamp):
    __tablename__ = "ngo"

    id = Column(Integer, primary_key=True, nullable=False, unique=True)

    # coordinatorId = Column(Integer, ForeignKey('social_worker.id'), nullable=True)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=False)

    # country = Column(Integer, nullable=False)
    # city = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    postalAddress = Column(Text, nullable=False)
    emailAddress = Column(String, nullable=False)
    phoneNumber = Column(String, nullable=False)
    website = Column(String, nullable=True)
    logoUrl = Column(ResourceURL, nullable=False)
    balance = Column(Integer, nullable=False, default=0)
    # childrenCount = Column(Integer, nullable=False, default=0)
    # currentChildrenCount = Column(Integer, nullable=False, default=0)
    registerDate = Column(DateTime, nullable=False)
    isActive = Column(Boolean, nullable=False, default=True)
    isDeleted = Column(Boolean, nullable=False, default=False)

    socialWorkerCount = column_property(
        select([coalesce(func.count(1), 0,)]).where(
            SocialWorker.ngo_id == id,
        )
    )

    currentSocialWorkerCount = column_property(
        select([coalesce(func.count(1), 0,)]).where(
            and_(
                SocialWorker.ngo_id == id,
                SocialWorker.is_active.is_(True),
                SocialWorker.is_deleted.is_(False),
            )
        )
    )

    childrenCount = column_property(
        select([coalesce(func.count(1), 0,)]).where(
            and_(
                Child.id_ngo == id,
            )
        )
    )

    currentChildrenCount = column_property(
        select([coalesce(func.count(1), 0,)]).where(
            and_(
                Child.id_ngo == id,
                Child.isDeleted.is_(False),
                Child.isMigrated.is_(False),
            )
        )
    )

    coordinators = relationship(
        'SocialWorker',
        primaryjoin='''and_(
            SocialWorker.ngo_id==Ngo.id,
            SocialWorker.is_coordinator.is_(True),
            SocialWorker.is_deleted.is_(False),
            SocialWorker.is_active.is_(True),
        )''',
    )

    _city = relationship('City', foreign_keys=city_id, lazy='selectin')

    @hybrid_property
    def cityId(self):
        return self.city_id

    @hybrid_property
    def city(self):
        return self._city
