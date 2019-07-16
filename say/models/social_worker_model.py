from say.models.ngo_model import NgoModel
from say.models.privilege_model import PrivilegeModel
from . import *

"""
SocialWorker Model
"""


class SocialWorkerModel(base):
    __tablename__ = 'social_worker'

    Id = Column(Integer, primary_key=True, nullable=False, unique=True)
    GeneratedCode = Column(String, nullable=False)
    Id_ngo = Column(Integer, ForeignKey(NgoModel.Id), nullable=False)
    Country = Column(Integer, nullable=False)
    City = Column(Integer, nullable=False)
    Id_type = Column(Integer, ForeignKey(PrivilegeModel.Id), nullable=False)
    FirstName = Column(String, nullable=False)
    LastName = Column(String, nullable=False)
    UserName = Column(String, nullable=False)
    Password = Column(String, nullable=False)
    BirthCertificateNumber = Column(String, nullable=False)
    IdNumber = Column(String, nullable=False)
    IdCardUrl = Column(String, nullable=False)
    PassportNumber = Column(String, nullable=False)
    PassportUrl = Column(String, nullable=False)
    Gender = Column(Boolean, nullable=False)
    BirthDate = Column(Date, nullable=False)
    PhoneNumber = Column(String, nullable=False)
    EmergencyPhoneNumber = Column(String, nullable=False)
    EmailAddress = Column(String, nullable=False)
    TelegramId = Column(String, nullable=False)
    PostalAddress = Column(Text, nullable=False)
    AvatarUrl = Column(String, nullable=False)
    ChildCount = Column(Integer, nullable=False, default=0)
    NeedCount = Column(Integer, nullable=False, default=0)
    BankAccountNumber = Column(String, nullable=False)
    BankAccountShebaNumber = Column(String, nullable=False)
    BankAccountCardNumber = Column(String, nullable=False)
    RegisterDate = Column(Date, nullable=False)
    LastUpdateDate = Column(Date, nullable=False)
    LastLoginDate = Column(Date, nullable=False)
    LastLogoutDate = Column(Date, nullable=True)
    IsActive = Column(Boolean, nullable=False, default=True)
    IsDeleted = Column(Boolean, nullable=False, default=False)

    privilege = relationship('PrivilegeModel', foreign_keys='SocialWorkerModel.Id_type')
    ngo = relationship('NgoModel', foreign_keys='SocialWorkerModel.Id_ngo')
