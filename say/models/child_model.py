from say.models.ngo_model import NgoModel
from say.models.social_worker_model import SocialWorkerModel
from . import *

"""
Child Model
"""


class ChildModel(base):
    __tablename__ = "child"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    firstName = Column(String, nullable=True)
    lastName = Column(String, nullable=True)
    sayName = Column(String, nullable=False)
    phoneNumber = Column(Integer, nullable=False)
    nationality = Column(Integer, nullable=True)  # 1:iranian | 2:afghan
    country = Column(
        Integer, nullable=False
    )  # 98:iran | 93:afghanistan | ... (real country codes)
    city = Column(Integer, nullable=False)  # 1:tehran | 2:karaj
    avatarUrl = Column(String, nullable=False)
    gender = Column(Boolean, nullable=False)  # true:male | false:female
    bio = Column(Text, nullable=False)
    bioSummary = Column(Text, nullable=False)
    voiceUrl = Column(String, nullable=False)
    birthPlace = Column(Text, nullable=True)  # 1:tehran | 2:karaj
    birthDate = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    housingStatus = Column(
        Integer, nullable=True
    )  # 0:homeless | 1:rent | 2:has home | 3:with relatives
    familyCount = Column(Integer, nullable=True)
    sayFamilyCount = Column(Integer, nullable=False, default=0)
    education = Column(
        Integer, nullable=True
    )  # -1:uneducated | 0:pre-school | 1:1st grade | 2:2nd grade | ...
    status = Column(Integer, nullable=True)  # happy, sad, etc
    doneNeedCount = Column(Integer, nullable=False, default=0)
    id_ngo = Column(Integer, ForeignKey(NgoModel.id), nullable=False)
    id_social_worker = Column(Integer, ForeignKey(SocialWorkerModel.id), nullable=False)
    spentCredit = Column(Integer, nullable=False, default=0)
    createdAt = Column(Date, nullable=False)
    lastUpdate = Column(Date, nullable=False)
    isDeleted = Column(Boolean, nullable=False, default=False)
    isConfirmed = Column(Boolean, nullable=False, default=False)
    confirmUser = Column(Integer, nullable=True)
    confirmDate = Column(Date, nullable=True)
    generatedCode = Column(String, nullable=False)
    isMigrated = Column(Boolean, nullable=False, default=False)
    migratedId = Column(Integer, nullable=True)
    migrateDate = Column(Date, nullable=True)

    ngo_relation = relationship("NgoModel", foreign_keys="ChildModel.id_ngo")
    social_worker_relation = relationship(
        "SocialWorkerModel", foreign_keys="ChildModel.id_social_worker"
    )
