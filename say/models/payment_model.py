from uuid import uuid4

from sqlalchemy.ext.hybrid import hybrid_property

from . import *
from .user_family_model import UserFamily


"""
Payment Model
"""

def create_order_id():
    return uuid4().hex


class Payment(base, Timestamp):
    __tablename__ = "payment"

    id = Column(Integer, nullable=False, primary_key=True)
    id_need = Column(Integer, ForeignKey('need.id'), nullable=True)
    id_user = Column(Integer, ForeignKey('user.id'), nullable=False)

    gateway_payment_id = Column(String, nullable=True)
    gateway_track_id = Column(String, nullable=True)
    link = Column(String, nullable=True)

    order_id = Column(String, nullable=True, default=create_order_id)
    desc = Column(String, nullable=True)
    card_no = Column(String, nullable=True)
    hashed_card_no = Column(String, nullable=True)
    transaction_date = Column(DateTime, nullable=True)
    verified = Column(DateTime, nullable=True)
    use_credit = Column(Boolean, default=False, nullable=False)

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
        "Need",
        foreign_keys=id_need,
        uselist=False,
        back_populates='payments',
        primaryjoin=
            'and_(Need.id==Payment.id_need, Payment.verified.isnot(None))',
    )

    user = relationship(
        "User",
        foreign_keys=id_user,
        back_populates='payments',
        uselist=False,
    )

    def verify(self, transaction_date=datetime.utcnow(), track_id=None,
               verify_date=datetime.utcnow(), card_no=None,
               hashed_card_no=None):

        session = object_session(self)

        self.transaction_date = transaction_date
        self.gateway_track_id = track_id or self.order_id
        self.verified = verify_date
        self.card_no = card_no
        self.hashed_card_no = hashed_card_no

        session.flush()

        if self.id_need is None:
            return

        family = self.need.child.family

        participant = (
            session.query(NeedFamily)
            .filter_by(id_need=self.id_need)
            .filter_by(id_user=self.id_user)
            .filter(NeedFamily.user_role != -1)
            .filter_by(isDeleted=False)
            .with_for_update()
            .first()
        )

        if participant is None:
            user_role = session.query(UserFamily.userRole) \
                .filter(UserFamily.id_user==self.user.id) \
                .filter(UserFamily.id_family==family.id) \
                .one_or_none()

            if user_role:
                user_role, = user_role

            new_participant = NeedFamily(
                id_family=family.id,
                user=self.user,
                need=self.need,
                user_role=user_role
            )
            session.add(new_participant)

