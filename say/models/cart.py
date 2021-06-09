from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import column_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql.functions import func
from sqlalchemy_utils import Timestamp

from say.models.need_model import Need

from ..orm import base


class CartNeed(base, Timestamp):
    """ Cart Needs Table
    Need will be deleted from cart when get done/delete/unconfirm
    #TODO: if need become unpayable, what happen?
    """
    __tablename__ = 'cart_needs'

    id = Column(Integer, primary_key=True)

    cart_id = Column(Integer, ForeignKey('cart.id'), index=True, nullable=False)
    need_id = Column(Integer, ForeignKey('need.id'), index=True, nullable=False)

    name = association_proxy('need', 'name')
    title = association_proxy('need', 'title')
    cost = association_proxy('need', 'cost')
    paid = association_proxy('need', 'paid')
    deleted = Column(DateTime, nullable=True)

    amount = column_property(
        select([Need.cost - Need.paid]).where(Need.id == need_id)
    )

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
    __tablename__ = 'cart'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, unique=True)

    total_amount = column_property(
        select([coalesce(func.sum(CartNeed.amount), 0,)]).where(
            and_(
                CartNeed.cart_id == id,
                CartNeed.deleted.is_(None),
            )
        )
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

    def delete_need(self, item):
        pass
