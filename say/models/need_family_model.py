from khayyam import JalaliDate

from . import *

"""
Need-Family Model
"""


# TODO: ParticipantModel?
class NeedFamilyModel(base):
    __tablename__ = "need_family"

    id = Column(Integer, nullable=False, primary_key=True)
    id_family = Column(Integer, ForeignKey('family.id'), nullable=False)
    id_user = Column(Integer, ForeignKey('user.id'), nullable=False)
    id_need = Column(Integer, ForeignKey('need.id'), nullable=False)
    isDeleted = Column(Boolean, nullable=False, default=False)

    family = relationship(
        "FamilyModel",
        foreign_keys="NeedFamilyModel.id_family",
    )
    user = relationship(
        'UserModel',
        foreign_keys=id_user,
    )
    need = relationship(
        "NeedModel",
        foreign_keys=id_need,
        back_populates='need_family',
    )
