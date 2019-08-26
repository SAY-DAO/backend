from say.models.family_model import FamilyModel
from say.models.need_model import NeedModel
from say.models.user_model import UserModel
from . import *

"""
Need-Family Model
"""


class NeedFamilyModel(base):
    __tablename__ = 'need_family'

    id = Column(Integer, nullable=False, primary_key=True)
    id_family = Column(Integer, ForeignKey(FamilyModel.id), nullable=False)
    id_user = Column(Integer, ForeignKey(UserModel.id), nullable=False)
    id_need = Column(Integer, ForeignKey(NeedModel.id), nullable=False)
    isDeleted = Column(Boolean, nullable=False, default=False)

    family_relation = relationship('FamilyModel', foreign_keys='NeedFamilyModel.id_family')
    user_relation = relationship('UserModel', foreign_keys='NeedFamilyModel.id_user')
    need_relation = relationship('NeedModel', foreign_keys='NeedFamilyModel.id_need')
