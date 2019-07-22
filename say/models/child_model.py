from . import *

"""
Child Model
"""


class ChildModel(base):
    __tablename__ = 'child'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
    FirstName = Column(String, nullable=True)
    LastName = Column(String, nullable=True)
    SayName = Column(String, nullable=False)
    PhoneNumber = Column(String, nullable=False)
    Nationality = Column(String, nullable=True)
    Country = Column(Integer, nullable=False)
    City = Column(Integer, nullable=False)
    AvatarUrl = Column(String, nullable=False)
    Gender = Column(Boolean, nullable=False)
    Bio = Column(Text, nullable=False)
    BioSummary = Column(Text, nullable=False)
    VoiceUrl = Column(String, nullable=False)
    BirthPlace = Column(String, nullable=True)
    BirthDate = Column(Date, nullable=True)
    Address = Column(Text, nullable=True)
    HousingStatus = Column(String, nullable=True)
    FamilyCount = Column(Integer, nullable=True)
    SayFamilyCount = Column(Integer, nullable=False, default=0)
    Education = Column(String, nullable=True)
    Status = Column(Integer, nullable=True)  # happy, sad, etc
    DoneNeedCount = Column(Integer, nullable=False, default=0)
    NgoId = Column(Integer, nullable=False)
    SocialWorkerId = Column(Integer, nullable=False)
    SpentCredit = Column(Integer, nullable=False, default=0)
    CreatedAt = Column(Date, nullable=False)
    LastUpdate = Column(Date, nullable=False)
    IsDeleted = Column(Boolean, nullable=False, default=False)
    IsConfirmed = Column(Boolean, nullable=False, default=False)
    HasFamily = Column(Boolean, nullable=False, default=False)
    ConfirmUser = Column(Integer, nullable=True)
    ConfirmDate = Column(Date, nullable=True)
    GeneratedCode = Column(String, nullable=True)
