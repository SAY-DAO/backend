from . import *

"""
User Model
"""


class UserModel(base):
    __tablename__ = 'user'

    Id = Column(Integer, nullable=False, primary_key=True, unique=True)
    FirstName = Column(String, nullable=False)
    LastName = Column(String, nullable=False)
    UserName = Column(String, nullable=False)
    Credit = Column(Integer, nullable=False, default=0)
    AvatarUrl = Column(String, nullable=True)
    FlagUrl = Column(String, nullable=True)
    PhoneNumber = Column(String, nullable=False)
    EmailAddress = Column(String, nullable=True)
    Gender = Column(Boolean, nullable=True)
    City = Column(Integer, nullable=False)
    Country = Column(Integer, nullable=False)
    IsDeleted = Column(Boolean, nullable=False, default=False)
    CreatedAt = Column(Date, nullable=False)
    LastUpdate = Column(Date, nullable=False)
    BirthDate = Column(Date, nullable=True)
    BirthPlace = Column(String, nullable=True)
    LastLogin = Column(Date, nullable=False)
    Password = Column(String, nullable=False)
    SpentCredit = Column(Integer, nullable=False, default=0)
    DoneNeedCount = Column(Integer, nullable=False, default=0)
