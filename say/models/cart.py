from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy_utils import Timestamp

from ..orm import base


class Cart(base, Timestamp):
    __tablename__ = 'cart'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, unique=True)

    user = relationship(
        'User',
        foreign_keys=user_id,
        uselist=False,
    )
    needs = relationship(
        'Need',
        secondary='cart_need',
        primaryjoin='cart.id==cart_need.cart_id AND cart_need.deleted_at IS NULL',
        secondaryjoin='need.id==cart_need.need_id AND cart_need.deleted_at IS NULL',
        back_populates='carts',
    )


class CartsNeeds(base, Timestamp):
    __tablename__ = 'cart_need'

    id = Column(Integer, primary_key=True)

    cart_id = Column(Integer, ForeignKey('cart.id'), index=True, nullable=False)
    need_id = Column(Integer, ForeignKey('need.id'), index=True, nullable=False)

    amount = Column(Integer, nullable=True)  # if null, full amount will be used
    deleted = Column(DateTime, nullable=True)
