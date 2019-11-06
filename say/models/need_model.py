from . import *

"""
Need Model
"""


class NeedModel(base):
    __tablename__ = "need"

    id = Column(Integer, nullable=False, primary_key=True, unique=True)

    child_id = Column(Integer, ForeignKey('child.id'))

    name = Column(String, nullable=False)
    imageUrl = Column(String, nullable=False)
    category = Column(Integer, nullable=False)  # 0:Growth | 1:Joy | 2:Health | 3:Surroundings
    isUrgent = Column(Boolean, nullable=False)
    description = Column(Text, nullable=False)
    descriptionSummary = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    cost = Column(Integer, nullable=False)
    progress = Column(Integer, nullable=False, default=0)
    paid = Column(Integer, nullable=False, default=0)
    affiliateLinkUrl = Column(String, nullable=True)
    isDone = Column(Boolean, nullable=False, default=False)
    isDeleted = Column(Boolean, nullable=False, default=False)
    createdAt = Column(Date, nullable=False)
    receipts = Column(String, nullable=True)  # comma separated
    isConfirmed = Column(Boolean, nullable=False, default=False)
    confirmDate = Column(Date, nullable=True)
    confirmUser = Column(Integer, nullable=True)
    type = Column(Integer, nullable=False)  # 0:donate | 1:affiliate
    lastUpdate = Column(Date, nullable=False)
    doing_duration = Column(Integer, nullable=False, default=5)

    child = relationship('ChildModel', foreign_keys=child_id, uselist=False)
