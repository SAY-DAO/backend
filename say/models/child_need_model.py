
from . import *

"""
Child-Need Model
"""


class ChildNeedModel(base):
    __tablename__ = "child_need"

    id_child = Column(Integer, ForeignKey('child.id'), nullable=False)
    id_need = Column(Integer, ForeignKey('need.id'), nullable=False)
    id = Column(Integer, nullable=False, primary_key=True)
    isDeleted = Column(Boolean, nullable=False, default=False)

    child = relationship("ChildModel", foreign_keys="ChildNeedModel.id_child")
    need = relationship("NeedModel", foreign_keys="ChildNeedModel.id_need")
