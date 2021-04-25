
from . import *

"""
User-Family Model
"""


# TODO: FamilyMember?
class UserFamily(base, Timestamp):
    __tablename__ = "user_family"

    id = Column(Integer, nullable=False, primary_key=True)

    id_user = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    id_family = Column(Integer, ForeignKey('family.id'), nullable=False, index=True)
    
    userRole = Column(Integer, nullable=False)  # 0:father | 1:mother | 2:uncle | 3:aunt
    isDeleted = Column(Boolean, nullable=False, default=False)

    family = relationship(
        'Family',
        foreign_keys=id_family,
        back_populates='members',
        uselist=False,
    )

    user = relationship(
        'User',
        foreign_keys=id_user,
        uselist=False,
        back_populates='user_families',
    )

