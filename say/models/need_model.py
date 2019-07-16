from . import *

"""
Need Model
"""


class NeedModel(base):
    __tablename__ = 'need'

    Id = Column(Integer, nullable=False, primary_key=True, unique=True)
    Name = Column(String, nullable=False)
    ImageUrl = Column(String, nullable=False)
    Category = Column(Integer, nullable=False)  # love, joy, etc
    IsUrgent = Column(Boolean, nullable=False)
    Description = Column(Text, nullable=False)
    DescriptionSummary = Column(Text, nullable=False)
    Cost = Column(Integer, nullable=False)
    Progress = Column(Integer, nullable=False, default=0)
    Paid = Column(Integer, nullable=False, default=0)
    AffiliateLinkUrl = Column(String, nullable=True)
    IsDone = Column(Boolean, nullable=False, default=False)
    IsDeleted = Column(Boolean, nullable=False, default=False)
    CreatedAt = Column(Date, nullable=False)
    Receipts = Column(String, nullable=True)  # comma separated
    IsConfirmed = Column(Boolean, nullable=False, default=False)
    ConfirmDate = Column(Date, nullable=True)
    ConfirmUser = Column(Integer, nullable=True)
    Type = Column(Integer, nullable=False)  # donate, affiliate
    LastUpdate = Column(Date, nullable=False)
