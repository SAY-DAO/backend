from say.models.need_model import NeedModel
from say.models.user_model import UserModel
from . import *

"""
Payment Model
"""


class PaymentModel(base):
    __tablename__ = "payment"

    id = Column(Integer, nullable=False, primary_key=True)
    id_need = Column(Integer, ForeignKey(NeedModel.id), nullable=False)
    id_user = Column(Integer, ForeignKey(UserModel.id), nullable=False)

    createdAt = Column(Date, nullable=False)
    orderId = Column(String, nullable=True)
    paymentId = Column(String, nullable=True)
    link = Column(String, nullable=True)
    amount = Column(Integer, nullable=True)
    desc = Column(String, nullable=True)
    is_verified = Column(Boolean, nullable=True)
    date = Column(Date, nullable=True)
    card_no = Column(String, nullable=True)
    hashed_card_no = Column(String, nullable=True)
    track_id = Column(String, nullable=True)
    verfied_date = Column(Date, nullable=True)
    donate = Column(Integer, default=0)

    need = relationship(
        "NeedModel",
        foreign_keys="PaymentModel.id_need",
        uselist=False
    )
    user = relationship("UserModel", foreign_keys="PaymentModel.id_user")
