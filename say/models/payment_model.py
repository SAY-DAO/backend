
from . import *

"""
Payment Model
"""


class PaymentModel(base):
    __tablename__ = "payment"

    id = Column(Integer, nullable=False, primary_key=True)
    id_need = Column(Integer, ForeignKey('need.id'), nullable=False)
    id_user = Column(Integer, ForeignKey('user.id'), nullable=False)

    createdAt = Column(DateTime, nullable=False)
    orderId = Column(String, nullable=True)
    paymentId = Column(String, nullable=True)
    link = Column(String, nullable=True)
    amount = Column(Integer, nullable=True)
    desc = Column(String, nullable=True)
    is_verified = Column(Boolean, nullable=True)
    date = Column(DateTime, nullable=True)
    card_no = Column(String, nullable=True)
    hashed_card_no = Column(String, nullable=True)
    track_id = Column(String, nullable=True)
    verfied_date = Column(DateTime, nullable=True)
    donate = Column(Integer, default=0)

    need = relationship(
        "NeedModel",
        foreign_keys=id_need,
        uselist=False,
        back_populates='payments',
    )
    user = relationship(
        "UserModel",
        foreign_keys=id_user,
        back_populates='payments',
        uselist=False,
    )
