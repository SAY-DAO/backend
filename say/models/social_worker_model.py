from say.models.ngo_model import NgoModel
from say.models.privilege_model import PrivilegeModel
from . import *

"""
SocialWorker Model
"""


class SocialWorkerModel(base):
    __tablename__ = 'social_worker'

    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    generatedCode = Column(String, nullable=False)
    id_ngo = Column(Integer, ForeignKey(NgoModel.id), nullable=False)
    country = Column(Integer, nullable=True)
    city = Column(Integer, nullable=True)
    id_type = Column(Integer, ForeignKey(PrivilegeModel.id), nullable=False)
    firstName = Column(String, nullable=True)
    lastName = Column(String, nullable=False)
    userName = Column(String, nullable=False)  # ngoName + "-sw" + generatedCode
    password = Column(String, nullable=False)
    birthCertificateNumber = Column(String, nullable=True)
    idNumber = Column(String, nullable=False)
    idCardUrl = Column(String, nullable=True)
    passportNumber = Column(String, nullable=True)
    passportUrl = Column(String, nullable=True)
    gender = Column(Boolean, nullable=False)
    birthDate = Column(Date, nullable=True)
    phoneNumber = Column(String, nullable=False)
    emergencyPhoneNumber = Column(String, nullable=False)
    emailAddress = Column(String, nullable=False)
    telegramId = Column(String, nullable=False)
    postalAddress = Column(Text, nullable=True)
    avatarUrl = Column(String, nullable=False)
    childCount = Column(Integer, nullable=False, default=0)
    currentChildCount = Column(Integer, nullable=False, default=0)
    needCount = Column(Integer, nullable=False, default=0)
    currentNeedCount = Column(Integer, nullable=False, default=0)
    bankAccountNumber = Column(String, nullable=True)
    bankAccountShebaNumber = Column(String, nullable=True)
    bankAccountCardNumber = Column(String, nullable=True)
    registerDate = Column(Date, nullable=False)
    lastUpdateDate = Column(Date, nullable=False)
    lastLoginDate = Column(Date, nullable=False)
    lastLogoutDate = Column(Date, nullable=True)
    isActive = Column(Boolean, nullable=False, default=True)
    isDeleted = Column(Boolean, nullable=False, default=False)

    privilege = relationship('PrivilegeModel', foreign_keys='SocialWorkerModel.id_type')
    ngo = relationship('NgoModel', foreign_keys='SocialWorkerModel.id_ngo')
