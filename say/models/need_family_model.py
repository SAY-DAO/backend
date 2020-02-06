from khayyam import JalaliDate

from . import *

"""
Need-Family Model
"""


# TODO: Participant?
class NeedFamily(base, Timestamp):
    __tablename__ = "need_family"

    id = Column(Integer, nullable=False, primary_key=True)
    id_family = Column(Integer, ForeignKey('family.id'), nullable=True)
    id_user = Column(Integer, ForeignKey('user.id'), nullable=False)
    id_need = Column(Integer, ForeignKey('need.id'), nullable=False)
    isDeleted = Column(Boolean, nullable=False, default=False)
    user_fullname = Column(Text, nullable=False)
    user_avatar = Column(Text, nullable=False)

    @aggregated('need.payments', Column(Integer, default=0, nullable=False))
    def paid(cls):
        from . import Payment
        return func.sum(Payment.need_amount) \
            .filter(Payment.id_user==cls.id_user) \

    @observes('user.avatarUrl')
    def user_avatar_observer(self, avatar):
        self.user_avatar = avatar

    @observes('user.firstName', 'user.lastName')
    def user_fullname_observer(self, firstname, lastname):
        self.user_fullname = f'{firstname} {lastname}'

    family = relationship(
        "Family",
        foreign_keys="NeedFamily.id_family",
        lazy='selectin',
    )
    user = relationship(
        'User',
        foreign_keys=id_user,
        back_populates='participations',
        lazy='selectin',
    )
    need = relationship(
        "Need",
        foreign_keys=id_need,
        back_populates='participants',
        lazy='selectin',
    )
