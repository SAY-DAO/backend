
from . import *

"""
User-Family Model
"""


# TODO: FamilyMemberModel?
class UserFamilyModel(base):
    __tablename__ = "user_family"

    id = Column(Integer, nullable=False, primary_key=True)
    id_user = Column(Integer, ForeignKey('user.id'), nullable=False)
    id_family = Column(Integer, ForeignKey('family.id'), nullable=False)
    userRole = Column(Integer, nullable=False)  # 0:father | 1:mother | 2:uncle | 3:aunt
    isDeleted = Column(Boolean, nullable=False, default=False)

    family = relationship(
        'FamilyModel',
        foreign_keys=id_family,
        back_populates='members',
        uselist=False,
    )

    user = relationship(
        'UserModel',
        foreign_keys=id_user,
        uselist=False,
    )

