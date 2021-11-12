from say.orm.types import ResourceURL

from . import *


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
    logoUrl = Column(Unicode, nullable=False)
    balance = Column(Integer, nullable=False, default=0)
    socialWorkerCount = Column(Integer, nullable=False, default=0)
    currentSocialWorkerCount = Column(Integer, nullable=False, default=0)
    childrenCount = Column(Integer, nullable=False, default=0)
    currentChildrenCount = Column(Integer, nullable=False, default=0)
    registerDate = Column(DateTime, nullable=False)
    isActive = Column(Boolean, nullable=False, default=True)
    isDeleted = Column(Boolean, nullable=False, default=False)

    coordinator = relationship(
        'SocialWorker',
        foreign_keys=coordinatorId,
        uselist=False,
    )
