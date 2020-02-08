from sqlalchemy.dialects.postgresql import HSTORE

from . import *


"""
Child Model
"""


# TODO: why it has N family instead of one?
class ChildModel(base):
    __tablename__ = "child"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_ngo = Column(Integer, ForeignKey('ngo.id'), nullable=False)
    id_social_worker = Column(Integer, ForeignKey('social_worker.id'), nullable=False)

    firstName_translations = Column(HSTORE)
    firstName = translation_hybrid(firstName_translations)

    lastName_translations = Column(HSTORE)
    lastName = translation_hybrid(lastName_translations)

    sayname_translations = Column(HSTORE)
    sayName = translation_hybrid(sayname_translations)

    phoneNumber = Column(Integer, nullable=False)
    nationality = Column(Integer, nullable=True)  # 98:iranian | 93:afghan
    country = Column(
        Integer, nullable=False
    )  # 98:iran | 93:afghanistan | ... (real country codes) / [must be change after using real country/city api]
    city = Column(Integer, nullable=False)  # 1:tehran | 2:karaj / [must be change after using real country/city api]
    avatarUrl = Column(String, nullable=False)
    sleptAvatarUrl = Column(String, nullable=False)
    gender = Column(Boolean, nullable=False)  # true:male | false:female

    bio_translations = Column(HSTORE)
    bio = translation_hybrid(bio_translations)

    bio_summary_translations = Column(HSTORE)
    bioSummary = translation_hybrid(bio_summary_translations)

    voiceUrl = Column(String, nullable=False)
    birthPlace = Column(Text, nullable=True)  # 1:tehran | 2:karaj / [must be change after using real country/city api]
    birthDate = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    housingStatus = Column(
        Integer, nullable=True
    )  # 0:Street child | 1:Living at home | 2:Care centers
    familyCount = Column(Integer, nullable=True)
    sayFamilyCount = Column(Integer, nullable=False, default=0)
    education = Column(
        Integer, nullable=True
    )  # -3:Deprived of education | -2:Kinder garden | -1:Not attending | 0:Pre-school | 1:1st grade | 2:2nd grade | ... | 13:University
    status = Column(Integer, nullable=True)  # happy, sad, etc
    doneNeedCount = Column(Integer, nullable=False, default=0)
    spentCredit = Column(Integer, nullable=False, default=0)
    createdAt = Column(DateTime, nullable=False)
    lastUpdate = Column(DateTime, nullable=False)
    isDeleted = Column(Boolean, nullable=False, default=False)
    isConfirmed = Column(Boolean, nullable=False, default=False)
    confirmUser = Column(Integer, nullable=True)
    confirmDate = Column(Date, nullable=True)
    generatedCode = Column(String, nullable=False)
    isMigrated = Column(Boolean, nullable=False, default=False)
    migratedId = Column(Integer, nullable=True)
    migrateDate = Column(Date, nullable=True)

    needs = relationship(
        'NeedModel',
        back_populates='child',
    )
    families = relationship('FamilyModel', back_populates='child')
    ngo = relationship("NgoModel", foreign_keys="ChildModel.id_ngo")
    social_worker = relationship(
        "SocialWorkerModel",
        foreign_keys=id_social_worker,
        back_populates='children',
    )
    migrations = relationship(
        'ChildMigration',
        back_populates='child',
    )
