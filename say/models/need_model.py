from sqlalchemy.ext.hybrid import hybrid_property

from say.utils import get_price
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
    _cost = Column(Integer, nullable=False)
    progress = Column(Integer, nullable=False, default=0)
    paid = Column(Integer, nullable=False, default=0)
    donated = Column(Integer, nullable=False, default=0)
    link = Column(String, nullable=True)
    affiliateLinkUrl = Column(String, nullable=True)
    isDone = Column(Boolean, nullable=False, default=False)
    doneAt = Column(DateTime, nullable=True)
    isDeleted = Column(Boolean, nullable=False, default=False)
    createdAt = Column(DateTime, nullable=False)
    receipts = Column(String, nullable=True)  # comma separated
    isConfirmed = Column(Boolean, nullable=False, default=False)
    confirmDate = Column(DateTime, nullable=True)
    confirmUser = Column(Integer, nullable=True)
    type = Column(Integer, nullable=False)  # 0:service | 1:product
    lastUpdate = Column(DateTime, nullable=False)
    doing_duration = Column(Integer, nullable=False, default=5)
    status = Column(Integer, nullable=False, default=0)

    @hybrid_property
    def cost(self):
        if not self.link:
            return self._cost
        return get_price(self.link)

    @cost.expression
    def cost(cls):
        return

    child = relationship('ChildModel', foreign_keys=child_id, uselist=False)
