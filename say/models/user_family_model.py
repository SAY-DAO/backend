from say.models.family_model import FamilyModel
from say.models.user_model import UserModel
from . import *

"""
User-Family Model
"""


class UserFamilyModel(base):
    __tablename__ = "user_family"

    id = Column(Integer, nullable=False, primary_key=True)
    id_user = Column(Integer, ForeignKey(UserModel.id), nullable=False)
    id_family = Column(Integer, ForeignKey(FamilyModel.id), nullable=False)
    userRole = Column(Integer, nullable=False)  # 0:father | 1:mother | 2:uncle | 3:aunt
    isDeleted = Column(Boolean, nullable=False, default=False)

    family = relationship(
        "FamilyModel",
        foreign_keys="UserFamilyModel.id_family",
        uselist=False,
    )
    user = relationship(
        "UserModel",
        foreign_keys="UserFamilyModel.id_user",
        uselist=False,
    )
