from flask.globals import session
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql.functions import func
from sqlalchemy_utils import Timestamp

from ..orm import base


# if need unpayable or done, delete, unconfirmed from cart
# if cost of need changed, change cart item


class CartNeed(base, Timestamp):
    __tablename__ = 'cart_needs'

    id = Column(Integer, primary_key=True)

    cart_id = Column(Integer, ForeignKey('cart.id'), index=True, nullable=False)
    need_id = Column(Integer, ForeignKey('need.id'), index=True, nullable=False)

    name = association_proxy('need', 'name')
    title = association_proxy('need', 'title')
    cost = association_proxy('need', 'cost')
    paid = association_proxy('need', 'paid')
    amount = Column(Integer, nullable=False)
    donation = Column(Integer, default=0)
    deleted = Column(DateTime, nullable=True)

    cart = relationship(
        'Cart',
        foreign_keys=cart_id,
        uselist=False,
    )
    need = relationship(
        'Need',
        foreign_keys=need_id,
        uselist=False,
    )


class Cart(base, Timestamp):
    __tablename__ = 'cart'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, unique=True)

    need_amount = column_property(
        select([coalesce(func.sum(CartNeed.amount), 0,)]).where(
            and_(
                CartNeed.cart_id == id,
                CartNeed.deleted.is_(None),
            )
        )
    )
    donation_amount = column_property(
        select([coalesce(func.sum(CartNeed.donation), 0,)]).where(
            and_(
                CartNeed.cart_id == id,
                CartNeed.deleted.is_(None),
            )
        )
    )

    @hybrid_property
    def total_amount(self):
        return self.need_amount + self.donation_amount

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

    def delete_need(self, item):
        pass
