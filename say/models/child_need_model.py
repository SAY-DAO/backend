
from . import *


"""
Child-Need Model
"""


class ChildNeed(base, Timestamp):
    __tablename__ = "child_need"

    id_child = Column(Integer, ForeignKey('child.id'), nullable=False)
    id_need = Column(Integer, ForeignKey('need.id'), nullable=False)
    id = Column(Integer, nullable=False, primary_key=True)
    isDeleted = Column(Boolean, nullable=False, default=False)

    child = relationship("Child", foreign_keys="ChildNeed.id_child")
    need = relationship("Need", foreign_keys="ChildNeed.id_need")
