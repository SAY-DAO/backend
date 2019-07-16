from say.models.family_model import FamilyModel
from say.models.need_model import NeedModel
from say.models.user_model import UserModel
from . import *

"""
Need-Family Model
"""


class NeedFamilyModel(base):
    __tablename__ = 'need_family'

    Id = Column(Integer, nullable=False, primary_key=True)
    Id_family = Column(Integer, ForeignKey(FamilyModel.Id), nullable=False)
    Id_user = Column(Integer, ForeignKey(UserModel.Id), nullable=False)
    Id_need = Column(Integer, ForeignKey(NeedModel.Id), nullable=False)
    IsDeleted = Column(Boolean, nullable=False, default=False)

    family_relation = relationship('FamilyModel', foreign_keys='NeedFamilyModel.Id_family')
    user_relation = relationship('UserModel', foreign_keys='NeedFamilyModel.Id_user')
    need_relation = relationship('NeedModel', foreign_keys='NeedFamilyModel.Id_need')
