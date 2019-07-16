from say.models.family_model import FamilyModel
from say.models.user_model import UserModel
from . import *

"""
User-Family Model
"""


class UserFamilyModel(base):
    __tablename__ = 'user_family'

    Id = Column(Integer, nullable=False, primary_key=True)
    Id_user = Column(Integer, ForeignKey(UserModel.Id), nullable=False)
    Id_family = Column(Integer, ForeignKey(FamilyModel.Id), nullable=False)
    UserRole = Column(Integer, nullable=False)
    IsDeleted = Column(Boolean, nullable=False, default=False)

    family_relation = relationship('FamilyModel', foreign_keys='UserFamilyModel.Id_family')
    user_relation = relationship('UserModel', foreign_keys='UserFamilyModel.Id_user')
