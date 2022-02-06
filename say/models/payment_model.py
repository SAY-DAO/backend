from uuid import uuid4

from sqlalchemy.ext.hybrid import hybrid_property

from say.constants import SAY_ROLE

from . import *
from .user_family_model import UserFamily


'''
Payment Model
'''


def create_order_id():
    return uuid4().hex


class Payment(base, Timestamp):
    __tablename__ = 'payment'

    id = Column(Integer, nullable=False, primary_key=True)
    id_need = Column(Integer, ForeignKey('need.id'), nullable=True, index=True)
    id_user = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    cart_payment_id = Column(
        Integer, ForeignKey('cart_payments.id'), nullable=True, index=True
    )

    gateway_payment_id = Column(String, nullable=True, index=True)
    gateway_track_id = Column(String, nullable=True, index=True)
    link = Column(String, nullable=True)

    order_id = Column(String, nullable=True, unique=False, index=True)
    desc = Column(String, nullable=True)
    card_no = Column(String, nullable=True)
    hashed_card_no = Column(String, nullable=True)
    transaction_date = Column(DateTime, nullable=True)
    verified = Column(DateTime, nullable=True, index=True)
    is_nakama = Column(Boolean, default=False, nullable=False)

    need_amount = Column(Integer, default=0)
    credit_amount = Column(Integer, default=0)
    donation_amount = Column(Integer, default=0)

    @hybrid_property
    def bank_amount(self):
        return self.need_amount + self.donation_amount - self.credit_amount

    @hybrid_property
    def total_amount(self):
        return self.need_amount + self.donation_amount

    need = relationship(
        'Need',
        foreign_keys=id_need,
        uselist=False,
        back_populates='payments',
    )

    user = relationship(
        'User',
        foreign_keys=id_user,
        back_populates='payments',
        uselist=False,
    )
    cart_payment = relationship(
        'CartPayment',
        foreign_keys=cart_payment_id,
        back_populates='payments',
    )

    def verify(
        self,
        transaction_date=None,
        track_id=None,
        verify_date=None,
        card_no=None,
        hashed_card_no=None,
        is_say=False,
    ):

        from .need_family_model import NeedFamily

        session = object_session(self)

        self.transaction_date = transaction_date or datetime.utcnow()
        self.gateway_track_id = track_id or self.order_id
        self.verified = verify_date or datetime.utcnow()
        self.card_no = card_no
        self.hashed_card_no = hashed_card_no

        # To update need.paid
        session.flush()
        session.expire_all()

        if self.id_need is None:
            return

        session.expire(self.need)

        if self.need.paid >= self.need.cost:
            if not self.need.isDone:
                self.need.done()
        else:
            self.need.status = 1

        family = self.need.child.family

        participant = (
            session.query(NeedFamily)
            .filter_by(id_need=self.id_need)
            .filter_by(id_user=self.id_user)
            .with_for_update()
            .one_or_none()
        )

        if participant is None:
            user_family = (
                session.query(UserFamily)
                .filter(UserFamily.id_user == self.user.id)
                .filter(UserFamily.id_family == family.id)
                .filter(UserFamily.isDeleted.is_(False))
                .one_or_none()
            )

            if user_family:
                user_family.is_participated = True
                user_role = user_family.role
            elif is_say:
                user_role = SAY_ROLE
            else:
                raise Exception('User not in family')

            new_participant = NeedFamily(
                id_family=family.id,
                user=self.user,
                need=self.need,
                user_role=user_role,
            )
            session.add(new_participant)
