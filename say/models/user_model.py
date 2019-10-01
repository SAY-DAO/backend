from . import *

"""
User Model
"""


class UserModel(base):
    __tablename__ = "user"

    id = Column(Integer, nullable=False, primary_key=True, unique=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    userName = Column(String, nullable=False, unique=True)
    credit = Column(Integer, nullable=False, default=0)
    avatarUrl = Column(String, nullable=True)
    flagUrl = Column(String, nullable=True)
    phoneNumber = Column(String, nullable=True)
    emailAddress = Column(String, nullable=True)
    gender = Column(Boolean, nullable=True)  # real country codes
    city = Column(Integer, nullable=False)  # 1:tehran | 2:karaj
    country = Column(Integer, nullable=False)
    isDeleted = Column(Boolean, nullable=False, default=False)
    isVerified = Column(Boolean, nullable=False, default=False)
    createdAt = Column(Date, nullable=False)
    lastUpdate = Column(Date, nullable=False)
    birthDate = Column(Date, nullable=True)
    birthPlace = Column(Integer, nullable=True)  # 1:tehran | 2:karaj
    lastLogin = Column(Date, nullable=False)
    password = Column(String, nullable=False)
    token = Column(String, nullable=True)
    spentCredit = Column(Integer, nullable=False, default=0)
    doneNeedCount = Column(Integer, nullable=False, default=0)
