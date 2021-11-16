from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import column_property

from . import *
from .payment_model import Payment


"""
Need-Family Model
"""


# TODO: Participant?
class NeedFamily(base, Timestamp):
    __tablename__ = "need_family"

    id = Column(Integer, nullable=False, primary_key=True)
    id_family = Column(Integer, ForeignKey('family.id'), nullable=True, index=True)
    id_user = Column(Integer, ForeignKey('user.id'), nullable=True, index=True)
    id_need = Column(Integer, ForeignKey('need.id'), nullable=False, index=True)
    isDeleted = Column(Boolean, nullable=False, default=False, index=True)
    type = Column(Text, nullable=False)
    user_role = Column(Integer, nullable=True)
    user_avatar = association_proxy('user', 'avatarUrl')
    username = association_proxy('user', 'userName')

    paid = column_property(
        select([coalesce(func.sum(Payment.need_amount), 0,)]).where(
            and_(
                Payment.verified.isnot(None),
                Payment.id_user == id_user,
                Payment.id_need == id_need,
            )
        )
    )

    family = relationship(
        "Family",
        foreign_keys="NeedFamily.id_family",
        uselist=False,
    )
    user = relationship(
        'User',
        foreign_keys=id_user,
        back_populates='participations',
        uselist=False,
    )
    need = relationship(
        "Need",
        foreign_keys=id_need,
        back_populates='participants',
        uselist=False,
    )

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'app',
    }
