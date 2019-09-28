from say.models.child_model import ChildModel
from say.models.need_model import NeedModel

from . import *

"""
Child-Need Model
"""


class ChildNeedModel(base):
    __tablename__ = "child_need"

    id_child = Column(Integer, ForeignKey(ChildModel.id), nullable=False)
    id_need = Column(Integer, ForeignKey(NeedModel.id), nullable=False)
    id = Column(Integer, nullable=False, primary_key=True)
    isDeleted = Column(Boolean, nullable=False, default=False)

    child_relation = relationship("ChildModel", foreign_keys="ChildNeedModel.id_child")
    need_relation = relationship("NeedModel", foreign_keys="ChildNeedModel.id_need")
