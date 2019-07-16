from . import *

"""
NGO Model
"""


class NgoModel(base):
    __tablename__ = 'ngo'

    Id = Column(Integer, primary_key=True, nullable=False, unique=True)
    Country = Column(Integer, nullable=False)
    City = Column(Integer, nullable=False)
    CoordinatorId = Column(Integer, nullable=False)
    Name = Column(String, nullable=False)
    PostalAddress = Column(Text, nullable=False)
    EmailAddress = Column(String, nullable=False)
    PhoneNumber = Column(String, nullable=False)
    LogoUrl = Column(String, nullable=False)
    Balance = Column(Integer, nullable=False)
    SocialWorkerCount = Column(Integer, nullable=False, default=0)
    ChildrenCount = Column(Integer, nullable=False, default=0)
    RegisterDate = Column(Date, nullable=False)
    LastUpdateDate = Column(Date, nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    IsDeleted = Column(Boolean, nullable=False, default=False)
