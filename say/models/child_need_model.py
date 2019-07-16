from say.models.child_model import ChildModel
from say.models.need_model import NeedModel

from . import *

"""
Child-Need Model
"""


class ChildNeedModel(base):
    __tablename__ = 'child_need'

    Id_child = Column(Integer, ForeignKey(ChildModel.Id), nullable=False)
    Id_need = Column(Integer, ForeignKey(NeedModel.Id), nullable=False)
    Id = Column(Integer, nullable=False, primary_key=True)
    IsDeleted = Column(Boolean, nullable=False, default=False)

    child_relation = relationship('ChildModel', foreign_keys='ChildNeedModel.Id_child')
    need_relation = relationship('NeedModel', foreign_keys='ChildNeedModel.Id_need')
