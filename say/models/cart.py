from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import column_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import String
from sqlalchemy_utils import Timestamp

from say.models.need_model import Need

from ..orm import base


class CartNeed(base, Timestamp):
    """Cart Needs Table
    Need will be deleted from cart when get done/delete/unconfirm
    #TODO: what happen if a need become unpayable?
    """

    __tablename__ = 'cart_needs'

    id = Column(Integer, primary_key=True)

    cart_id = Column(Integer, ForeignKey('carts.id'), index=True, nullable=False)
    need_id = Column(Integer, ForeignKey('need.id'), index=True, nullable=False)

    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    name = association_proxy('need', 'name')
    title = association_proxy('need', 'title')
    cost = association_proxy('need', 'cost')
    paid = association_proxy('need', 'paid')
    deleted = Column(DateTime, nullable=True)

    amount = column_property(select([Need.cost - Need.paid]).where(Need.id == need_id))

    cart = relationship(
        'Cart',
        foreign_keys=cart_id,
        uselist=False,
    )
    need = relationship(
        'Need',
        foreign_keys=need_id,
        uselist=False,
        back_populates='carts',
    )


class Cart(base, Timestamp):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, unique=True)

    total_amount = column_property(
        select([cast(coalesce(func.sum(CartNeed.amount), 0), Integer)]).where(
            and_(
                CartNeed.cart_id == id,
                CartNeed.deleted.is_(None),
            )
        )
    )

    cart_payments = relationship(
        'CartPayment',
        back_populates='cart',
    )
    user = relationship(
        'User',
        foreign_keys=user_id,
        uselist=False,
        back_populates='cart',
    )
    needs = relationship(
        'CartNeed',
        primaryjoin='and_(Cart.id==CartNeed.cart_id, CartNeed.deleted.is_(None))',
        back_populates='cart',
    )


class CartPayment(base, Timestamp):
    __tablename__ = 'cart_payments'

    id = Column(Integer, primary_key=True)

    cart_id = Column(Integer, ForeignKey('carts.id'), index=True)
    order_id = Column(String, unique=True)

    bank_amount = Column(Integer, default=0)
    credit_amount = Column(Integer, default=0)
    donation_amount = Column(Integer, default=0)
    needs_amount = Column(Integer, default=0)
    total_amount = Column(Integer, default=0)

    gateway_payment_id = Column(String, nullable=True, index=True)
    gateway_track_id = Column(String, nullable=True, index=True)
    link = Column(String, nullable=True)
    transaction_date = Column(DateTime, nullable=True)
    verified = Column(DateTime, nullable=True)
    card_no = Column(String, nullable=True)
    hashed_card_no = Column(String, nullable=True)

    cart = relationship(
        'Cart',
        foreign_keys=cart_id,
        uselist=False,
        back_populates='cart_payments',
    )
    payments = relationship('Payment', back_populates='cart_payment')

    def verify(
        self,
        transaction_date=datetime.utcnow(),
        track_id=None,
        verify_date=datetime.utcnow(),
        card_no=None,
        hashed_card_no=None,
    ):

        self.transaction_date = transaction_date
        self.verified = verify_date
        self.gateway_track_id = track_id
        self.hashed_card_no = hashed_card_no
        self.card_no = card_no

        for payment in self.payments:
            payment.verify(
                transaction_date=transaction_date,
                track_id=track_id,
                verify_date=verify_date,
                card_no=card_no,
                hashed_card_no=hashed_card_no,
            )
